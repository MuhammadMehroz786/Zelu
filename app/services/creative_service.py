"""Creative service — ad creative generation pipeline."""

import structlog

logger = structlog.get_logger(__name__)


def build_creative_brief(product_name: str, ad_copy: dict, brand_config: dict) -> dict:
    """Build a creative brief for image generation."""
    variations = ad_copy if isinstance(ad_copy, list) else ad_copy.get("variations", [])

    briefs = []
    for i, variation in enumerate(variations[:4]):
        hook = variation.get("primary_text", "") if isinstance(variation, dict) else str(variation)
        headline = variation.get("headline", "") if isinstance(variation, dict) else ""

        briefs.append({
            "variation": i + 1,
            "hook": hook,
            "headline": headline,
            "formats": ["1:1", "4:5", "9:16"],
            "brand_colors": brand_config.get("colors", "#1a1a2e, #e94560"),
            "style": brand_config.get("style", "modern, clean, professional"),
        })

    return {
        "product_name": product_name,
        "total_images_needed": len(briefs) * 3,  # 3 formats each
        "briefs": briefs,
    }


def estimate_creative_cost(num_variations: int = 4, formats_per_variation: int = 3) -> dict:
    """Estimate the cost of generating ad creatives."""
    total_images = num_variations * formats_per_variation
    cost_per_image = 0.03  # Ideogram Flash/Turbo pricing

    return {
        "total_images": total_images,
        "cost_per_image": cost_per_image,
        "estimated_cost": round(total_images * cost_per_image, 2),
    }
