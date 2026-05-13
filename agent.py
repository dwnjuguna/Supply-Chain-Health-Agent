import os
from dotenv import load_dotenv
import anthropic
from domains import build_system_prompt
from scoring import parse_scores

# ── API Key Resolution ─────────────────────────────────────────────────────────
# Priority order:
#   1. Streamlit secrets (st.secrets) — used when deployed on Streamlit Cloud
#   2. Environment variable ANTHROPIC_API_KEY — works on Render, Railway, local
#   3. .env file (via python-dotenv) — local development convenience
#
# We attempt Streamlit secrets first (only available inside a Streamlit runtime),
# then fall back to the standard environment variable loaded by dotenv.

load_dotenv()  # No-op if .env doesn't exist; safe to call always

def _resolve_api_key() -> str:
    """
    Resolve the Anthropic API key from the available secret stores.
    Raises a clear RuntimeError if no key is found anywhere.
    """
    # 1. Try Streamlit secrets (only works inside a running Streamlit app)
    try:
        import streamlit as st
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass  # Not running inside Streamlit, or secrets not configured — move on

    # 2. Try environment variable (covers Render, Railway, local .env via dotenv)
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key

    # 3. Nothing found — raise a clear, actionable error
    raise RuntimeError(
        "ANTHROPIC_API_KEY not found.\n\n"
        "To fix this:\n"
        "  • Locally: add ANTHROPIC_API_KEY=your-key to your .env file\n"
        "  • Streamlit Cloud: add it under App Settings → Secrets\n"
        "  • Render / Railway: add it as an Environment Variable in the dashboard\n\n"
        "Get your key at https://console.anthropic.com"
    )


class SupplyChainHealthAgent:

    def __init__(self, vertical: str = "general"):
        self.vertical = vertical
        self.chat_history = []
        self.system_prompt = build_system_prompt(vertical)
        # Resolve and validate the key at instantiation time so the error
        # surfaces immediately in the UI, not mid-assessment.
        api_key = _resolve_api_key()
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

    def ask_followup(self, question: str) -> str:
        """Send a follow-up question maintaining full conversation history."""
        self.chat_history.append({"role": "user", "content": question})
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=self.system_prompt + "\n\nYou are now in follow-up Q&A mode. Answer concisely and specifically, referencing the assessment report where relevant. Do not output JSON.",
            messages=self.chat_history
        )
        reply = response.content[0].text
        self.chat_history.append({"role": "assistant", "content": reply})
        return reply

    def _call_claude(self, user_msg: str) -> dict:
        self.chat_history = [{"role": "user", "content": user_msg}]
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=self.system_prompt,
            messages=self.chat_history
        )
        reply = response.content[0].text
        self.chat_history.append({"role": "assistant", "content": reply})
        scores = parse_scores(reply)
        narrative_start = reply.find("EXECUTIVE")
        narrative = reply[narrative_start:] if narrative_start != -1 else reply
        return {"scores": scores, "narrative": narrative, "raw": reply}
