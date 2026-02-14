"""Phase 3 — Audience & Pain Points Agent
Builds buyer personas using search data, Reddit, and AI synthesis.
"""

from app.agents.base import BaseAgent


class AudienceProfilerAgent(BaseAgent):
    agent_name = "audience_profiler"
    phase_number = 3

    def run(self, input_data: dict, learning_context: list) -> dict:
        niche = input_data.get("niche", "")
        phase_1 = input_data.get("phase_1_output", {})
        phase_2 = input_data.get("phase_2_output", {})

        # Step 1: Get search questions (People Also Ask, autocomplete)
        search_questions = self._get_search_questions(niche)

        # Step 2: Get Reddit discussions
        reddit_data = self._get_reddit_discussions(niche)

        # Step 3: Perplexity deep research
        research = self._deep_research(niche)

        # Step 4: Build audience profile with LLM
        audience_profile = self._build_profile(
            niche, search_questions, reddit_data, research,
            phase_1.get("analysis", {}), learning_context,
        )

        # Step 5: Extract pain points
        pain_points = self._extract_pain_points(niche, reddit_data, search_questions)

        return {
            "audience_profile": audience_profile,
            "pain_points": pain_points,
            "search_questions": search_questions,
            "reddit_insights": reddit_data,
            "phase": self.phase_number,
            "agent": self.agent_name,
        }

    def _get_search_questions(self, niche: str) -> dict:
        try:
            from app.integrations.serpapi_client import get_people_also_ask, get_autocomplete
            return {
                "people_also_ask": get_people_also_ask(niche),
                "autocomplete": get_autocomplete(niche),
            }
        except Exception as e:
            self.logger.warning("search_questions.failed", error=str(e))
            return {"error": str(e)}

    def _get_reddit_discussions(self, niche: str) -> dict:
        try:
            from app.integrations.reddit_client import get_trending_posts, get_comments
            posts = get_trending_posts(niche, limit=15)
            return {"posts": posts}
        except Exception as e:
            self.logger.warning("reddit.failed", error=str(e))
            return {"error": str(e)}

    def _deep_research(self, niche: str) -> dict:
        try:
            from app.integrations.perplexity_client import call_perplexity
            research_prompt = (
                f"What are the biggest problems, frustrations, and unmet needs "
                f"people have related to {niche}? Include real examples and "
                f"common complaints from forums and communities."
            )
            return {"research": call_perplexity(research_prompt)}
        except Exception as e:
            self.logger.warning("perplexity.failed", error=str(e))
            return {"error": str(e)}

    def _build_profile(self, niche, questions, reddit, research, trends, learning_context) -> dict:
        learning_text = ""
        if learning_context:
            learning_text = "\n\nSUCCESSFUL AUDIENCE PROFILES FROM PAST RUNS:\n"
            for ctx in learning_context:
                learning_text += f"- {ctx['output_summary']}\n"

        prompt = self.get_prompt(
            "build_audience_profile",
            niche=niche,
            search_questions=str(questions),
            reddit_discussions=str(reddit),
            trend_data=str(trends),
        )
        prompt += learning_text

        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _extract_pain_points(self, niche, reddit, questions) -> dict:
        prompt = self.get_prompt(
            "extract_pain_points",
            niche=niche,
            discussions=str({"reddit": reddit, "search_questions": questions}),
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)
