import os
from dotenv import load_dotenv
import anthropic
from domains import build_system_prompt
from scoring import parse_scores

load_dotenv()

# ── Web search tool definition ─────────────────────────────────────────────────
# Server-side tool — Anthropic executes searches autonomously.
# Claude decides when and what to search during assessment.
# Requires web search to be enabled at console.anthropic.com.
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
}

# ── Text extractor for mixed content responses ─────────────────────────────────
def _extract_text(response) -> str:
    """
    Extract all text content from a response that may contain mixed
    content blocks (text, server_tool_use, web_search_tool_result).
    """
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text" and block.text:
            parts.append(block.text)
    return "\n".join(parts).strip()

class SupplyChainHealthAgent:
    def __init__(
        self,
        vertical: str = "general",
        persona: str = "analyst",
        include_cba: bool = False,
        enable_web_search: bool = True,
        customisation: dict = None,
    ):
        self.vertical          = vertical
        self.persona           = persona
        self.include_cba       = include_cba
        self.enable_web_search = enable_web_search
        self.customisation     = customisation or {}
        self.chat_history      = []
        self.system_prompt     = build_system_prompt(vertical)

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY", api_key)
        except Exception:
            pass
        self.client = anthropic.Anthropic(api_key=api_key)

    def run_general_assessment(self) -> dict:
        """Run a general industry-benchmark health check."""
        user_msg = (
            f"Perform a general supply chain health assessment for a mid-size "
            f"{self.vertical} company using SCOR and Gartner benchmarks as the baseline. "
            f"Assume a typical organization with common industry challenges. "
            f"Score each domain and produce a full structured report."
        )
        return self._call_claude(user_msg)

    def run_custom_assessment(self, inputs: dict) -> dict:
        """Run assessment using user-provided domain data."""
        formatted = "\n\n".join(
            f"**{domain}:** {value}"
            for domain, value in inputs.items()
            if value.strip()
        )
        user_msg = (
            f"Perform a supply chain health assessment based on the following "
            f"organizational data for a {self.vertical} company:\n\n{formatted}\n\n"
            f"Score each domain based on what has been shared, note any information "
            f"gaps, and produce a full structured report with recommendations."
        )
        return self._call_claude(user_msg)

    def ask_followup(
        self,
        question: str,
        history: list = None,
        assessment_context: str = None,
    ) -> str:
        """
        Answer a follow-up question.
        History is owned by the caller — no internal appends here.
        assessment_context: the narrative from the completed assessment,
        injected into the system prompt so Claude always has the results.
        """
        messages = (history if history is not None else self.chat_history)
        messages = messages + [{"role": "user", "content": question}]

        followup_system = self.system_prompt

        # Inject the actual assessment results so Claude never loses context
        if assessment_context:
            followup_system += (
                "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "COMPLETED ASSESSMENT RESULTS FOR THIS SESSION\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{assessment_context}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )

        followup_system += (
            "\n\nYou are in follow-up Q&A mode. Always reference the specific "
            "scores, findings and recommendations from the assessment above "
            "when answering. Be concise and specific. Do not output JSON. "
            "You may search the web if the question requires current data."
        )
        if self.persona == "executive":
            followup_system += (
                " Maintain executive-level language. Lead with business impact."
            )
        if self.include_cba:
            followup_system += (
                " Remind the user that financial estimates are directional only."
            )
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=followup_system,
                messages=messages,
                tools=[WEB_SEARCH_TOOL] if self.enable_web_search else [],
            )
            reply = _extract_text(response)
        except Exception as e:
            reply = f"Unable to process your question: {e}"

        return reply

    def _call_claude(self, user_msg: str) -> dict:
        self.chat_history = [{"role": "user", "content": user_msg}]

        # Token budget scales with persona and features
        if self.persona == "executive":
            max_tokens = 4000
        elif self.include_cba:
            max_tokens = 2500
        else:
            max_tokens = 1800

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=self.chat_history,
                tools=[WEB_SEARCH_TOOL] if self.enable_web_search else [],
            )
        except Exception as e:
            return {
                "scores":    None,
                "narrative": f"Assessment failed: {e}",
                "raw":       "",
            }

        reply = _extract_text(response)
        self.chat_history.append({"role": "assistant", "content": reply})
        scores = parse_scores(reply)

        # Locate narrative — try multiple section headers robustly
        narrative = reply
        for marker in ["EXECUTIVE SUMMARY", "EXECUTIVE", "TOP RISKS", "DOMAIN"]:
            idx = reply.upper().find(marker)
            if idx != -1:
                narrative = reply[idx:]
                break

        return {"scores": scores, "narrative": narrative, "raw": reply}
