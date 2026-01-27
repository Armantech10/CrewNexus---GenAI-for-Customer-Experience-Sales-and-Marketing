"""
Payments Router
API endpoints for Stripe payment processing.
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.tools.stripe_payments import stripe_payments

router = APIRouter()


class PaymentIntentRequest(BaseModel):
    amount: int  # Amount in cents
    currency: str = "usd"
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CheckoutItemPrice(BaseModel):
    unit_amount: int  # Price in cents
    currency: str = "usd"
    product_data: Dict[str, str]


class CheckoutItem(BaseModel):
    price_data: CheckoutItemPrice
    quantity: int = 1


class CheckoutSessionRequest(BaseModel):
    items: List[CheckoutItem]
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None
    mode: str = "payment"


class RefundRequest(BaseModel):
    payment_intent_id: str
    amount: Optional[int] = None  # None = full refund
    reason: Optional[str] = None


class CreateCustomerRequest(BaseModel):
    email: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/mode")
async def get_payment_mode():
    """Check if payments are in mock or live mode"""
    return {
        "mock_mode": stripe_payments.is_mock,
        "message": "Mock mode - no real charges" if stripe_payments.is_mock else "Live mode"
    }


@router.post("/create-intent")
async def create_payment_intent(request: PaymentIntentRequest):
    """
    Create a payment intent for processing a payment.
    Returns a client_secret for use with Stripe.js on the frontend.
    """
    try:
        intent = await stripe_payments.create_payment_intent(
            amount=request.amount,
            currency=request.currency,
            customer_id=request.customer_id,
            metadata=request.metadata
        )
        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": intent.status,
            "mock": stripe_payments.is_mock
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-checkout")
async def create_checkout_session(request: CheckoutSessionRequest):
    """
    Create a Stripe Checkout session.
    Returns a URL to redirect the customer to.
    """
    try:
        line_items = [
            {
                "price_data": {
                    "unit_amount": item.price_data.unit_amount,
                    "currency": item.price_data.currency,
                    "product_data": item.price_data.product_data
                },
                "quantity": item.quantity
            }
            for item in request.items
        ]
        
        session = await stripe_payments.create_checkout_session(
            line_items=line_items,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_email=request.customer_email,
            mode=request.mode
        )
        return {
            "id": session.id,
            "url": session.url,
            "amount_total": session.amount_total,
            "status": session.status,
            "mock": stripe_payments.is_mock
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_intent_id}/status")
async def get_payment_status(payment_intent_id: str):
    """Get the current status of a payment intent"""
    try:
        intent = await stripe_payments.get_payment_status(payment_intent_id)
        return {
            "id": intent.id,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": intent.status,
            "mock": stripe_payments.is_mock
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refund")
async def process_refund(request: RefundRequest):
    """Process a refund for a payment"""
    try:
        refund = await stripe_payments.process_refund(
            payment_intent_id=request.payment_intent_id,
            amount=request.amount,
            reason=request.reason
        )
        return {
            "id": refund.id,
            "payment_intent_id": refund.payment_intent_id,
            "amount": refund.amount,
            "status": refund.status,
            "mock": stripe_payments.is_mock
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/customers")
async def create_customer(request: CreateCustomerRequest):
    """Create a Stripe customer for recurring payments"""
    try:
        customer = await stripe_payments.create_customer(
            email=request.email,
            name=request.name,
            metadata=request.metadata
        )
        return {**customer, "mock": stripe_payments.is_mock}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe webhook events.
    Configure webhook URL in Stripe Dashboard.
    """
    try:
        payload = await request.body()
        event = stripe_payments.handle_webhook(
            payload=payload,
            signature=stripe_signature or ""
        )
        
        # Handle specific events
        event_type = event.get("type", "")
        
        if event_type == "payment_intent.succeeded":
            # Payment successful - update order status, send confirmation, etc.
            pass
        elif event_type == "payment_intent.payment_failed":
            # Payment failed - notify customer, retry logic, etc.
            pass
        elif event_type == "checkout.session.completed":
            # Checkout completed - fulfill order
            pass
        
        return {"received": True, "type": event_type, "mock": event.get("mock", False)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
