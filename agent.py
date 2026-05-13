import os
from dotenv import load_dotenv
import anthropic
from domains import build_system_prompt
from scoring import parse_scores

load_dotenv()


def _resolve_api_key() -> str:
    try:
        import streamlit as st
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    raise RuntimeError(
        "ANTHROPIC_API_KEY not found.\n\n"
        "To fix this:\n"
        "  • Locally: add ANTHROPIC_API_KEY=your-key to your .env file\n"
        "  • Streamlit Cloud: add it under App Settings → Secrets\n"
        "  • Render / Railway: add it as an Environment Variable in the dashboard\n\n"
        "Get your key at https://console.anthropic.com"
    )


class SupplyChainHealthAgent:

    def __init__(
        self,
        vertical: str = "general",
        include_cba: bool = False,
        persona: str = "analyst",
        customisation: dict = None,
    ):
        self.vertical      = vertical
        self.include_cba   = include_cba
        self.persona       = persona
        self.customisation = customisation or {}
        self.chat_history  = []

        self.system_prompt = build_system_prompt(
            vertical=vertical,
            include_cba=include_cba,
            persona=persona,
            customisation=customisation,
        )

        api_key = _resolve_api_key()
        self.client = anthropic.Anthropic(api_key=api_key)

    def run_general_assessment(self, financial_suffix: str = "") -> dict:
        """Run a general industry-benchmark health check."""
        if self.persona == "executive":
            user_msg = (
                f"Perform a strategic supply chain assessment for a "
                f"{self.vertical} organisation. Use Gartner Top 25 and SCOR "
                f"world-class benchmarks as the baseline. Assume a typical "
                f"mid-to-large organisation with common industry challenges. "
                f"Score each domain, then produce the full structured report "
                f"including the Strategic Scenario Comparison and Maturity Roadmap."
                f"{financial_suffix}"
            )
        else:
            user_msg = (
                f"Perform a general supply chain health assessment for a mid-size "
                f"{self.vertical} company using SCOR and Gartner benchmarks as the "
                f"baseline. Assume a typical organization with common industry "
                f"challenges. Score each domain and produce a full structured report."
                f"{financial_suffix}"
            )
        return self._call_claude(user_msg)

    def run_custom_assessment(
        self, inputs: dict, financial_suffix: str = ""
    ) -> dict:
        """Run assessment using user-provided context."""
        formatted = "\n\n".join(
            f"**{k}:** {v}" for k, v in inputs.items() if str(v).strip()
        )
        if self.persona == "executive":
            user_msg = (
                f"Perform a strategic supply chain assessment for a "
                f"{self.vertical} organisation based on the following context "
                f"provided by the leadership team:\n\n{formatted}\n\n"
                f"Score each domain based on the context provided, infer gaps "
                f"where information is missing, and produce the full structured "
                f"report including the Strategic Scenario Comparison and Maturity "
                f"Roadmap tailored to their stated priorities, investment horizon, "
                f"and risk appetite."
                f"{financial_suffix}"
            )
        else:
            user_msg = (
                f"Perform a supply chain health assessment based on the following "
                f"organizational data for a {self.vertical} company:\n\n{formatted}\n\n"
                f"Score each domain based on what has been shared, note any "
                f"information gaps, and produce a full structured report with "
                f"recommendations."
                f"{financial_suffix}"
            )
        return self._call_claude(user_msg)

    def ask_followup(self, question: str) -> str:
        """Send a follow-up question maintaining full conversation history."""
        self.chat_history.append({"role": "user", "content": question})

        followup_system = self.system_prompt + (
            "\n\nYou are now in follow-up Q&A mode. Answer concisely and "
            "specifically, referencing the assessment report where relevant. "
            "Do not output JSON."
        )
        if self.persona == "executive":
            followup_system += (
                " Maintain executive-level language — no unexplained jargon. "
                "Lead with business impact."
            )
        if self.include_cba:
            followup_system += (
                " If asked about financial figures, always remind the user that "
                "estimates are directional and illustrative only."
            )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=followup_system,
            messages=self.chat_history,
        )
        reply = response.content[0].text
        self.chat_history.append({"role": "assistant", "content": reply})
        return reply

    def _call_claude(self, user_msg: str) -> dict:
        self.chat_history = [{"role": "user", "content": user_msg}]

        # Executive track with scenarios + roadmap needs more tokens
        if self.persona == "executive":
            max_tokens = 4000
        elif self.include_cba:
            max_tokens = 2500
        else:
            max_tokens = 1500

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=self.chat_history,
        )
        reply = response.content[0].text
        self.chat_history.append({"role": "assistant", "content": reply})

        scores = parse_scores(reply)
        narrative_start = reply.find("EXECUTIVE")
        narrative = reply[narrative_start:] if narrative_start != -1 else reply
        return {"scores": scores, "narrative": narrative, "raw": reply}
