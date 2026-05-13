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
# max_uses caps searches per call to control cost.

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
}


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
        "  • Render / Railway: add it as an Environment Variable\n\n"
        "Get your key at https://console.anthropic.com"
    )


def _extract_text(response) -> str:
    """
    Extract all text content from a response that may contain mixed
    content blocks (text, server_tool_use, web_search_tool_result).
    Joins all text blocks in order.
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
        include_cba: bool = False,
        persona: str = "analyst",
        customisation: dict = None,
        enable_web_search: bool = True,
    ):
        self.vertical          = vertical
        self.include_cba       = include_cba
        self.persona           = persona
        self.customisation     = customisation or {}
        self.enable_web_search = enable_web_search
        self.chat_history      = []

        self.system_prompt = build_system_prompt(
            vertical=vertical,
            include_cba=include_cba,
            persona=persona,
            customisation=customisation,
        )

        api_key = _resolve_api_key()
        self.client = anthropic.Anthropic(api_key=api_key)

    # ── Assessment methods ─────────────────────────────────────────────────────

    def run_general_assessment(self, financial_suffix: str = "") -> dict:
        if self.persona == "executive":
            user_msg = (
                f"Perform a strategic supply chain assessment for a typical "
                f"mid-to-large {self.vertical} organisation. Use Gartner Top 25 "
                f"and SCOR world-class benchmarks. Search for the latest supply "
                f"chain trends, disruptions, and benchmark data relevant to this "
                f"vertical before producing your assessment. Score each domain and "
                f"produce the full structured report including Strategic Scenario "
                f"Comparison and Maturity Roadmap."
                f"{financial_suffix}"
            )
        else:
            user_msg = (
                f"Perform a supply chain health assessment for a mid-size "
                f"{self.vertical} company. Search for the latest industry benchmarks, "
                f"supply chain disruptions, and KPI standards relevant to this "
                f"vertical to ground your assessment in current market data. "
                f"Score each domain and produce a full structured report."
                f"{financial_suffix}"
            )
        return self._call_claude(user_msg)

    def run_custom_assessment(
        self, inputs: dict, financial_suffix: str = ""
    ) -> dict:
        formatted = "\n\n".join(
            f"**{k}:** {v}" for k, v in inputs.items() if str(v).strip()
        )
        if self.persona == "executive":
            user_msg = (
                f"Perform a strategic supply chain assessment for a "
                f"{self.vertical} organisation based on the following leadership "
                f"context:\n\n{formatted}\n\n"
                f"Search for the latest supply chain news, benchmarks, and "
                f"regulatory developments relevant to this vertical and their "
                f"stated priorities. Then score each domain and produce the full "
                f"structured report including Strategic Scenario Comparison and "
                f"Maturity Roadmap tailored to their context."
                f"{financial_suffix}"
            )
        else:
            user_msg = (
                f"Perform a supply chain health assessment for a "
                f"{self.vertical} company based on:\n\n{formatted}\n\n"
                f"Search for the latest benchmarks and supply chain developments "
                f"relevant to this vertical to ensure your recommendations reflect "
                f"current market conditions. Score each domain and produce a full "
                f"structured report."
                f"{financial_suffix}"
            )
        return self._call_claude(user_msg)

    def generate_action_pack(self, assessment_narrative: str) -> dict:
        """
        Autonomously generate the three action pack outputs after assessment.
        Called automatically — no user prompt needed.
        Returns dict with keys: board_summary, action_plan, risk_watchlist.
        """
        prompt = (
            f"Based on the following supply chain assessment, autonomously generate "
            f"three outputs. Do not ask for clarification — produce all three now.\n\n"
            f"ASSESSMENT:\n{assessment_narrative}\n\n"
            f"OUTPUT 1 — BOARD SUMMARY\n"
            f"5 bullet points, written for a CFO or CEO. No jargon. Lead with "
            f"financial impact. End with the single most important recommended action.\n\n"
            f"OUTPUT 2 — 90-DAY ACTION PLAN\n"
            f"A prioritised list of 8–10 specific actions. For each action include: "
            f"action name, domain it addresses, suggested owner (role title), "
            f"success metric, and target completion week (Week 1–4, 5–8, or 9–12).\n\n"
            f"OUTPUT 3 — RISK WATCH LIST\n"
            f"Top 5 supply chain risks for this organisation right now. For each: "
            f"risk name, severity (High/Medium/Low), likelihood, business impact, "
            f"and one immediate mitigation action.\n\n"
            f"Format each output with its title (OUTPUT 1, OUTPUT 2, OUTPUT 3) "
            f"as a clear section header."
        )

        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=(
                    "You are a senior supply chain strategy advisor. "
                    "Produce concise, actionable outputs for executive audiences. "
                    "Be specific — name roles, metrics, and timelines. "
                    "Do not hedge excessively. Write with confidence."
                ),
                messages=messages,
                tools=[WEB_SEARCH_TOOL] if self.enable_web_search else [],
            )
            full_text = _extract_text(response)
            return _parse_action_pack(full_text)
        except Exception as e:
            return {
                "board_summary":  f"Action pack generation failed: {e}",
                "action_plan":    "",
                "risk_watchlist": "",
                "raw":            "",
            }

    def get_market_intelligence(self) -> str:
        """
        Autonomously search for live supply chain signals relevant to
        the chosen vertical. Called alongside the assessment.
        Returns formatted markdown string of findings.
        """
        prompt = (
            f"Search for the 5 most important supply chain developments "
            f"happening RIGHT NOW that would affect a {self.vertical} company. "
            f"Cover: freight/shipping conditions, commodity prices if relevant, "
            f"regulatory changes, geopolitical risks, and technology trends. "
            f"For each finding give: a headline, a one-sentence explanation of "
            f"why it matters, and a risk level (High / Medium / Low). "
            f"Be specific — include figures, dates, and sources where available. "
            f"Format as: SIGNAL 1, SIGNAL 2, etc."
        )
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1200,
                system=(
                    "You are a supply chain intelligence analyst with access to "
                    "real-time web search. Always search before responding. "
                    "Prioritise recency — information from the last 30 days "
                    "is far more valuable than older data."
                ),
                messages=[{"role": "user", "content": prompt}],
                tools=[WEB_SEARCH_TOOL],
            )
            return _extract_text(response)
        except Exception as e:
            return f"Market intelligence search unavailable: {e}"

    def ask_followup(self, question: str) -> str:
        self.chat_history.append({"role": "user", "content": question})
        followup_system = (
            self.system_prompt
            + "\n\nYou are in follow-up Q&A mode. Answer concisely and specifically, "
            "referencing the assessment where relevant. Do not output JSON. "
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
                messages=self.chat_history,
                tools=[WEB_SEARCH_TOOL] if self.enable_web_search else [],
            )
            reply = _extract_text(response)
        except Exception as e:
            reply = f"Unable to process your question: {e}"
        self.chat_history.append({"role": "assistant", "content": reply})
        return reply

    # ── Core API call ──────────────────────────────────────────────────────────

    def _call_claude(self, user_msg: str) -> dict:
        self.chat_history = [{"role": "user", "content": user_msg}]

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
        except anthropic.BadRequestError:
            # Graceful fallback: retry without web search if it's not enabled
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=self.chat_history,
            )

        reply = _extract_text(response)
        self.chat_history.append({"role": "assistant", "content": reply})

        scores = parse_scores(reply)
        narrative_start = reply.find("EXECUTIVE")
        narrative = reply[narrative_start:] if narrative_start != -1 else reply

        return {
            "scores":    scores,
            "narrative": narrative,
            "raw":       reply,
        }


# ── Action pack parser ─────────────────────────────────────────────────────────

def _parse_action_pack(text: str) -> dict:
    """Split the action pack text into its three named sections."""
    sections = {"board_summary": "", "action_plan": "", "risk_watchlist": "", "raw": text}
    markers  = {
        "OUTPUT 1": "board_summary",
        "OUTPUT 2": "action_plan",
        "OUTPUT 3": "risk_watchlist",
    }
    current_key = None
    buffer      = []

    for line in text.split("\n"):
        matched = False
        for marker, key in markers.items():
            if marker in line.upper():
                if current_key and buffer:
                    sections[current_key] = "\n".join(buffer).strip()
                current_key = key
                buffer      = []
                matched     = True
                break
        if not matched and current_key:
            buffer.append(line)

    if current_key and buffer:
        sections[current_key] = "\n".join(buffer).strip()

    return sections

