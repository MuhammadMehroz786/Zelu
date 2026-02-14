"""QA Review Agent — Cross-phase quality checker.
Used by other agents to validate outputs.
"""

from app.agents.base import BaseAgent


class QAReviewerAgent(BaseAgent):
    agent_name = "qa_reviewer"
    phase_number = 0  # used across phases

    def run(self, input_data: dict, learning_context: list) -> dict:
        content = input_data.get("content", "")
        check_type = input_data.get("check_type", "general")

        if check_type == "content":
            return self._review_content(content)
        elif check_type == "copy":
            return self._review_marketing_copy(content)
        elif check_type == "brand":
            return self._review_brand_consistency(content, input_data.get("brand_guidelines", {}))
        else:
            return self._general_review(content)

    def _review_content(self, content: str) -> dict:
        prompt = (
            "Review this content for quality. Check for:\n"
            "1. AI artifacts (phrases like 'dive into', 'unleash', 'journey', 'landscape', 'tapestry')\n"
            "2. Repetitive statements\n"
            "3. Generic advice without specifics\n"
            "4. Grammar and flow issues\n"
            "5. Actionability — does it give concrete steps?\n\n"
            f"CONTENT:\n{content[:5000]}\n\n"
            "Return JSON: {\"score\": <1-100>, \"issues\": [{\"type\": \"...\", \"description\": \"...\"}], "
            "\"summary\": \"...\"}"
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _review_marketing_copy(self, content: str) -> dict:
        prompt = (
            "Review this marketing copy for effectiveness. Check for:\n"
            "1. Clear value proposition\n"
            "2. Emotional triggers\n"
            "3. Strong CTAs\n"
            "4. Objection handling\n"
            "5. Urgency/scarcity (without being scammy)\n\n"
            f"COPY:\n{content[:5000]}\n\n"
            "Return JSON: {\"score\": <1-100>, \"strengths\": [...], \"improvements\": [...], \"summary\": \"...\"}"
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _review_brand_consistency(self, content: str, guidelines: dict) -> dict:
        prompt = (
            f"Check if this content matches these brand guidelines:\n{str(guidelines)}\n\n"
            f"CONTENT:\n{content[:5000]}\n\n"
            "Return JSON: {\"consistent\": <bool>, \"issues\": [...], \"suggestions\": [...]}"
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)

    def _general_review(self, content: str) -> dict:
        prompt = (
            f"Review this content for overall quality:\n{content[:5000]}\n\n"
            "Return JSON: {\"score\": <1-100>, \"feedback\": \"...\"}"
        )
        response = self.call_llm("openai", prompt, json_mode=True)
        return self.parse_json_response(response)
