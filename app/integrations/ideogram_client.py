"""Ideogram API integration — AI image generation for covers and ad creatives."""

import httpx
from config.settings import settings

BASE_URL = "https://api.ideogram.ai"


def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    style: str = "design",
    negative_prompt: str = "",
    model: str = "V_2",
) -> dict:
    """Generate an image using Ideogram API."""
    response = httpx.post(
        f"{BASE_URL}/generate",
        headers={
            "Api-Key": settings.IDEOGRAM_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio.upper().replace(":", "_"),
                "model": model,
                "style_type": style.upper(),
                "negative_prompt": negative_prompt,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    images = data.get("data", [])
    if images:
        return {
            "url": images[0].get("url"),
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
        }

    return {"error": "No images generated", "prompt": prompt}
