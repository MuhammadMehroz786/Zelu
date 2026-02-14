"""Phase 4 — Product Structure Agent
Creates the master blueprint: main product + bonuses + upsells + order bump.
"""

from app.agents.base import BaseAgent
from app import db
from app.models.product import Product


class ProductArchitectAgent(BaseAgent):
    agent_name = "product_architect"
    phase_number = 4

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        pipeline_run_id = input_data.get("pipeline_config", {}).get("pipeline_run_id", "")
        phase_2 = input_data.get("phase_2_output", {})
        phase_3 = input_data.get("phase_3_output", {})

        audience_profile = phase_3.get("audience_profile", {})
        pain_points = phase_3.get("pain_points", {})
        competitor_analysis = phase_2.get("validation", {})

        # Step 1: Create master blueprint
        blueprint = self._create_blueprint(
            niche, audience_profile, pain_points, competitor_analysis, learning_context,
        )

        # Step 2: Create product records in database
        products = self._create_product_records(
            pipeline_run_id=input_data.get("pipeline_config", {}).get("pipeline_run_id"),
            niche=niche,
            blueprint=blueprint,
        )

        return {
            "blueprint": blueprint,
            "products_created": [p.to_dict() for p in products],
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _create_blueprint(self, niche, audience, pain_points, competitors, learning_context) -> dict:
        learning_text = ""
        if learning_context:
            learning_text = "\n\nSUCCESSFUL PRODUCT STRUCTURES FROM PAST RUNS:\n"
            for ctx in learning_context:
                learning_text += f"- {ctx['output_summary']}\n"

        prompt = self.get_prompt(
            "create_blueprint",
            niche=niche,
            audience_profile=str(audience),
            pain_points=str(pain_points),
            competitor_analysis=str(competitors),
        )
        prompt += learning_text

        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _create_product_records(self, pipeline_run_id: str, niche: str, blueprint: dict) -> list:
        """Create Product records in the database from the blueprint."""
        if not pipeline_run_id:
            return []

        products = []
        product_types = [
            ("main_product", "main"),
            ("bonus_1", "bonus"),
            ("bonus_2", "bonus"),
            ("order_bump", "order_bump"),
            ("upsell", "upsell"),
        ]

        for key, product_type in product_types:
            product_data = blueprint.get(key, {})
            if not product_data:
                continue

            product = Product(
                pipeline_run_id=pipeline_run_id,
                name=product_data.get("title", f"{niche} - {product_type}"),
                niche=niche,
                product_type=product_type,
                status="draft",
                description=product_data.get("subtitle", ""),
                price=product_data.get("price_point"),
                blueprint=product_data,
            )
            db.session.add(product)
            products.append(product)

        db.session.commit()
        return products
