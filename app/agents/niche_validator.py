"""Phase 2 — Niche Validation Agent
Validates demand using Meta Ad Library, Hotmart, and competitor analysis.
"""

from app.agents.base import BaseAgent


class NicheValidatorAgent(BaseAgent):
    agent_name = "niche_validator"
    phase_number = 2

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_1 = input_data.get("phase_1_output", {})
        trends = phase_1.get("analysis", {})

        # Step 1: Check Meta Ad Library for active advertisers
        competitor_ads = self._get_competitor_ads(niche)

        # Step 2: Check Hotmart marketplace for existing products
        marketplace_data = self._get_marketplace_data(niche)

        # Step 3: Get keyword data for demand signals
        keyword_data = self._get_keyword_data(niche)

        # Step 4: LLM validates the niche
        validation = self._validate(niche, trends, competitor_ads, marketplace_data, keyword_data, learning_context)

        return {
            "competitor_ads": competitor_ads,
            "marketplace_data": marketplace_data,
            "keyword_data": keyword_data,
            "validation": validation,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _get_competitor_ads(self, niche: str) -> dict:
        try:
            from app.integrations.meta_adlibrary import search_ads
            return search_ads(niche, limit=20)
        except Exception as e:
            self.logger.warning("meta_adlibrary.failed", error=str(e))
            return {"error": str(e)}

    def _get_marketplace_data(self, niche: str) -> dict:
        try:
            from app.integrations.hotmart_client import search_marketplace
            return search_marketplace(niche)
        except Exception as e:
            self.logger.warning("hotmart.failed", error=str(e))
            return {"error": str(e)}

    def _get_keyword_data(self, niche: str) -> dict:
        try:
            from app.integrations.serpapi_client import get_keyword_data
            return get_keyword_data(niche)
        except Exception as e:
            self.logger.warning("serpapi_keywords.failed", error=str(e))
            return {"error": str(e)}

    def _validate(self, niche, trends, ads, marketplace, keywords, learning_context) -> dict:
        learning_text = ""
        if learning_context:
            learning_text = "\n\nPAST VALIDATION RESULTS FOR SIMILAR NICHES:\n"
            for ctx in learning_context:
                learning_text += f"- Score: {ctx.get('performance_score', 'N/A')} | {ctx['output_summary']}\n"

        prompt = self.get_prompt(
            "validate_niche",
            niche=niche,
            trend_data=str(trends),
            competitor_data=str(ads),
            marketplace_data=str(marketplace),
        )
        prompt += learning_text

        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)
