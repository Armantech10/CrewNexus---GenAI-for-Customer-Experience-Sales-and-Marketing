"""
CRM Tool - Customer relationship management integration.

Provides customer lookup, lead management, and payment link generation.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import uuid4


class Customer(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lifetime_value: float = 0.0
    engagement_score: int = 5
    created_at: datetime
    tags: List[str] = []
    notes: Optional[str] = None


class Lead(BaseModel):
    id: str
    name: str
    email: str
    source: str
    status: str = "new"  # new, contacted, qualified, converted, lost
    created_at: datetime


# In-memory store for demo (replace with database/Stripe in production)
_customers: Dict[str, Customer] = {
    "cust_001": Customer(
        id="cust_001",
        name="Alice Johnson",
        email="alice@example.com",
        company="TechCorp",
        lifetime_value=15000.0,
        engagement_score=8,
        created_at=datetime.now(),
        tags=["enterprise", "high-value"]
    ),
    "cust_002": Customer(
        id="cust_002", 
        name="Bob Smith",
        email="bob@startup.io",
        company="Startup.io",
        lifetime_value=2500.0,
        engagement_score=6,
        created_at=datetime.now(),
        tags=["startup"]
    )
}

_leads: Dict[str, Lead] = {}


class CRMTool:
    """CRM integration tool for agents."""
    
    async def lookup_customer(
        self,
        customer_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[Customer]:
        """Look up a customer by ID or email."""
        if customer_id and customer_id in _customers:
            return _customers[customer_id]
        
        if email:
            for customer in _customers.values():
                if customer.email == email:
                    return customer
        
        return None
    
    async def get_customer_context(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive customer context for agent processing."""
        customer = await self.lookup_customer(customer_id=user_id)
        
        if not customer:
            return {
                "is_known_customer": False,
                "customer_value": "unknown",
                "engagement": 5
            }
        
        return {
            "is_known_customer": True,
            "customer_id": customer.id,
            "customer_name": customer.name,
            "company": customer.company,
            "customer_value": "high" if customer.lifetime_value > 10000 else "medium" if customer.lifetime_value > 1000 else "low",
            "lifetime_value": customer.lifetime_value,
            "engagement": customer.engagement_score,
            "tags": customer.tags
        }
    
    async def create_lead(
        self,
        name: str,
        email: str,
        source: str = "chat"
    ) -> Lead:
        """Create a new lead from conversation."""
        lead_id = f"lead_{uuid4().hex[:8]}"
        lead = Lead(
            id=lead_id,
            name=name,
            email=email,
            source=source,
            created_at=datetime.now()
        )
        _leads[lead_id] = lead
        return lead
    
    async def update_lead_status(
        self,
        lead_id: str,
        status: str
    ) -> Optional[Lead]:
        """Update lead status."""
        if lead_id in _leads:
            _leads[lead_id].status = status
            return _leads[lead_id]
        return None
    
    async def generate_payment_link(
        self,
        amount: float,
        product_name: str,
        customer_email: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a payment link.
        
        In production, this would integrate with Stripe:
        - stripe.checkout.Session.create(...)
        """
        # Mock implementation - in production use Stripe
        payment_id = f"pay_{uuid4().hex[:12]}"
        mock_url = f"https://checkout.example.com/pay/{payment_id}"
        
        return {
            "payment_id": payment_id,
            "checkout_url": mock_url,
            "amount": f"${amount:.2f}",
            "product": product_name,
            "status": "pending",
            "note": "Mock payment link - integrate with Stripe for production"
        }
    
    async def list_customers(
        self,
        tag: Optional[str] = None,
        min_value: Optional[float] = None
    ) -> List[Customer]:
        """List customers with optional filtering."""
        customers = list(_customers.values())
        
        if tag:
            customers = [c for c in customers if tag in c.tags]
        if min_value:
            customers = [c for c in customers if c.lifetime_value >= min_value]
        
        return customers


# Singleton instance
crm_tool = CRMTool()
