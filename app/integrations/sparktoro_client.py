"""SparkToro API integration — audience intelligence."""

import httpx
from config.settings import settings

BASE_URL = "https://api.sparktoro.com/v1"


def get_audience_data(query: str) -> dict:
    """Get audience intelligence from SparkToro.

    Note: SparkToro API requires contacting sales for access.
    This is a placeholder that will be activated once API access is granted.
    """
    if not settings.SPARKTORO_API_KEY:
        return {
            "status": "api_key_not_configured",
            "message": "SparkToro API key not set. Contact SparkToro sales for API access.",
        }

    try:
        response = httpx.get(
            f"{BASE_URL}/audience",
            headers={"Authorization": f"Bearer {settings.SPARKTORO_API_KEY}"},
            params={"q": query},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
