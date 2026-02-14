"""Phase 5 — Content Writing Agent
Writes product content chapter-by-chapter using Claude, with AI review.
"""

from app.agents.base import BaseAgent
from app import db
from app.models.product import Product


class ContentWriterAgent(BaseAgent):
    agent_name = "content_writer"
    phase_number = 5

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_3 = input_data.get("phase_3_output", {})
        phase_4 = input_data.get("phase_4_output", {})

        audience_profile = phase_3.get("audience_profile", {})
        blueprint = phase_4.get("blueprint", {})
        products = phase_4.get("products_created", [])

        config = input_data.get("pipeline_config", {})
        author_style = config.get("author_style", "Conversational, authoritative, practical. No fluff.")

        all_content = {}

        # Write main product chapter by chapter
        main_product = blueprint.get("main_product", {})
        if main_product:
            chapters = main_product.get("chapter_outline", [])
            main_content = self._write_product(
                product_name=main_product.get("title", niche),
                chapters=chapters,
                audience_profile=audience_profile,
                author_style=author_style,
            )
            all_content["main_product"] = main_content

        # Write bonuses
        for bonus_key in ["bonus_1", "bonus_2"]:
            bonus = blueprint.get(bonus_key, {})
            if bonus:
                bonus_content = self._write_bonus(
                    product_name=main_product.get("title", niche),
                    bonus_title=bonus.get("title", ""),
                    bonus_outline=str(bonus.get("content_outline", "")),
                    audience_profile=audience_profile,
                )
                all_content[bonus_key] = bonus_content

        # Write order bump
        order_bump = blueprint.get("order_bump", {})
        if order_bump:
            ob_content = self._write_bonus(
                product_name=main_product.get("title", niche),
                bonus_title=order_bump.get("title", ""),
                bonus_outline=str(order_bump.get("content_outline", "")),
                audience_profile=audience_profile,
            )
            all_content["order_bump"] = ob_content

        # Update product records with content
        self._update_product_records(products, all_content)

        return {
            "content": all_content,
            "chapters_written": len(all_content.get("main_product", {}).get("chapters", [])),
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _write_product(self, product_name, chapters, audience_profile, author_style) -> dict:
        """Write a product chapter by chapter using Claude."""
        written_chapters = []
        previous_summaries = []

        for i, chapter in enumerate(chapters):
            chapter_title = chapter if isinstance(chapter, str) else chapter.get("title", f"Chapter {i+1}")
            chapter_outline = "" if isinstance(chapter, str) else str(chapter.get("key_points", ""))

            self.logger.info("writing.chapter", chapter=i+1, title=chapter_title)

            prompt = self.get_prompt(
                "write_chapter",
                product_name=product_name,
                chapter_title=chapter_title,
                chapter_outline=chapter_outline,
                author_style=author_style,
                audience_profile=str(audience_profile),
                previous_chapters_summary="\n".join(previous_summaries[-3:]),
            )

            content = self.call_llm("anthropic", prompt, json_mode=False)

            # Review the content
            reviewed = self._review_content(content)

            final_content = reviewed.get("revised_content", content) if reviewed.get("score", 100) < 80 else content

            written_chapters.append({
                "chapter_number": i + 1,
                "title": chapter_title,
                "content": final_content,
                "quality_score": reviewed.get("score", 0),
                "issues": reviewed.get("issues", []),
            })

            previous_summaries.append(f"Chapter {i+1} ({chapter_title}): covered key points about {chapter_outline[:100]}")

        return {"chapters": written_chapters}

    def _write_bonus(self, product_name, bonus_title, bonus_outline, audience_profile) -> dict:
        """Write a bonus resource."""
        prompt = self.get_prompt(
            "write_bonus",
            product_name=product_name,
            bonus_title=bonus_title,
            bonus_outline=bonus_outline,
            audience_profile=str(audience_profile),
        )

        content = self.call_llm("anthropic", prompt, json_mode=False)
        return {"title": bonus_title, "content": content}

    def _review_content(self, content: str) -> dict:
        """Run the QA review agent on written content."""
        prompt = self.get_prompt("review_content", content=content[:5000])
        try:
            response = self.call_llm("openai", prompt, json_mode=True)
            return self.parse_json_response(response)
        except Exception as e:
            self.logger.warning("review.failed", error=str(e))
            return {"score": 100, "issues": []}

    def _update_product_records(self, products: list, all_content: dict):
        """Update product records with written content."""
        type_to_key = {
            "main": "main_product",
            "bonus": ["bonus_1", "bonus_2"],
            "order_bump": "order_bump",
        }
        bonus_index = 0

        for product_data in products:
            product = Product.query.get(product_data.get("id"))
            if not product:
                continue

            if product.product_type == "main":
                product.content = all_content.get("main_product")
            elif product.product_type == "bonus":
                key = f"bonus_{bonus_index + 1}"
                product.content = all_content.get(key)
                bonus_index += 1
            elif product.product_type == "order_bump":
                product.content = all_content.get("order_bump")

        db.session.commit()
