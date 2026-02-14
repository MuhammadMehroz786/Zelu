"""GoHighLevel API integration — CRM, workflows, email automation."""

import httpx
from config.settings import settings

BASE_URL = "https://services.leadconnectorhq.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }


def create_contact(email: str, name: str, tags: list = None) -> dict:
    """Create a contact in GoHighLevel."""
    payload = {
        "email": email,
        "name": name,
        "locationId": settings.GHL_LOCATION_ID,
    }
    if tags:
        payload["tags"] = tags

    response = httpx.post(
        f"{BASE_URL}/contacts/",
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def add_tag(contact_id: str, tags: list) -> dict:
    """Add tags to a contact."""
    response = httpx.post(
        f"{BASE_URL}/contacts/{contact_id}/tags",
        headers=_headers(),
        json={"tags": tags},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def create_workflow(product_name: str, email_sequence: dict) -> dict:
    """Create a workflow for email automation.

    Note: GHL workflow creation via API is limited.
    This sets up the basic structure — detailed workflow steps
    may need manual configuration in GHL dashboard.
    """
    try:
        # Create a pipeline for tracking
        pipeline_response = httpx.post(
            f"{BASE_URL}/opportunities/pipelines",
            headers=_headers(),
            json={
                "name": f"ZEULE - {product_name}",
                "locationId": settings.GHL_LOCATION_ID,
                "stages": [
                    {"name": "Lead", "position": 0},
                    {"name": "Customer", "position": 1},
                    {"name": "Upsell", "position": 2},
                ],
            },
            timeout=15,
        )
        pipeline_response.raise_for_status()

        return {
            "pipeline": pipeline_response.json(),
            "status": "created",
            "note": "Email workflow steps should be configured in GHL dashboard using the generated copy.",
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


def list_funnels() -> dict:
    """List existing funnels in GHL."""
    try:
        response = httpx.get(
            f"{BASE_URL}/funnels/",
            headers=_headers(),
            params={"locationId": settings.GHL_LOCATION_ID},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
