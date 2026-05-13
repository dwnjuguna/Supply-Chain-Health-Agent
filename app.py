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

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1E1A4E 0%, #534AB7 100%);
    padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;
}
.main-header h1 { color: white; margin: 0; font-size: 2rem; }
.main-header p  { color: #AFA9EC; margin: 0.5rem 0 0; font-size: 1rem; }

.persona-card {
    border: 2px solid #E5E7EB; border-radius: 14px;
    padding: 1.5rem; text-align: center; cursor: pointer;
    transition: all 0.2s ease; background: white; height: 100%;
}
.persona-card:hover { border-color: #534AB7; box-shadow: 0 4px 16px rgba(83,74,183,0.15); }
.persona-card.selected { border-color: #534AB7; background: #F5F4FF; }
.persona-card.disabled { opacity: 0.45; cursor: not-allowed; }
.persona-icon  { font-size: 2.5rem; margin-bottom: 0.5rem; }
.persona-title { font-weight: 700; font-size: 1.05rem; margin-bottom: 0.4rem; }
.persona-desc  { font-size: 0.82rem; color: #6B7280; line-height: 1.4; }
.persona-badge {
    display: inline-block; border-radius: 20px; padding: 2px 10px;
    font-size: 0.72rem; font-weight: 600; margin-top: 0.6rem; color: white;
}

.score-overall {
    background: linear-gradient(135deg, #534AB7, #0F6E56);
    color: white; border-radius: 12px; padding: 1.5rem; text-align: center;
}
.section-header {
    border-left: 4px solid #534AB7; padding-left: 0.75rem;
    margin: 1.5rem 0 0.75rem; font-weight: 600; color: #2C2C2A;
}
.exec-section-header {
    border-left: 4px solid #0F6E56; padding-left: 0.75rem;
    margin: 1.5rem 0 0.75rem; font-weight: 600; color: #2C2C2A;
}
.risk-box     { background: #FCEBEB; border-left: 4px solid #E24B4A; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.rec-box      { background: #E1F5EE; border-left: 4px solid #0F6E56; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.cba-box      { background: #FFF8E7; border-left: 4px solid #E8A020; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.scenario-box { background: #F0FDF4; border-left: 4px solid #0F6E56; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.roadmap-box  { background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.privacy-box  { background: #F0F4FF; border: 1px solid #C7D2FE; border-radius: 10px; padding: 1.25rem 1.5rem; margin: 1rem 0; }
.disclaimer-box { background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 8px; padding: 1rem 1.25rem; margin: 0.75rem 0; font-size: 0.85rem; color: #78350F; }
.domain-pill  { display: inline-block; background: #EEEDFE; color: #534AB7; border-radius: 20px; padding: 3px 12px; font-size: 0.8rem; margin: 2px; font-weight: 500; }
.chat-user    { background: #EEEDFE; border-radius: 12px 12px 4px 12px; padding: 0.75rem 1rem; margin: 0.5rem 0; }
.chat-agent   { background: #F1EFE8; border-radius: 12px 12px 12px 4px; padding: 0.75rem 1rem; margin: 0.5rem 0; }
div[data-testid="stProgress"] > div { background: #534AB7 !important; }
</style>
""", unsafe_allow_html=True)

# ── API key check ─────────────────────────────────────────────────────────────

def _api_key_is_configured() -> bool:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return True
    except Exception:
        pass
    return bool(os.environ.get("ANTHROPIC_API_KEY", ""))

api_key_ok = _api_key_is_configured()

# ── Session state ─────────────────────────────────────────────────────────────

defaults = {
    "persona":            None,   # "analyst" | "executive"
    "agent":              None,
    "result":             None,
    "chat_history":       [],
    "assessment_done":    False,
    "cba_consent_given":  False,
    "customisation":      {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🤖 Supply Chain Health Agent</h1>
    <p>AI-powered end-to-end supply chain diagnostics · Powered by Anthropic Claude SDK</p>
</div>
""", unsafe_allow_html=True)

# Global illustrative disclaimer — always visible
st.markdown("""
<div class="disclaimer-box">
    ℹ️ <strong>Illustrative &amp; Directional Use Only.</strong>
    All assessments, scores, benchmarks, and financial estimates produced by this tool
    are for informational and directional purposes only. They do not constitute
    professional financial, legal, or management consulting advice. You are encouraged
    to use your own data and validate all outputs with qualified advisors before making
    business or investment decisions.
</div>
""", unsafe_allow_html=True)

if not api_key_ok:
    st.error(
        "**🔑 Anthropic API key not configured.**\n\n"
        "1. Go to your app on [share.streamlit.io](https://share.streamlit.io)\n"
        "2. Click **⋮ → Settings → Secrets** and add:\n"
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
        "Select the profile that best describes your role. "
        "The tool will tailor the experience and output to your needs."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(3, gap="large")
    for col, (key, p) in zip(cols, PERSONAS.items()):
        with col:
            disabled = p.get("disabled", False)
            card_cls = "persona-card disabled" if disabled else "persona-card"
            st.markdown(f"""
            <div class="{card_cls}">
                <div class="persona-icon">{p['icon']}</div>
                <div class="persona-title">{p['title']}</div>
                <div class="persona-desc">{p['description']}</div>
                <span class="persona-badge"
                      style="background:{p['badge_color']}">
                    {p['badge']}
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if not disabled:
                if st.button(
                    f"Select — {p['title']}",
                    key=f"persona_btn_{key}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state.persona = key
                    st.rerun()
            else:
                st.button(
                    "Coming Soon",
                    key=f"persona_btn_{key}",
                    use_container_width=True,
                    disabled=True,
                )
    st.stop()  # Nothing below renders until a persona is chosen

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHARED SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

persona     = st.session_state.persona
persona_cfg = PERSONAS[persona]

with st.sidebar:
    # Show which track is active + allow switching
    st.markdown(f"### {persona_cfg['icon']} {persona_cfg['title']}")
    st.caption(f"*{persona_cfg['badge']}*")
    if st.button("← Switch profile", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")

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
        "Industry Vertical",
        list(vertical_labels.keys()),
        format_func=lambda x: vertical_labels[x],
        index=0,
    )

    # Analyst track only — assessment mode toggle
    if persona == "analyst":
        mode = st.radio(
            "Assessment Mode",
            ["general", "custom"],
            format_func=lambda x: "⚡ General (instant benchmark)"
                                  if x == "general"
                                  else "✏️ Custom (describe your org)",
        )
    else:
        mode = "custom"   # Executive track always uses context inputs

    st.markdown("---")
    st.markdown("### 📊 Score Guide")
    for band, desc in [
        ("🟢 80–100", "Excellent — World-class"),
        ("🔵 60–79",  "Good — Above average"),
        ("🟡 40–59",  "Fair — Improvement needed"),
        ("🔴 0–39",   "At Risk — Urgent action"),
    ]:
        st.markdown(f"**{band}** {desc}")

    st.markdown("---")
    st.markdown("[GitHub](https://github.com/dwnjuguna/supply-chain-health-agent) · "
                "[Anthropic Docs](https://docs.anthropic.com) · "
                "[SCOR](https://www.ascm.org/learning-development/scor/)")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRACK 1 — ANALYST / MANAGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if persona == "analyst":

    domains_html = "".join(
        f'<span class="domain-pill">{d["label"]}</span>' for d in DOMAINS
    )
    st.markdown(domains_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Domain inputs
    custom_inputs = {}
    if mode == "custom":
        st.markdown('<div class="section-header">📝 Describe Your Supply Chain</div>',
                    unsafe_allow_html=True)
        st.caption("Fill in what you can. Blank fields will be flagged by Claude.")
        col1, col2 = st.columns(2)
        for i, domain in enumerate(DOMAINS):
            with col1 if i % 2 == 0 else col2:
                val = st.text_area(
                    domain["label"],
                    placeholder=f"Describe your {domain['label'].lower()} — "
                                f"metrics, tools, challenges...",
                    height=90,
                    key=f"analyst_input_{domain['key']}",
                )
                if val.strip():
                    custom_inputs[domain["label"]] = val

    # CBA section
    st.markdown('<div class="section-header">💰 Cost-Benefit Analysis (Optional)</div>',
                unsafe_allow_html=True)
    st.markdown('<a name="privacy"></a>', unsafe_allow_html=True)
    st.markdown("""
    <div class="privacy-box">
        <strong>🔒 Privacy Notice</strong><br><br>
        <strong>What we collect:</strong> Financial figures you enter below.<br>
        <strong>How it's used:</strong> Solely to generate your cost-benefit analysis
        during this session. Data is passed to the
        <a href="https://www.anthropic.com/legal/privacy" target="_blank">Anthropic Claude API</a>
        in accordance with their Privacy Policy.<br>
        <strong>Storage:</strong> <em>None.</em> No financial data is stored, logged, or
        retained. It exists only in your browser session and is discarded on tab close,
        Reset, or session expiry.<br>
        <strong>Sharing:</strong> Never sold or shared with third parties.<br>
        <em>Operated in accordance with GDPR (EU) 2016/679 and CCPA.</em>
    </div>
    """, unsafe_allow_html=True)

    cba_consent = st.checkbox(
        "✅ I understand the above. I voluntarily choose to enter financial data "
        "and acknowledge that all outputs are directional estimates for illustrative "
        "purposes only — not professional financial advice.",
        value=st.session_state.cba_consent_given,
    )
    st.session_state.cba_consent_given = cba_consent

    financial_context = {}
    include_cba = False

    if cba_consent:
        st.caption("Enter as many fields as you like. Blank fields use benchmark assumptions.")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            rev = st.selectbox("Annual Revenue (USD)",
                               ["Prefer not to say","< $50M","$50M–$250M",
                                "$250M–$1B","$1B–$5B","$5B–$20B","$20B+"])
            if rev != "Prefer not to say":
                financial_context["Annual Revenue Range"] = rev
            sc_pct = st.number_input("Supply Chain Cost (% of revenue)",
                                     0.0, 100.0, 0.0, 0.5, format="%.1f")
            if sc_pct > 0:
                financial_context["Supply Chain Cost % of Revenue"] = f"{sc_pct}%"
        with fc2:
            inv = st.selectbox("Total Inventory Value (USD)",
                               ["Prefer not to say","< $5M","$5M–$25M",
                                "$25M–$100M","$100M–$500M","$500M+"])
            if inv != "Prefer not to say":
                financial_context["Total Inventory Value"] = inv
            freight = st.number_input("Freight Cost (% of revenue)",
                                      0.0, 100.0, 0.0, 0.5, format="%.1f")
            if freight > 0:
                financial_context["Freight Cost % of Revenue"] = f"{freight}%"
        with fc3:
            otif = st.number_input("Current OTIF Rate (%)",
                                   0.0, 100.0, 0.0, 1.0, format="%.1f")
            if otif > 0:
                financial_context["Current OTIF Rate"] = f"{otif}%"
            gm = st.number_input("Gross Margin (%)",
                                 0.0, 100.0, 0.0, 1.0, format="%.1f")
            if gm > 0:
                financial_context["Gross Margin"] = f"{gm}%"
        extra = st.text_area("Any other financial context (optional)",
                             placeholder="e.g. 'We carry 90 days of inventory, "
                                         "OEE is currently 55%...'",
                             height=70)
        if extra.strip():
            financial_context["Additional Context"] = extra.strip()
        include_cba = True
        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <strong>Reminder:</strong> All cost-benefit figures are
            <strong>directional estimates for illustrative purposes only</strong>.
            Validate with your finance team before making investment decisions.
        </div>
        """, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRACK 2 — C-SUITE / EXECUTIVE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

elif persona == "executive":

    st.markdown("""
    ### Strategic Supply Chain Assessment
    Answer a few questions about your organisation and priorities.
    Claude will diagnose your current state, compare strategic options,
    and map out a phased improvement roadmap tailored to your context.
    """)

    # Context questions
    exec_inputs = {}
    st.markdown('<div class="section-header">📋 Your Organisation</div>',
                unsafe_allow_html=True)
    for q in EXECUTIVE_CONTEXT_QUESTIONS:
        val = st.text_area(
            q["label"],
            placeholder=q["placeholder"],
            height=q["height"],
            key=f"exec_{q['key']}",
        )
        if val.strip():
            exec_inputs[q["label"]] = val

    # Customisation toggle
    st.markdown('<div class="section-header">🎛️ Customise This Assessment</div>',
                unsafe_allow_html=True)
    show_custom = st.toggle(
        "Adjust assessment parameters",
        value=False,
        help="Fine-tune the strategic orientation, timeline, and output style.",
    )

    customisation = {}
    if show_custom:
        cc1, cc2 = st.columns(2)
        opts = list(EXECUTIVE_CUSTOMISATION_OPTIONS.items())
        for i, (key, cfg) in enumerate(opts):
            with cc1 if i % 2 == 0 else cc2:
                val = st.selectbox(
                    cfg["label"],
                    cfg["options"],
                    index=cfg["options"].index(cfg["default"]),
                    help=cfg["help"],
                    key=f"custom_{key}",
                )
                customisation[key] = val
        st.session_state.customisation = customisation
    else:
        customisation = st.session_state.customisation

    # Financial context for CBA — same privacy-first approach
    st.markdown('<div class="section-header">💰 Financial Context (Optional)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="privacy-box">
        <strong>🔒 Privacy Notice</strong><br><br>
        Any financial figures you provide are used solely to size the cost-benefit
        analysis in this session. They are passed to the
        <a href="https://www.anthropic.com/legal/privacy" target="_blank">Anthropic Claude API</a>
        and are <strong>never stored, logged, or shared</strong>. This session data is
        permanently discarded when you close the tab or click Reset.<br>
        <em>Operated in accordance with GDPR (EU) 2016/679 and CCPA.</em>
    </div>
    """, unsafe_allow_html=True)

    exec_cba_consent = st.checkbox(
        "✅ I understand the privacy notice above and voluntarily choose to provide "
        "financial context. I acknowledge all financial outputs are directional "
        "estimates for illustrative purposes only — not professional financial advice.",
        value=st.session_state.cba_consent_given,
    )
    st.session_state.cba_consent_given = exec_cba_consent

    financial_context = {}
    include_cba       = False

    if exec_cba_consent:
        ec1, ec2 = st.columns(2)
        with ec1:
            rev = st.selectbox("Annual Revenue (USD)",
                               ["Prefer not to say","< $50M","$50M–$250M",
                                "$250M–$1B","$1B–$5B","$5B–$20B","$20B+"],
                               key="exec_rev")
            if rev != "Prefer not to say":
                financial_context["Annual Revenue Range"] = rev
            inv_budget = st.selectbox("Available Transformation Budget",
                                      ["Prefer not to say","< $1M","$1M–$5M",
                                       "$5M–$20M","$20M–$50M","$50M+"],
                                      key="exec_inv_budget")
            if inv_budget != "Prefer not to say":
                financial_context["Available Transformation Budget"] = inv_budget
        with ec2:
            sc_pct = st.number_input("Supply Chain Cost (% of revenue)",
                                     0.0, 100.0, 0.0, 0.5, format="%.1f",
                                     key="exec_sc_pct")
            if sc_pct > 0:
                financial_context["Supply Chain Cost % of Revenue"] = f"{sc_pct}%"
            gm = st.number_input("Gross Margin (%)",
                                 0.0, 100.0, 0.0, 1.0, format="%.1f",
                                 key="exec_gm")
            if gm > 0:
                financial_context["Gross Margin"] = f"{gm}%"

        extra = st.text_area("Any other financial context",
                             placeholder="e.g. 'We have $50M tied up in inventory, "
                                         "our freight bill is $8M/year...'",
                             height=70, key="exec_extra")
        if extra.strip():
            financial_context["Additional Context"] = extra.strip()
        include_cba = True
        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ All scenario and roadmap financial figures are
            <strong>directional estimates for illustrative purposes only</strong>.
            Validate with your CFO and advisors before committing to investments.
        </div>
        """, unsafe_allow_html=True)

    # Merge exec inputs + financial context for the agent
    combined_inputs = {**exec_inputs}
    if financial_context:
        combined_inputs["Financial Context"] = "; ".join(
            f"{k}: {v}" for k, v in financial_context.items()
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN / RESET — shared across both tracks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
btn1, btn2, _ = st.columns([1, 1, 4])

with btn1:
    run_clicked = st.button("🚀 Run Assessment", type="primary",
                            use_container_width=True)
with btn2:
    if st.button("🔄 Reset", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

if run_clicked:
    try:
        if persona == "analyst":
            agent = SupplyChainHealthAgent(
                vertical=vertical,
                include_cba=include_cba,
                persona="analyst",
            )
        else:
            agent = SupplyChainHealthAgent(
                vertical=vertical,
                include_cba=include_cba,
                persona="executive",
                customisation=customisation or {},
            )
        st.session_state.agent = agent
    except RuntimeError as e:
        st.error(f"**Configuration error:** {e}")
        st.stop()

    st.session_state.chat_history    = []
    st.session_state.assessment_done = False

    # Build financial suffix
    financial_suffix = ""
    if include_cba and financial_context:
        lines = "\n".join(f"  • {k}: {v}" for k, v in financial_context.items())
        financial_suffix = (
            f"\n\nFINANCIAL CONTEXT PROVIDED BY USER:\n{lines}\n\n"
            "Use these figures directly in the Cost-Benefit Analysis. "
            "State clearly when using provided data vs. benchmark assumptions."
        )
    elif include_cba:
        financial_suffix = (
            "\n\nThe user has opted into financial analysis but has not provided "
            "specific figures. Use conservative industry benchmark assumptions "
            "for the chosen vertical. State all assumptions clearly."
        )

    with st.spinner("🔍 Claude is analysing your supply chain..."):
        try:
            if persona == "analyst" and mode == "custom" and custom_inputs:
                result = agent.run_custom_assessment(
                    custom_inputs, financial_suffix=financial_suffix
                )
            elif persona == "executive" and combined_inputs:
                result = agent.run_custom_assessment(
                    combined_inputs, financial_suffix=financial_suffix
                )
            else:
                result = agent.run_general_assessment(
                    financial_suffix=financial_suffix
                )
            st.session_state.result          = result
            st.session_state.assessment_done = True
        except Exception as e:
            st.error(f"**Assessment failed:** {e}")
            st.stop()

    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESULTS — shared rendering with persona-aware section styling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if st.session_state.assessment_done and st.session_state.result:
    result        = st.session_state.result
    scores_data   = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall       = scores_data.get("overall", "N/A")

    st.markdown("---")
    hdr_class = "exec-section-header" if persona == "executive" else "section-header"
    st.markdown(f'<div class="{hdr_class}">📈 Domain Health Scores</div>',
                unsafe_allow_html=True)

    rating, desc = (
        interpret_score(int(overall)) if isinstance(overall, (int, float))
        else ("N/A", "")
    )
    col_ov, col_sp = st.columns([1, 3])
    with col_ov:
        st.markdown(f"""
        <div class="score-overall">
            <div style="font-size:3rem;font-weight:700">{overall}</div>
            <div style="font-size:1rem;opacity:0.85">Overall Score</div>
            <div style="font-size:0.9rem;margin-top:4px">{rating}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_sp:
        st.caption(
            f"Industry vertical: **{vertical_labels.get(vertical, vertical)}** "
            f"| Track: **{persona_cfg['title']}** | {desc}"
        )
        if domain_scores:
            for domain, score in domain_scores.items():
                r, _ = interpret_score(int(score))
                st.markdown(f"**{domain.capitalize()}** — {score}/100 &nbsp; `{r}`")
                st.progress(score / 100)

    # Section rendering map
    narrative = result.get("narrative", "")
    if narrative:
        SECTIONS = {
            "EXECUTIVE SUMMARY":           ("📋 Executive Summary",           "section-header",      "default"),
            "TOP RISKS":                   ("⚠️ Top Risks",                   "section-header",      "risk"),
            "DOMAIN HIGHLIGHTS":           ("🏷️ Domain Highlights",           "section-header",      "default"),
            "PRIORITY RECOMMENDATIONS":    ("✅ Priority Recommendations",    "section-header",      "rec"),
            "COST-BENEFIT ANALYSIS":       ("💰 Cost-Benefit Analysis",       "section-header",      "cba"),
            "STRATEGIC SCENARIO":          ("🔀 Strategic Scenario Comparison","exec-section-header", "scenario"),
            "SUPPLY CHAIN MATURITY":       ("📅 Supply Chain Maturity Roadmap","exec-section-header", "roadmap"),
        }

        current_section = None
        section_text    = {}
        for line in narrative.split("\n"):
            matched = False
            for key in SECTIONS:
                if key in line.upper():
                    current_section      = key
                    section_text[key]    = []
                    matched              = True
                    break
            if not matched and current_section:
                section_text[current_section].append(line)

        BOX_MAP = {
            "risk":     "risk-box",
            "rec":      "rec-box",
            "cba":      "cba-box",
            "scenario": "scenario-box",
            "roadmap":  "roadmap-box",
            "default":  None,
        }

        for key, (title, hdr_cls, box_style) in SECTIONS.items():
            if key in section_text:
                content = "\n".join(section_text[key]).strip()
                if content:
                    st.markdown(f'<div class="{hdr_cls}">{title}</div>',
                                unsafe_allow_html=True)
                    box_cls = BOX_MAP.get(box_style)
                    if box_cls:
                        st.markdown(
                            f'<div class="{box_cls}">'
                            f'{content.replace(chr(10), "<br>")}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(content)

    # ── Follow-up Q&A ──────────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown(f'<div class="{hdr_class}">💬 Follow-up Q&A</div>',
                unsafe_allow_html=True)

    if persona == "executive":
        st.caption(
            "Ask Claude to explore any scenario further, adjust assumptions, "
            "drill into a specific phase of the roadmap, or prepare a board presentation."
        )
        suggestions = [
            "Walk me through the recommended scenario in more detail",
            "What does Phase 1 look like in practice for our organisation?",
            "What's the cost of doing nothing for the next 12 months?",
            "Prepare a 5-bullet board summary of this assessment",
        ]
    else:
        st.caption(
            "Ask Claude anything about your results — drill into domains, "
            "get action plans, compare to specific benchmarks, and more."
        )
        suggestions = [
            "What are the top 3 actions for the next 90 days?",
            "How do we compare to world-class benchmarks?",
            "Give me a board-level summary in 3 bullet points",
            "Which domain has the highest ROI for improvement?",
        ]

    for msg in st.session_state.chat_history:
        tag = "chat-user" if msg["role"] == "user" else "chat-agent"
        icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{tag}">{icon} {msg["content"]}</div>',
                    unsafe_allow_html=True)

    st.markdown("**💡 Suggested questions:**")
    scols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with scols[i % 2]:
            if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                with st.spinner("Claude is thinking..."):
                    reply = st.session_state.agent.ask_followup(suggestion)
                st.session_state.chat_history.append(
                    {"role": "user", "content": suggestion}
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
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
    "<center><small>"
    "Built with ❤️ using the Anthropic Claude SDK · "
    "<a href='https://github.com/dwnjuguna/supply-chain-health-agent'>GitHub</a> · "
    "MIT License · "
    "<a href='https://www.anthropic.com/legal/privacy' target='_blank'>"
    "Anthropic Privacy Policy</a>"
    "</small></center>",
    unsafe_allow_html=True,
)
