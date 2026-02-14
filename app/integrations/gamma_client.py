"""Gamma API integration — document/ebook formatting and PDF generation."""

import httpx
from config.settings import settings

BASE_URL = "https://api.gamma.app/v1"


def create_document(
    title: str,
    content: str,
    output_format: str = "pdf",
    theme: str = "professional",
) -> dict:
    """Create a formatted document/PDF using Gamma.

    Note: Gamma's API is relatively new and may have limitations.
    This will be updated as their API evolves.
    """
    if not settings.GAMMA_API_KEY:
        return {
            "status": "api_key_not_configured",
            "message": "Gamma API key not set.",
        }

    try:
        response = httpx.post(
            f"{BASE_URL}/generate",
            headers={
                "Authorization": f"Bearer {settings.GAMMA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "title": title,
                "content": content,
                "format": output_format,
                "theme": theme,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "url": data.get("url"),
            "document_id": data.get("id"),
            "status": "completed",
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
