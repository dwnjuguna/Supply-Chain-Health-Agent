import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agent import SupplyChainHealthAgent
from scoring import interpret_score
from domains import DOMAINS
from personas import (
    PERSONAS,
    EXECUTIVE_CONTEXT_QUESTIONS,
    EXECUTIVE_CUSTOMISATION_OPTIONS,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Supply Chain Health Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system ─────────────────────────────────────────────────────────────
# Purple   #534AB7 — analyst track, primary actions
# Teal     #0F6E56 — executive track, success states
# Amber    #E8A020 — CBA, warnings
# Red      #E24B4A — risks, danger
# Gray     #2C2C2A — text, structure

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background surfaces ── */
/* Warm off-white — softer than pure white, easier on the eye over long sessions */
[data-testid="stAppViewContainer"] {
    background-color: #F7F6F3;
}
section.main > div {
    background-color: #F7F6F3;
}
/* Sidebar gets a faint purple tint to anchor it to the brand */
[data-testid="stSidebar"] {
    background-color: #F0EFF9;
}
/* Keep content blocks white so they lift off the background */
.sc-box, .sc-privacy, .sc-coming-soon {
    background-color: #FFFFFF;
}

/* ── Header ── */
.sc-header {
    background: #1E1A4E;
    border-radius: 16px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}
.sc-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: #534AB7;
    border-radius: 50%;
    opacity: 0.25;
}
.sc-header h1 {
    color: #fff;
    margin: 0 0 4px;
    font-size: 1.65rem;
    font-weight: 600;
    letter-spacing: -0.3px;
}
.sc-header p {
    color: #AFA9EC;
    margin: 0;
    font-size: 0.875rem;
}
.sc-header-badge {
    display: inline-block;
    background: #534AB7;
    color: #EEEDFE;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Disclaimer ── */
.sc-disclaimer {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.25rem;
    font-size: 0.8rem;
    color: #78350F;
    line-height: 1.55;
}

/* ── Persona cards ── */
.persona-card {
    background: #fff;
    border: 1.5px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.75rem 1.5rem 1.5rem;
    text-align: center;
    height: 100%;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.persona-card:hover {
    border-color: #534AB7;
    box-shadow: 0 6px 24px rgba(83,74,183,0.12);
}
.persona-card.exec:hover {
    border-color: #0F6E56;
    box-shadow: 0 6px 24px rgba(15,110,86,0.12);
}
.persona-card.disabled {
    opacity: 0.4;
    pointer-events: none;
}
.persona-icon-wrap {
    width: 56px; height: 56px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 14px;
    font-size: 1.5rem;
}
.persona-icon-wrap.analyst { background: #EEEDFE; }
.persona-icon-wrap.exec    { background: #E1F5EE; }
.persona-icon-wrap.config  { background: #F1EFE8; }
.persona-title {
    font-weight: 600;
    font-size: 0.95rem;
    color: #2C2C2A;
    margin-bottom: 8px;
}
.persona-desc {
    font-size: 0.8rem;
    color: #6B7280;
    line-height: 1.55;
    margin-bottom: 16px;
}
.persona-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    color: #fff;
    text-transform: uppercase;
}

/* ── Score card ── */
.sc-score-overall {
    background: #1E1A4E;
    border-radius: 14px;
    padding: 1.75rem 1.5rem;
    text-align: center;
    color: #fff;
}
.sc-score-number {
    font-size: 3.5rem;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -2px;
}
.sc-score-label {
    font-size: 0.8rem;
    color: #AFA9EC;
    margin-top: 4px;
}
.sc-score-rating {
    font-size: 0.85rem;
    font-weight: 500;
    color: #CEC BF6;
    margin-top: 6px;
}

/* ── Section headers ── */
.sc-section {
    border-left: 3px solid #534AB7;
    padding-left: 0.875rem;
    margin: 1.75rem 0 0.875rem;
    font-weight: 600;
    font-size: 0.95rem;
    color: #2C2C2A;
}
.sc-section.exec { border-color: #0F6E56; }
.sc-section.amber { border-color: #E8A020; }
.sc-section.red   { border-color: #E24B4A; }

/* ── Content boxes ── */
.sc-box {
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 0.875rem;
    line-height: 1.65;
}
.sc-box.risk     { background: #FCEBEB; border-left: 3px solid #E24B4A; }
.sc-box.rec      { background: #E1F5EE; border-left: 3px solid #0F6E56; }
.sc-box.cba      { background: #FFF8E7; border-left: 3px solid #E8A020; }
.sc-box.scenario { background: #F0FDF4; border-left: 3px solid #0F6E56; }
.sc-box.roadmap  { background: #EFF6FF; border-left: 3px solid #3B82F6; }
.sc-box.intel    { background: #F5F4FF; border-left: 3px solid #534AB7; }
.sc-box.action   { background: #F9FAFB; border-left: 3px solid #888780; }

/* ── Privacy box ── */
.sc-privacy {
    background: #F5F4FF;
    border: 1px solid #CECBF6;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.8rem;
    line-height: 1.65;
    color: #3C3489;
}

/* ── Coming soon panel ── */
.sc-coming-soon {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
}
.sc-coming-soon-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}
.sc-capability {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 0.5px solid #E5E7EB;
}
.sc-capability:last-child { border-bottom: none; }
.sc-capability-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    background: #EEEDFE;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    flex-shrink: 0;
    color: #534AB7;
}
.sc-capability-text { font-size: 0.8rem; color: #374151; line-height: 1.45; }
.sc-capability-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 20px;
    background: #E5E7EB;
    color: #6B7280;
    margin-left: 6px;
    vertical-align: middle;
    text-transform: uppercase;
}

/* ── Domain pills ── */
.sc-domain-pill {
    display: inline-block;
    background: #EEEDFE;
    color: #3C3489;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 2px;
}

/* ── Chat ── */
.sc-chat-user  { background: #EEEDFE; border-radius: 12px 12px 4px 12px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.875rem; }
.sc-chat-agent { background: #F1EFE8; border-radius: 12px 12px 12px 4px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.875rem; }

/* ── Progress bars ── */
div[data-testid="stProgress"] > div { background: #534AB7 !important; }

/* ── Tabs ── */
div[data-baseweb="tab-list"] { gap: 4px; }
div[data-baseweb="tab"] { font-size: 0.875rem; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _api_key_ok() -> bool:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return True
    except Exception:
        pass
    return bool(os.environ.get("ANTHROPIC_API_KEY", ""))

def _box(content: str, style: str) -> None:
    st.markdown(
        f'<div class="sc-box {style}">{content.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

def _section(title: str, style: str = "") -> None:
    cls = f"sc-section {style}".strip()
    st.markdown(f'<div class="{cls}">{title}</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

DEFAULTS = {
    "persona":           None,
    "agent":             None,
    "result":            None,
    "action_pack":       None,
    "market_intel":      None,
    "chat_history":      [],
    "assessment_done":   False,
    "cba_consent_given": False,
    "customisation":     {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="sc-header">
    <span class="sc-header-badge">AI-Powered · Agentic</span>
    <h1>🤖 Supply Chain Health Agent</h1>
    <p>End-to-end supply chain diagnostics with live market intelligence &nbsp;·&nbsp; Powered by Anthropic Claude</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sc-disclaimer">
    ℹ️ <strong>Illustrative &amp; Directional Use Only.</strong>
    All assessments, scores, benchmarks, and financial estimates are for informational
    purposes only and do not constitute professional financial, legal, or management
    consulting advice. Validate outputs with qualified advisors before making
    investment decisions.
</div>
""", unsafe_allow_html=True)

if not _api_key_ok():
    st.error(
        "**🔑 API key not configured.**\n\n"
        "Go to your Streamlit app → **⋮ → Settings → Secrets** and add:\n"
        "```\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```",
        icon="🔑",
    )
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LANDING — PERSONA SELECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if st.session_state.persona is None:

    st.markdown("## Who are you?")
    st.markdown(
        "Select your profile and the tool tailors the entire experience — "
        "inputs, analysis depth, and output format — to your needs."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="persona-card">
            <div class="persona-icon-wrap analyst">📊</div>
            <div class="persona-title">Supply Chain Manager / Analyst</div>
            <div class="persona-desc">Deep KPI diagnostics, benchmark comparisons,
            domain inputs, and cost-benefit analysis. Built for practitioners
            who speak the language.</div>
            <span class="persona-badge" style="background:#534AB7;">Practitioner track</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Select — Analyst / Manager", key="btn_analyst",
                     use_container_width=True, type="primary"):
            st.session_state.persona = "analyst"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="persona-card exec">
            <div class="persona-icon-wrap exec">🏢</div>
            <div class="persona-title">C-Suite / Board Member</div>
            <div class="persona-desc">Strategic scenario comparison, maturity
            roadmap, and board-ready summaries. Built for leaders making
            investment and transformation decisions.</div>
            <span class="persona-badge" style="background:#0F6E56;">Executive track</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Select — C-Suite / Board", key="btn_exec",
                     use_container_width=True, type="primary"):
            st.session_state.persona = "executive"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="persona-card disabled config">
            <div class="persona-icon-wrap config">⚙️</div>
            <div class="persona-title">Enterprise Configuration</div>
            <div class="persona-desc">Embed and configure this agent within your
            organisation's systems. Set access controls, presets, branding,
            and compliance guardrails.</div>
            <span class="persona-badge" style="background:#9CA3AF;">Coming soon · Phase 2</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Coming Soon", key="btn_config",
                  use_container_width=True, disabled=True)

    # Coming soon agentic capabilities panel
    st.markdown("""
    <div class="sc-coming-soon">
        <div class="sc-coming-soon-title">🚀 Agentic capabilities — on the roadmap</div>
        <div class="sc-capability">
            <div class="sc-capability-icon">🧠</div>
            <div class="sc-capability-text">
                <strong>Cross-session memory</strong> — Claude remembers your organisation
                across sessions and tracks KPI trends over time.
                <span class="sc-capability-badge">Phase 2</span>
            </div>
        </div>
        <div class="sc-capability">
            <div class="sc-capability-icon">🔔</div>
            <div class="sc-capability-text">
                <strong>Proactive risk alerts</strong> — Claude monitors supply chain
                news and flags risks to your vertical before you ask.
                <span class="sc-capability-badge">Phase 2</span>
            </div>
        </div>
        <div class="sc-capability">
            <div class="sc-capability-icon">🔗</div>
            <div class="sc-capability-text">
                <strong>Workflow integrations</strong> — Push summaries to Slack,
                create Jira tickets, and draft emails — directly from the assessment.
                <span class="sc-capability-badge">Phase 2</span>
            </div>
        </div>
        <div class="sc-capability">
            <div class="sc-capability-icon">🏢</div>
            <div class="sc-capability-text">
                <strong>Enterprise configuration</strong> — Embed with your branding,
                access controls, and organisation-level presets.
                <span class="sc-capability-badge">Phase 2</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHARED SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

persona     = st.session_state.persona
persona_cfg = PERSONAS[persona]

with st.sidebar:
    badge_color = "#534AB7" if persona == "analyst" else "#0F6E56"
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>"
        f"<span style='font-size:1.2rem;'>{persona_cfg['icon']}</span>"
        f"<span style='font-weight:600;font-size:0.9rem;color:#2C2C2A;'>{persona_cfg['title']}</span>"
        f"</div>"
        f"<span style='display:inline-block;background:{badge_color};color:#fff;"
        f"font-size:0.65rem;font-weight:600;padding:2px 9px;border-radius:20px;"
        f"text-transform:uppercase;letter-spacing:0.4px;margin-bottom:12px;'>"
        f"{persona_cfg['badge']}</span>",
        unsafe_allow_html=True,
    )
    if st.button("← Switch profile", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

    st.markdown("---")
    st.markdown("**⚙️ Configuration**")

    vertical_labels = {
        "general":       "🏭 General",
        "semiconductor": "💾 Semiconductor",
        "automotive":    "🚗 Automotive",
        "pharma":        "💊 Pharmaceutical",
        "retail":        "🛒 Retail & E-commerce",
        "cpg":           "📦 Consumer Packaged Goods",
        "aerospace":     "✈️ Aerospace & Defense",
        "healthcare":    "🏥 Healthcare",
    }
    vertical = st.selectbox(
        "Industry vertical",
        list(vertical_labels.keys()),
        format_func=lambda x: vertical_labels[x],
    )

    if persona == "analyst":
        mode = st.radio(
            "Assessment mode",
            ["general", "custom"],
            format_func=lambda x: "⚡ General benchmark"
                                  if x == "general" else "✏️ Custom (describe your org)",
        )
    else:
        mode = "custom"

    st.markdown("---")
    st.markdown("**📊 Score guide**")
    for band, desc in [
        ("🟢 80–100", "Excellent — World-class"),
        ("🔵 60–79",  "Good — Above average"),
        ("🟡 40–59",  "Fair — Needs work"),
        ("🔴 0–39",   "At Risk — Urgent action"),
    ]:
        st.markdown(
            f"<div style='font-size:0.8rem;margin:3px 0;'>"
            f"<strong>{band}</strong>&nbsp; {desc}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem;color:#9CA3AF;'>"
        "<a href='https://github.com/dwnjuguna/supply-chain-health-agent' "
        "style='color:#9CA3AF;'>GitHub</a> · "
        "<a href='https://docs.anthropic.com' style='color:#9CA3AF;'>Docs</a> · "
        "<a href='https://www.anthropic.com/legal/privacy' style='color:#9CA3AF;'>Privacy</a>"
        "</div>",
        unsafe_allow_html=True,
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRACK 1 — ANALYST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

custom_inputs    = {}
financial_context = {}
include_cba      = False
combined_inputs  = {}
customisation    = {}

if persona == "analyst":
    pills = "".join(
        f'<span class="sc-domain-pill">{d["label"]}</span>' for d in DOMAINS
    )
    st.markdown(pills + "<br><br>", unsafe_allow_html=True)

    if mode == "custom":
        _section("📝 Describe your supply chain")
        st.caption("Fill in what you can. Blank fields will be flagged by Claude.")
        c1, c2 = st.columns(2)
        for i, domain in enumerate(DOMAINS):
            with c1 if i % 2 == 0 else c2:
                val = st.text_area(
                    domain["label"], height=88,
                    placeholder=f"Metrics, tools, challenges...",
                    key=f"a_inp_{domain['key']}",
                )
                if val.strip():
                    custom_inputs[domain["label"]] = val

    _section("💰 Cost-benefit analysis", "amber")
    st.markdown("""
    <div class="sc-privacy">
        🔒 <strong>Privacy notice</strong> — Financial data you enter is used only
        to generate your CBA during this session. It is passed to the Anthropic
        Claude API per their <a href="https://www.anthropic.com/legal/privacy"
        target="_blank" style="color:#3C3489;">Privacy Policy</a> and is
        <strong>never stored, logged, or shared</strong>. Session data is
        discarded on tab close or Reset. Optional — skip to run without financials.
        Operated under GDPR (EU) 2016/679 and CCPA.
    </div>
    """, unsafe_allow_html=True)

    cba_consent = st.checkbox(
        "✅ I understand and voluntarily provide financial data. "
        "I acknowledge outputs are illustrative estimates — not financial advice.",
        value=st.session_state.cba_consent_given,
    )
    st.session_state.cba_consent_given = cba_consent

    if cba_consent:
        include_cba = True
        st.caption("Leave any field at 0 / 'Prefer not to say' to use benchmark assumptions.")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            rev = st.selectbox("Annual revenue (USD)",
                ["Prefer not to say","< $50M","$50M–$250M","$250M–$1B","$1B–$5B","$5B–$20B","$20B+"])
            if rev != "Prefer not to say":
                financial_context["Annual Revenue"] = rev
            sc_pct = st.number_input("Supply chain cost (% revenue)", 0.0, 100.0, 0.0, 0.5, format="%.1f")
            if sc_pct > 0:
                financial_context["SC Cost % Revenue"] = f"{sc_pct}%"
        with fc2:
            inv = st.selectbox("Total inventory value (USD)",
                ["Prefer not to say","< $5M","$5M–$25M","$25M–$100M","$100M–$500M","$500M+"])
            if inv != "Prefer not to say":
                financial_context["Inventory Value"] = inv
            freight = st.number_input("Freight cost (% revenue)", 0.0, 100.0, 0.0, 0.5, format="%.1f")
            if freight > 0:
                financial_context["Freight Cost % Revenue"] = f"{freight}%"
        with fc3:
            otif = st.number_input("Current OTIF rate (%)", 0.0, 100.0, 0.0, 1.0, format="%.1f")
            if otif > 0:
                financial_context["OTIF Rate"] = f"{otif}%"
            gm = st.number_input("Gross margin (%)", 0.0, 100.0, 0.0, 1.0, format="%.1f")
            if gm > 0:
                financial_context["Gross Margin"] = f"{gm}%"
        extra = st.text_area("Additional financial context", height=68,
            placeholder="e.g. 'OEE is 55%, we carry 90 days of inventory...'")
        if extra.strip():
            financial_context["Additional"] = extra.strip()
        st.markdown("""
        <div class="sc-disclaimer" style="margin-top:8px;">
            ⚠️ All CBA figures are <strong>directional estimates only</strong>.
            Validate with your finance team before making investment decisions.
        </div>
        """, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRACK 2 — EXECUTIVE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

elif persona == "executive":

    st.markdown("""
    <p style="font-size:0.95rem;color:#4B5563;line-height:1.65;margin-bottom:1.5rem;">
    Answer a few questions about your organisation and priorities. Claude will
    search for the latest market intelligence, diagnose your supply chain,
    compare strategic options, and map a phased improvement roadmap — tailored
    to your context.
    </p>
    """, unsafe_allow_html=True)

    exec_inputs = {}
    _section("📋 Your organisation", "exec")
    for q in EXECUTIVE_CONTEXT_QUESTIONS:
        val = st.text_area(q["label"], placeholder=q["placeholder"],
                           height=q["height"], key=f"exec_{q['key']}")
        if val.strip():
            exec_inputs[q["label"]] = val

    _section("🎛️ Customise this assessment", "exec")
    show_custom = st.toggle("Adjust parameters", value=False,
        help="Fine-tune strategic orientation, timeline, and output style.")
    if show_custom:
        cc1, cc2 = st.columns(2)
        opts = list(EXECUTIVE_CUSTOMISATION_OPTIONS.items())
        for i, (key, cfg) in enumerate(opts):
            with cc1 if i % 2 == 0 else cc2:
                val = st.selectbox(cfg["label"], cfg["options"],
                    index=cfg["options"].index(cfg["default"]),
                    help=cfg["help"], key=f"custom_{key}")
                customisation[key] = val
        st.session_state.customisation = customisation
    else:
        customisation = st.session_state.customisation

    _section("💰 Financial context", "amber")
    st.markdown("""
    <div class="sc-privacy">
        🔒 <strong>Privacy notice</strong> — Financial figures are used solely
        to size the cost-benefit analysis during this session. Passed to the
        <a href="https://www.anthropic.com/legal/privacy" target="_blank"
        style="color:#3C3489;">Anthropic Claude API</a>.
        <strong>Never stored, logged, or shared.</strong>
        Discarded on tab close or Reset. GDPR &amp; CCPA compliant.
    </div>
    """, unsafe_allow_html=True)

    exec_cba = st.checkbox(
        "✅ I understand and voluntarily provide financial context. "
        "I acknowledge all financial outputs are illustrative estimates only.",
        value=st.session_state.cba_consent_given,
    )
    st.session_state.cba_consent_given = exec_cba

    if exec_cba:
        include_cba = True
        ec1, ec2 = st.columns(2)
        with ec1:
            rev = st.selectbox("Annual revenue (USD)",
                ["Prefer not to say","< $50M","$50M–$250M","$250M–$1B","$1B–$5B","$5B–$20B","$20B+"],
                key="exec_rev")
            if rev != "Prefer not to say":
                financial_context["Annual Revenue"] = rev
            budget = st.selectbox("Available transformation budget",
                ["Prefer not to say","< $1M","$1M–$5M","$5M–$20M","$20M–$50M","$50M+"],
                key="exec_budget")
            if budget != "Prefer not to say":
                financial_context["Transformation Budget"] = budget
        with ec2:
            sc_pct = st.number_input("Supply chain cost (% revenue)", 0.0, 100.0, 0.0, 0.5,
                format="%.1f", key="exec_sc")
            if sc_pct > 0:
                financial_context["SC Cost % Revenue"] = f"{sc_pct}%"
            gm = st.number_input("Gross margin (%)", 0.0, 100.0, 0.0, 1.0,
                format="%.1f", key="exec_gm")
            if gm > 0:
                financial_context["Gross Margin"] = f"{gm}%"
        extra = st.text_area("Additional financial context", height=68,
            placeholder="e.g. '$50M tied up in inventory, freight bill $8M/year...'",
            key="exec_extra")
        if extra.strip():
            financial_context["Additional"] = extra.strip()
        st.markdown("""
        <div class="sc-disclaimer" style="margin-top:8px;">
            ⚠️ Scenario and roadmap financial figures are <strong>directional
            estimates only</strong>. Validate with your CFO before committing.
        </div>
        """, unsafe_allow_html=True)

    combined_inputs = {**exec_inputs}
    if financial_context:
        combined_inputs["Financial Context"] = "; ".join(
            f"{k}: {v}" for k, v in financial_context.items()
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN / RESET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
rb1, rb2, _ = st.columns([1, 1, 4])
with rb1:
    run_clicked = st.button("🚀 Run assessment", type="primary",
                            use_container_width=True)
with rb2:
    if st.button("🔄 Reset", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

if run_clicked:
    try:
        agent = SupplyChainHealthAgent(
            vertical=vertical,
            include_cba=include_cba,
            persona=persona,
            customisation=customisation or {},
            enable_web_search=True,
        )
        st.session_state.agent = agent
    except RuntimeError as e:
        st.error(f"**Configuration error:** {e}")
        st.stop()

    st.session_state.chat_history    = []
    st.session_state.assessment_done = False
    st.session_state.action_pack     = None
    st.session_state.market_intel    = None

    financial_suffix = ""
    if include_cba and financial_context:
        lines = "\n".join(f"  • {k}: {v}" for k, v in financial_context.items())
        financial_suffix = (
            f"\n\nFINANCIAL CONTEXT (user-provided):\n{lines}\n\n"
            "Use these figures in the Cost-Benefit Analysis. "
            "State clearly when using provided data vs. benchmark assumptions."
        )
    elif include_cba:
        financial_suffix = (
            "\n\nUser opted into CBA but provided no figures. "
            "Use conservative benchmark assumptions. State all assumptions."
        )

    # ── Run assessment ─────────────────────────────────────────────────────────
    with st.spinner("🔍 Claude is searching the web and analysing your supply chain..."):
        try:
            if persona == "analyst" and mode == "custom" and custom_inputs:
                result = agent.run_custom_assessment(custom_inputs, financial_suffix)
            elif persona == "executive" and combined_inputs:
                result = agent.run_custom_assessment(combined_inputs, financial_suffix)
            else:
                result = agent.run_general_assessment(financial_suffix)
            st.session_state.result          = result
            st.session_state.assessment_done = True
        except Exception as e:
            st.error(f"**Assessment failed:** {e}")
            st.stop()

    # ── Auto-generate action pack ──────────────────────────────────────────────
    with st.spinner("⚡ Generating your action pack..."):
        try:
            ap = agent.generate_action_pack(result.get("narrative", ""))
            st.session_state.action_pack = ap
        except Exception:
            st.session_state.action_pack = None

    # ── Fetch market intelligence ──────────────────────────────────────────────
    with st.spinner("🌐 Fetching live market intelligence..."):
        try:
            mi = agent.get_market_intelligence()
            st.session_state.market_intel = mi
        except Exception:
            st.session_state.market_intel = None

    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESULTS — tabbed, persona-aware
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if st.session_state.assessment_done and st.session_state.result:
    result        = st.session_state.result
    scores_data   = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall       = scores_data.get("overall", "N/A")

    st.markdown("---")

    # Overall score header
    rating, desc = (
        interpret_score(int(overall)) if isinstance(overall, (int, float))
        else ("N/A", "")
    )
    ov_col, sp_col = st.columns([1, 3])
    with ov_col:
        st.markdown(f"""
        <div class="sc-score-overall">
            <div class="sc-score-number">{overall}</div>
            <div class="sc-score-label">Overall health score</div>
            <div class="sc-score-rating">{rating}</div>
        </div>
        """, unsafe_allow_html=True)
    with sp_col:
        st.caption(
            f"Vertical: **{vertical_labels.get(vertical, vertical)}** &nbsp;·&nbsp; "
            f"Track: **{persona_cfg['title']}** &nbsp;·&nbsp; {desc}"
        )
        if domain_scores:
            for domain, score in domain_scores.items():
                r, _ = interpret_score(int(score))
                color = (
                    "#1D9E75" if score >= 80 else
                    "#3B8BD4" if score >= 60 else
                    "#BA7517" if score >= 40 else
                    "#E24B4A"
                )
                st.markdown(
                    f"<div style='font-size:0.82rem;margin:3px 0;'>"
                    f"<strong>{domain.capitalize()}</strong> &nbsp; "
                    f"<span style='color:{color};font-weight:600;'>{score}/100</span> "
                    f"<span style='color:#9CA3AF;font-size:0.75rem;'>{r}</span></div>",
                    unsafe_allow_html=True,
                )
                st.progress(score / 100)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_labels = ["📋 Diagnostic report", "⚡ Action pack", "🌐 Market intelligence", "💬 Q&A"]
    tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

    # ── TAB 1: Diagnostic report ───────────────────────────────────────────────
    with tab1:
        narrative = result.get("narrative", "")
        if narrative:
            SECTIONS = {
                "EXECUTIVE SUMMARY":           ("📋 Executive summary",            "",       "default"),
                "TOP RISKS":                   ("⚠️ Top risks",                    "red",    "risk"),
                "DOMAIN HIGHLIGHTS":           ("🏷️ Domain highlights",            "",       "default"),
                "PRIORITY RECOMMENDATIONS":    ("✅ Priority recommendations",     "exec",   "rec"),
                "COST-BENEFIT ANALYSIS":       ("💰 Cost-benefit analysis",        "amber",  "cba"),
                "STRATEGIC SCENARIO":          ("🔀 Strategic scenario comparison","exec",   "scenario"),
                "SUPPLY CHAIN MATURITY":       ("📅 Maturity roadmap",             "exec",   "roadmap"),
            }
            current = None
            section_text = {}
            for line in narrative.split("\n"):
                matched = False
                for key in SECTIONS:
                    if key in line.upper():
                        current = key
                        section_text[key] = []
                        matched = True
                        break
                if not matched and current:
                    section_text[current].append(line)

            for key, (title, sec_style, box_style) in SECTIONS.items():
                if key in section_text:
                    content = "\n".join(section_text[key]).strip()
                    if content:
                        _section(title, sec_style)
                        if box_style == "default":
                            st.markdown(content)
                        else:
                            _box(content, box_style)

    # ── TAB 2: Action pack ─────────────────────────────────────────────────────
    with tab2:
        ap = st.session_state.action_pack
        if ap:
            _section("📌 Board summary", "")
            st.markdown("""
            <div class="sc-disclaimer">
                ⚠️ Auto-generated from your assessment. Review before sharing externally.
            </div>
            """, unsafe_allow_html=True)
            if ap.get("board_summary"):
                _box(ap["board_summary"], "intel")
            else:
                st.caption("No board summary generated.")

            _section("🗓️ 90-day action plan", "exec")
            if ap.get("action_plan"):
                _box(ap["action_plan"], "action")
            else:
                st.caption("No action plan generated.")

            _section("🚨 Risk watch list", "red")
            if ap.get("risk_watchlist"):
                _box(ap["risk_watchlist"], "risk")
            else:
                st.caption("No risk watch list generated.")
        else:
            st.info("Run an assessment to auto-generate your action pack.")

    # ── TAB 3: Market intelligence ─────────────────────────────────────────────
    with tab3:
        mi = st.session_state.market_intel
        _section("🌐 Live supply chain signals", "")
        st.caption(
            f"Real-time intelligence for the **{vertical_labels.get(vertical, vertical)}** "
            f"vertical, searched during your assessment."
        )
        st.markdown("""
        <div class="sc-disclaimer">
            ℹ️ Sourced via live web search during this assessment.
            Verify critical information before acting on it.
        </div>
        """, unsafe_allow_html=True)
        if mi:
            _box(mi, "intel")
        else:
            st.info("Market intelligence unavailable. Ensure web search is enabled "
                    "at console.anthropic.com.")

        # Coming soon intelligence features
        st.markdown("""
        <div class="sc-coming-soon" style="margin-top:1.5rem;">
            <div class="sc-coming-soon-title">Coming soon in this tab</div>
            <div class="sc-capability">
                <div class="sc-capability-icon">🔔</div>
                <div class="sc-capability-text">
                    <strong>Proactive alerts</strong> — Claude monitors your vertical
                    and notifies you of relevant disruptions.
                    <span class="sc-capability-badge">Phase 2</span>
                </div>
            </div>
            <div class="sc-capability">
                <div class="sc-capability-icon">📈</div>
                <div class="sc-capability-text">
                    <strong>KPI trend tracking</strong> — Compare your scores
                    across assessments over time.
                    <span class="sc-capability-badge">Phase 2</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 4: Q&A ────────────────────────────────────────────────────────────
    with tab4:
        _section("💬 Follow-up Q&A", "")
        if persona == "executive":
            st.caption(
                "Ask Claude to explore any scenario, drill into a roadmap phase, "
                "or prepare a board presentation."
            )
            suggestions = [
                "Walk me through the recommended scenario in detail",
                "What does Phase 1 look like in practice?",
                "What's the cost of doing nothing for 12 months?",
                "Prepare a 5-bullet board summary",
            ]
        else:
            st.caption(
                "Drill into any domain, get action plans, "
                "or compare to specific benchmarks."
            )
            suggestions = [
                "What are the top 3 actions for the next 90 days?",
                "How do we compare to world-class benchmarks?",
                "Give me a board-level summary in 3 bullet points",
                "Which domain has the highest ROI for improvement?",
            ]

        for msg in st.session_state.chat_history:
            tag  = "sc-chat-user"  if msg["role"] == "user" else "sc-chat-agent"
            icon = "🧑" if msg["role"] == "user" else "🤖"
            st.markdown(f'<div class="{tag}">{icon} {msg["content"]}</div>',
                        unsafe_allow_html=True)

        st.markdown("**💡 Suggested questions**")
        sc1, sc2 = st.columns(2)
        for i, s in enumerate(suggestions):
            with sc1 if i % 2 == 0 else sc2:
                if st.button(s, key=f"sugg_{i}", use_container_width=True):
                    with st.spinner("Claude is thinking..."):
                        reply = st.session_state.agent.ask_followup(s)
                    st.session_state.chat_history.append({"role": "user", "content": s})
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

        user_q = st.chat_input("Ask a follow-up question...")
        if user_q:
            with st.spinner("Claude is thinking..."):
                reply = st.session_state.agent.ask_followup(user_q)
            st.session_state.chat_history.append({"role": "user",      "content": user_q})
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<center style='font-size:0.75rem;color:#9CA3AF;'>"
    "Built with the Anthropic Claude SDK &nbsp;·&nbsp; "
    "<a href='https://github.com/dwnjuguna/supply-chain-health-agent' "
    "style='color:#9CA3AF;'>GitHub</a> &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; "
    "<a href='https://www.anthropic.com/legal/privacy' target='_blank' "
    "style='color:#9CA3AF;'>Anthropic Privacy Policy</a>"
    "</center>",
    unsafe_allow_html=True,
)
