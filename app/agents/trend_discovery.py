"""Phase 1 — Trend Discovery Agent
Combines Google Trends, Reddit, and news signals to identify
digital product opportunities.
"""

from app.agents.base import BaseAgent


class TrendDiscoveryAgent(BaseAgent):
    agent_name = "trend_discovery"
    phase_number = 1

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        config = input_data.get("pipeline_config", {})
        category = config.get("category", "general")
        region = config.get("region", "US")
        timeframe = config.get("timeframe", "past_12_months")

        # Step 1: Gather trend signals from multiple sources
        trend_signals = self._gather_signals(niche, region)

        # Step 2: Analyze and score trends with LLM
        analysis = self._analyze_trends(niche, trend_signals, category, region, timeframe, learning_context)

        return {
            "raw_signals": trend_signals,
            "analysis": analysis,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _gather_signals(self, niche: str, region: str) -> dict:
        """Collect trend data from all configured sources."""
        signals = {}

        # Google Trends via SerpAPI
        try:
            from app.integrations.serpapi_client import (
                get_google_trends,
                get_related_searches,
                get_people_also_ask,
            )
            signals["google_trends"] = get_google_trends(niche)
            signals["related_searches"] = get_related_searches(niche)
            signals["people_also_ask"] = get_people_also_ask(niche)
        except Exception as e:
            self.logger.warning("serpapi.failed", error=str(e))
            signals["google_trends"] = {"error": str(e)}

        # Reddit trending discussions
        try:
            from app.integrations.reddit_client import get_trending_posts
            signals["reddit"] = get_trending_posts(niche, limit=20)
        except Exception as e:
            self.logger.warning("reddit.failed", error=str(e))
            signals["reddit"] = {"error": str(e)}

        # Hotmart marketplace (what's selling)
        try:
            from app.integrations.hotmart_client import search_marketplace
            signals["hotmart"] = search_marketplace(niche)
        except Exception as e:
            self.logger.warning("hotmart.failed", error=str(e))
            signals["hotmart"] = {"error": str(e)}

        return signals

    def _analyze_trends(self, niche, signals, category, region, timeframe, learning_context) -> dict:
        """Use LLM to analyze and score trend signals."""
        learning_text = ""
        if learning_context:
            learning_text = "\n\nPAST SUCCESSFUL ANALYSES IN THIS NICHE:\n"
            for ctx in learning_context:
                learning_text += f"- {ctx['output_summary']}\n"

        prompt = self.get_prompt(
            "analyze_trends",
            category=category,
            region=region,
            timeframe=timeframe,
            trend_data=str(signals),
        )
        prompt += learning_text

        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)
