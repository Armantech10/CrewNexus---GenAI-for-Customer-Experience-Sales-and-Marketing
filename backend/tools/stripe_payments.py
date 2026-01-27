"""
Stripe Payments Tool
Handles payment processing with Stripe API.
Falls back to mock mode when STRIPE_SECRET_KEY is not set.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import uuid

# Try to import Stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

from backend.config.settings import settings


class PaymentIntent(BaseModel):
    """Payment intent model"""
    id: str
    amount: int
    currency: str
    status: str
    client_secret: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.now()


class CheckoutSession(BaseModel):
    """Checkout session model"""
    id: str
    url: str
    status: str
    amount_total: int
    currency: str
    customer_email: Optional[str] = None
    payment_status: str = "unpaid"
    created_at: datetime = datetime.now()


class RefundResult(BaseModel):
    """Refund result model"""
    id: str
    payment_intent_id: str
    amount: int
    status: str
    reason: Optional[str] = None


class StripePayments:
    """
    Stripe payments integration tool.
    Provides mock fallback when API key is not configured.
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        self.mock_mode = not self.api_key or not STRIPE_AVAILABLE
        
        if not self.mock_mode:
            stripe.api_key = self.api_key
        
        # Mock storage
        self._mock_intents: Dict[str, PaymentIntent] = {}
        self._mock_sessions: Dict[str, CheckoutSession] = {}
        self._mock_refunds: Dict[str, RefundResult] = {}
    
    @property
    def is_mock(self) -> bool:
        return self.mock_mode
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """
        Create a payment intent for processing payments.
        
        Args:
            amount: Amount in cents (e.g., 1000 = $10.00)
            currency: Three-letter ISO currency code
            customer_id: Optional Stripe customer ID
            metadata: Optional metadata to attach
        
        Returns:
            PaymentIntent with client_secret for frontend
        """
        if self.mock_mode:
            intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
            client_secret = f"{intent_id}_secret_{uuid.uuid4().hex[:24]}"
            
            intent = PaymentIntent(
                id=intent_id,
                amount=amount,
                currency=currency,
                status="requires_payment_method",
                client_secret=client_secret,
                customer_id=customer_id,
                metadata=metadata or {}
            )
            self._mock_intents[intent_id] = intent
            return intent
        
        # Real Stripe API
        intent_data = {
            "amount": amount,
            "currency": currency,
            "automatic_payment_methods": {"enabled": True},
        }
        if customer_id:
            intent_data["customer"] = customer_id
        if metadata:
            intent_data["metadata"] = metadata
            
        stripe_intent = stripe.PaymentIntent.create(**intent_data)
        
        return PaymentIntent(
            id=stripe_intent.id,
            amount=stripe_intent.amount,
            currency=stripe_intent.currency,
            status=stripe_intent.status,
            client_secret=stripe_intent.client_secret,
            customer_id=stripe_intent.customer,
            metadata=dict(stripe_intent.metadata) if stripe_intent.metadata else {}
        )
    
    async def create_checkout_session(
        self,
        line_items: List[Dict[str, Any]],
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        mode: str = "payment"
    ) -> CheckoutSession:
        """
        Create a Stripe Checkout session for hosted payment.
        
        Args:
            line_items: List of items with price_data or price
            success_url: Redirect URL after success
            cancel_url: Redirect URL if cancelled
            customer_email: Pre-fill customer email
            mode: 'payment', 'subscription', or 'setup'
        
        Returns:
            CheckoutSession with URL to redirect customer
        """
        if self.mock_mode:
            session_id = f"cs_mock_{uuid.uuid4().hex[:16]}"
            total = sum(
                item.get("price_data", {}).get("unit_amount", 0) * item.get("quantity", 1)
                for item in line_items
            )
            
            session = CheckoutSession(
                id=session_id,
                url=f"https://checkout.stripe.com/mock/{session_id}",
                status="open",
                amount_total=total,
                currency="usd",
                customer_email=customer_email
            )
            self._mock_sessions[session_id] = session
            return session
        
        # Real Stripe API
        session_data = {
            "line_items": line_items,
            "mode": mode,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        if customer_email:
            session_data["customer_email"] = customer_email
            
        stripe_session = stripe.checkout.Session.create(**session_data)
        
        return CheckoutSession(
            id=stripe_session.id,
            url=stripe_session.url,
            status=stripe_session.status,
            amount_total=stripe_session.amount_total or 0,
            currency=stripe_session.currency or "usd",
            customer_email=stripe_session.customer_email,
            payment_status=stripe_session.payment_status
        )
    
    async def get_payment_status(self, payment_intent_id: str) -> PaymentIntent:
        """
        Get the current status of a payment intent.
        
        Args:
            payment_intent_id: The payment intent ID
        
        Returns:
            Updated PaymentIntent
        """
        if self.mock_mode:
            if payment_intent_id in self._mock_intents:
                return self._mock_intents[payment_intent_id]
            # Return a mock "not found" response
            return PaymentIntent(
                id=payment_intent_id,
                amount=0,
                currency="usd",
                status="not_found"
            )
        
        stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return PaymentIntent(
            id=stripe_intent.id,
            amount=stripe_intent.amount,
            currency=stripe_intent.currency,
            status=stripe_intent.status,
            customer_id=stripe_intent.customer,
            metadata=dict(stripe_intent.metadata) if stripe_intent.metadata else {}
        )
    
    async def process_refund(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None
    ) -> RefundResult:
        """
        Process a refund for a payment.
        
        Args:
            payment_intent_id: The payment intent to refund
            amount: Amount to refund in cents (None = full refund)
            reason: Reason for the refund
        
        Returns:
            RefundResult with status
        """
        if self.mock_mode:
            refund_id = f"re_mock_{uuid.uuid4().hex[:16]}"
            refund_amount = amount or self._mock_intents.get(
                payment_intent_id, PaymentIntent(id="", amount=0, currency="usd", status="")
            ).amount
            
            refund = RefundResult(
                id=refund_id,
                payment_intent_id=payment_intent_id,
                amount=refund_amount,
                status="succeeded",
                reason=reason
            )
            self._mock_refunds[refund_id] = refund
            return refund
        
        refund_data = {"payment_intent": payment_intent_id}
        if amount:
            refund_data["amount"] = amount
        if reason:
            refund_data["reason"] = reason
            
        stripe_refund = stripe.Refund.create(**refund_data)
        
        return RefundResult(
            id=stripe_refund.id,
            payment_intent_id=payment_intent_id,
            amount=stripe_refund.amount,
            status=stripe_refund.status,
            reason=stripe_refund.reason
        )
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer for recurring payments.
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
        
        Returns:
            Customer object with ID
        """
        if self.mock_mode:
            return {
                "id": f"cus_mock_{uuid.uuid4().hex[:14]}",
                "email": email,
                "name": name,
                "metadata": metadata or {},
                "created": int(datetime.now().timestamp())
            }
        
        customer_data = {"email": email}
        if name:
            customer_data["name"] = name
        if metadata:
            customer_data["metadata"] = metadata
            
        customer = stripe.Customer.create(**customer_data)
        
        return {
            "id": customer.id,
            "email": customer.email,
            "name": customer.name,
            "metadata": dict(customer.metadata) if customer.metadata else {},
            "created": customer.created
        }
    
    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header
        
        Returns:
            Parsed event data
        """
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if self.mock_mode or not webhook_secret:
            # Mock webhook handling
            import json
            try:
                event = json.loads(payload)
                return {
                    "type": event.get("type", "unknown"),
                    "data": event.get("data", {}),
                    "mock": True
                }
            except:
                return {"type": "invalid", "data": {}, "mock": True}
        
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
        
        return {
            "type": event.type,
            "data": event.data.object,
            "mock": False
        }


# Singleton instance
stripe_payments = StripePayments()
