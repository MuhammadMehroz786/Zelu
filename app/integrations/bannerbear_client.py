"""Bannerbear API integration — branded template-based image generation."""

import time
import httpx
from config.settings import settings

BASE_URL = "https://api.bannerbear.com/v2"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.BANNERBEAR_API_KEY}"}


def generate_image(template_id: str, modifications: dict, timeout_seconds: int = 60) -> dict:
    """Generate an image using a Bannerbear template.

    Args:
        template_id: The Bannerbear template UID.
        modifications: Dict of layer modifications (text, images).
        timeout_seconds: Max time to wait for image generation.
    """
    if not template_id:
        return {"error": "No template_id provided. Set up Bannerbear templates first."}

    # Build modifications list for Bannerbear API
    mods = []
    for layer_name, value in modifications.items():
        if value is None:
            continue
        if isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
            mods.append({"name": layer_name, "image_url": value})
        else:
            mods.append({"name": layer_name, "text": str(value)})

    # Create the image
    response = httpx.post(
        f"{BASE_URL}/images",
        headers=_headers(),
        json={
            "template": template_id,
            "modifications": mods,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    # Poll for completion
    image_uid = data.get("uid")
    if not image_uid:
        return data

    elapsed = 0
    while elapsed < timeout_seconds:
        check = httpx.get(f"{BASE_URL}/images/{image_uid}", headers=_headers(), timeout=15)
        check.raise_for_status()
        result = check.json()

        if result.get("status") == "completed":
            return {
                "uid": image_uid,
                "url": result.get("image_url"),
                "status": "completed",
            }
        elif result.get("status") == "failed":
            return {"uid": image_uid, "status": "failed", "error": result.get("error")}

        time.sleep(2)
        elapsed += 2

    return {"uid": image_uid, "status": "timeout"}


def list_templates() -> list:
    """List all available Bannerbear templates."""
    response = httpx.get(f"{BASE_URL}/templates", headers=_headers(), timeout=15)
    response.raise_for_status()
    return response.json()
