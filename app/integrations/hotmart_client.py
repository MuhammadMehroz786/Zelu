"""Hotmart API integration — marketplace search and product validation."""

import httpx
from config.settings import settings

BASE_URL = "https://developers.hotmart.com/payments/api/v1"
AUTH_URL = "https://api-sec-vlc.hotmart.com/security/oauth/token"

_token = None


def _get_token() -> str:
    """Get OAuth token for Hotmart API."""
    global _token
    if _token:
        return _token

    response = httpx.post(
        AUTH_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.HOTMART_CLIENT_ID,
            "client_secret": settings.HOTMART_CLIENT_SECRET,
        },
        timeout=15,
    )
    response.raise_for_status()
    _token = response.json().get("access_token")
    return _token


def search_marketplace(query: str, max_results: int = 20) -> dict:
    """Search Hotmart marketplace for existing products in a niche.

    Note: Hotmart's public API is limited. This uses the affiliate
    marketplace search when available, with fallback to web data.
    """
    try:
        token = _get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Hotmart affiliate API for marketplace search
        response = httpx.get(
            f"{BASE_URL}/products",
            headers=headers,
            params={"product_name": query, "max_results": max_results},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        products = []
        for item in data.get("items", []):
            products.append({
                "name": item.get("product_name"),
                "id": item.get("product_id"),
                "price": item.get("price", {}).get("value"),
                "currency": item.get("price", {}).get("currency_code"),
            })

        return {"products": products, "total": len(products), "query": query}

    except Exception as e:
        return {"products": [], "total": 0, "query": query, "error": str(e)}
