"""Phase 8 — Campaign Launch Agent
Generates ad creatives with Ideogram + Bannerbear and launches Meta Ads campaigns.
"""

from app.agents.base import BaseAgent
from app import db
from app.models.product import Product


class CampaignLauncherAgent(BaseAgent):
    agent_name = "campaign_launcher"
    phase_number = 8

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_3 = input_data.get("phase_3_output", {})
        phase_4 = input_data.get("phase_4_output", {})
        phase_6 = input_data.get("phase_6_output", {})
        phase_7 = input_data.get("phase_7_output", {})

        audience_profile = phase_3.get("audience_profile", {})
        blueprint = phase_4.get("blueprint", {})
        ad_copy = phase_7.get("ad_copy", {})
        products = phase_4.get("products_created", [])

        main_product = blueprint.get("main_product", {})
        product_name = main_product.get("title", niche)

        config = input_data.get("pipeline_config", {})
        brand_colors = config.get("brand_colors", "#1a1a2e, #16213e, #e94560")

        # Get cover image URL
        cover_url = None
        for p in products:
            if p.get("product_type") == "main":
                cover_url = (p.get("assets") or {}).get("cover_url")
                break

        # Step 1: Generate ad creative images with Ideogram
        creatives = self._generate_creatives(product_name, ad_copy, brand_colors)

        # Step 2: Apply branded templates with Bannerbear
        branded_creatives = self._apply_templates(product_name, ad_copy, creatives, cover_url, brand_colors)

        # Step 3: Create Meta Ads campaign
        campaign = self._create_campaign(
            product_name, niche, audience_profile, ad_copy,
            branded_creatives, learning_context,
        )

        return {
            "creatives": creatives,
            "branded_creatives": branded_creatives,
            "campaign": campaign,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _generate_creatives(self, product_name: str, ad_copy: dict, brand_colors: str) -> list:
        """Generate ad images with Ideogram for each ad variation."""
        creatives = []
        variations = ad_copy if isinstance(ad_copy, list) else ad_copy.get("variations", [])

        for i, variation in enumerate(variations[:4]):
            hook = variation.get("primary_text", "") if isinstance(variation, dict) else str(variation)

            # Generate prompt for Ideogram
            ideogram_prompt_text = self.get_prompt(
                "ideogram_prompt",
                product_name=product_name,
                hook=hook,
                brand_colors=brand_colors,
            )
            prompt_config = self.call_llm("openai", ideogram_prompt_text, json_mode=True)
            prompt_config = self.parse_json_response(prompt_config)

            # Generate images in multiple formats
            for aspect_ratio in ["1:1", "4:5", "9:16"]:
                try:
                    from app.integrations.ideogram_client import generate_image
                    result = generate_image(
                        prompt=prompt_config.get("prompt", f"Ad creative for {product_name}"),
                        aspect_ratio=aspect_ratio,
                        style=prompt_config.get("style", "design"),
                        negative_prompt=prompt_config.get("negative_prompt", ""),
                    )
                    creatives.append({
                        "variation": i + 1,
                        "hook": hook[:50],
                        "aspect_ratio": aspect_ratio,
                        "url": result.get("url"),
                    })
                except Exception as e:
                    self.logger.warning("ideogram.creative.failed", variation=i, error=str(e))

        return creatives

    def _apply_templates(self, product_name, ad_copy, creatives, cover_url, brand_colors) -> list:
        """Apply branded templates using Bannerbear."""
        branded = []
        try:
            from app.integrations.bannerbear_client import generate_image as bb_generate

            variations = ad_copy if isinstance(ad_copy, list) else ad_copy.get("variations", [])
            for i, variation in enumerate(variations[:4]):
                headline = variation.get("headline", "") if isinstance(variation, dict) else ""
                description = variation.get("description", "") if isinstance(variation, dict) else ""

                result = bb_generate(
                    template_id=None,  # will use default template
                    modifications={
                        "headline": headline,
                        "description": description,
                        "product_name": product_name,
                        "background_image": creatives[i * 3]["url"] if i * 3 < len(creatives) else None,
                        "cover_image": cover_url,
                    },
                )
                branded.append(result)
        except Exception as e:
            self.logger.warning("bannerbear.failed", error=str(e))

        return branded

    def _create_campaign(self, product_name, niche, audience, ad_copy, creatives, learning_context) -> dict:
        """Create a Meta Ads campaign."""
        try:
            from app.integrations.meta_ads import create_campaign

            # Build targeting from audience profile
            targeting = {
                "interests": audience.get("meta_ads_targeting", {}).get("interests", []),
                "age_min": 18,
                "age_max": 65,
            }

            result = create_campaign(
                name=f"ZEULE - {product_name}",
                objective="CONVERSIONS",
                targeting=targeting,
                ad_copy=ad_copy,
                creatives=creatives,
                daily_budget=1000,  # $10 daily budget in cents
            )
            return result
        except Exception as e:
            self.logger.warning("meta_ads.failed", error=str(e))
            return {"error": str(e)}
