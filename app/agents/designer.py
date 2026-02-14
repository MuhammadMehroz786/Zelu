"""Phase 6 — Visual Design Agent
Generates ebook PDFs with Gamma and covers with Ideogram.
"""

from app.agents.base import BaseAgent
from app import db
from app.models.product import Product


class DesignerAgent(BaseAgent):
    agent_name = "designer"
    phase_number = 6

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_4 = input_data.get("phase_4_output", {})
        phase_5 = input_data.get("phase_5_output", {})

        blueprint = phase_4.get("blueprint", {})
        content = phase_5.get("content", {})
        products = phase_4.get("products_created", [])

        results = {}

        # Generate covers for all products
        for product_data in products:
            product_name = product_data.get("name", "")
            product_type = product_data.get("product_type", "main")

            self.logger.info("design.cover", product=product_name)

            # Step 1: Generate cover with Ideogram
            cover = self._generate_cover(product_name, niche, product_type)

            # Step 2: Format content as PDF with Gamma (main product only)
            pdf_url = None
            if product_type == "main" and content.get("main_product"):
                pdf_url = self._generate_pdf(product_name, content["main_product"])

            results[product_data.get("id", product_name)] = {
                "cover": cover,
                "pdf_url": pdf_url,
            }

            # Update product record
            product = Product.query.get(product_data.get("id"))
            if product:
                assets = product.assets or {}
                assets["cover_url"] = cover.get("url")
                if pdf_url:
                    assets["pdf_url"] = pdf_url
                product.assets = assets
                db.session.commit()

        return {
            "design_results": results,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _generate_cover(self, product_name: str, niche: str, product_type: str) -> dict:
        """Generate a book/product cover using Ideogram."""
        try:
            from app.integrations.ideogram_client import generate_image

            prompt = (
                f"Professional ebook cover design for '{product_name}'. "
                f"Clean, modern design with bold title text. "
                f"Niche: {niche}. Type: {product_type}. "
                f"High quality, professional typography, no spelling errors."
            )

            result = generate_image(
                prompt=prompt,
                aspect_ratio="2:3",  # book cover ratio
                style="design",
            )
            return result
        except Exception as e:
            self.logger.warning("ideogram.failed", error=str(e))
            return {"error": str(e)}

    def _generate_pdf(self, product_name: str, content: dict) -> str | None:
        """Format product content as a professional PDF using Gamma."""
        try:
            from app.integrations.gamma_client import create_document

            chapters = content.get("chapters", [])
            full_text = ""
            for ch in chapters:
                full_text += f"\n\n# {ch.get('title', '')}\n\n{ch.get('content', '')}"

            result = create_document(
                title=product_name,
                content=full_text,
                output_format="pdf",
            )
            return result.get("url")
        except Exception as e:
            self.logger.warning("gamma.failed", error=str(e))
            return None
