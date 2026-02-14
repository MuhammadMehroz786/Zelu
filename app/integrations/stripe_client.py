"""Stripe API integration — products, prices, and checkout."""

import stripe
from config.settings import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_product_with_price(name: str, price_cents: int, currency: str = "usd") -> dict:
    """Create a Stripe product with a price."""
    product = stripe.Product.create(
        name=name,
        metadata={"source": "zeule"},
    )

    price = stripe.Price.create(
        product=product.id,
        unit_amount=price_cents,
        currency=currency,
    )

    return {
        "product_id": product.id,
        "price_id": price.id,
        "amount": price_cents,
        "currency": currency,
    }


def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    """Create a Stripe Checkout session."""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return {
        "session_id": session.id,
        "checkout_url": session.url,
    }
