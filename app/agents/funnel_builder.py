"""Phase 7 — Funnel & Copy Agent
Generates all marketing copy (landing page, emails, checkout)
and prepares funnel assets.
"""

from app.agents.base import BaseAgent
from app import db
from app.models.product import Product


class FunnelBuilderAgent(BaseAgent):
    agent_name = "funnel_builder"
    phase_number = 7

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_3 = input_data.get("phase_3_output", {})
        phase_4 = input_data.get("phase_4_output", {})
        phase_6 = input_data.get("phase_6_output", {})

        audience_profile = phase_3.get("audience_profile", {})
        pain_points = phase_3.get("pain_points", {})
        blueprint = phase_4.get("blueprint", {})
        products = phase_4.get("products_created", [])

        main_product = blueprint.get("main_product", {})
        product_name = main_product.get("title", niche)
        price = main_product.get("price_point", "$27")

        bonuses_text = ""
        for key in ["bonus_1", "bonus_2"]:
            bonus = blueprint.get(key, {})
            if bonus:
                bonuses_text += f"- {bonus.get('title', '')}: {bonus.get('content_outline', '')}\n"

        # Step 1: Generate landing page copy
        landing_page = self._generate_landing_page(
            product_name, str(main_product), audience_profile,
            pain_points, price, bonuses_text, learning_context,
        )

        # Step 2: Generate email sequence
        email_sequence = self._generate_emails(
            product_name, str(main_product), audience_profile,
        )

        # Step 3: Generate ad copy variations
        ad_copy = self._generate_ad_copy(
            product_name, str(main_product), audience_profile, pain_points,
        )

        # Step 4: Set up Stripe product (if key available)
        stripe_result = self._setup_stripe(product_name, price, products)

        # Step 5: Set up GHL workflow
        ghl_result = self._setup_ghl_workflow(product_name, email_sequence)

        return {
            "landing_page_copy": landing_page,
            "email_sequence": email_sequence,
            "ad_copy": ad_copy,
            "stripe": stripe_result,
            "ghl": ghl_result,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _generate_landing_page(self, product_name, description, audience, pain_points, price, bonuses, learning_context) -> dict:
        learning_text = ""
        if learning_context:
            learning_text = "\n\nHIGH-PERFORMING LANDING PAGE PATTERNS:\n"
            for ctx in learning_context:
                learning_text += f"- {ctx['output_summary']}\n"

        prompt = self.get_prompt(
            "generate_landing_page",
            product_name=product_name,
            product_description=description,
            audience_profile=str(audience),
            pain_points=str(pain_points),
            price=str(price),
            bonuses=bonuses,
        )
        prompt += learning_text

        response = self.call_llm("anthropic", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _generate_emails(self, product_name, description, audience) -> dict:
        prompt = self.get_prompt(
            "generate_email_sequence",
            product_name=product_name,
            product_description=description,
            audience_profile=str(audience),
        )
        response = self.call_llm("anthropic", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _generate_ad_copy(self, product_name, description, audience, pain_points) -> dict:
        prompt = self.get_prompt(
            "generate_ad_copy",
            product_name=product_name,
            product_description=description,
            audience_profile=str(audience),
            pain_points=str(pain_points),
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _setup_stripe(self, product_name: str, price: str, products: list) -> dict:
        """Create Stripe product and price."""
        try:
            from app.integrations.stripe_client import create_product_with_price

            price_cents = int(float(str(price).replace("$", "").replace(",", "")) * 100)
            result = create_product_with_price(product_name, price_cents)

            # Update main product record
            for p in products:
                if p.get("product_type") == "main":
                    product = Product.query.get(p.get("id"))
                    if product:
                        product.stripe_product_id = result.get("product_id")
                        product.stripe_price_id = result.get("price_id")
                        db.session.commit()
                    break

            return result
        except Exception as e:
            self.logger.warning("stripe.failed", error=str(e))
            return {"error": str(e)}

    def _setup_ghl_workflow(self, product_name: str, email_sequence: dict) -> dict:
        """Set up GoHighLevel workflow for email automation."""
        try:
            from app.integrations.ghl_client import create_workflow
            return create_workflow(product_name, email_sequence)
        except Exception as e:
            self.logger.warning("ghl.failed", error=str(e))
            return {"error": str(e)}
