import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent import SupplyChainHealthAgent
from scoring import interpret_score
from domains import DOMAINS
from verticals import VERTICAL_PRESETS
from personas import PERSONAS, EXECUTIVE_CONTEXT_QUESTIONS, EXECUTIVE_CUSTOMISATION_OPTIONS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Health Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1E1A4E 0%, #534AB7 100%);
        padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p  { color: #AFA9EC; margin: 0.5rem 0 0; font-size: 1rem; }
    .score-card {
        background: white; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 1rem; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .score-overall {
        background: linear-gradient(135deg, #534AB7, #0F6E56);
        color: white; border-radius: 12px; padding: 1.5rem; text-align: center;
    }
    .domain-pill {
        display: inline-block; background: #EEEDFE; color: #534AB7;
        border-radius: 20px; padding: 3px 12px; font-size: 0.8rem;
        margin: 2px; font-weight: 500;
    }
    .section-header {
        border-left: 4px solid #534AB7; padding-left: 0.75rem;
        margin: 1.5rem 0 0.75rem; font-weight: 600; color: #2C2C2A;
    }
    .risk-box {
        background: #FCEBEB; border-left: 4px solid #E24B4A;
        border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0;
    }
    .rec-box {
        background: #E1F5EE; border-left: 4px solid #0F6E56;
        border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin: 0.5rem 0;
    }
    .chat-user { background: #EEEDFE; border-radius: 12px 12px 4px 12px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.875rem; line-height: 1.6; }
    .chat-agent { background: #F1EFE8; border-radius: 12px 12px 12px 4px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.875rem; line-height: 1.6; }
    .chat-agent ul, .chat-user ul { margin: 4px 0 4px 16px; padding: 0; }
    .chat-agent li, .chat-user li { margin: 2px 0; }
    div[data-testid="stProgress"] > div { background: #534AB7 !important; }
    .persona-card {
        background: #FFFFFF; border: 2px solid #E5E7EB;
        border-radius: 16px; padding: 1.5rem 1.25rem 1.25rem;
        text-align: center; height: 270px; min-height: 270px;
        transition: border-color 0.15s, box-shadow 0.15s;
        overflow: hidden; box-sizing: border-box;
    }
    .persona-title {
        font-weight: 600; font-size: 0.88rem; color: #1A1A2E;
        margin-bottom: 8px; height: 36px;
        display: flex; align-items: center; justify-content: center;
    }
    .persona-desc {
        font-size: 0.77rem; color: #374151; line-height: 1.5;
        margin-bottom: 12px; height: 72px;
        display: flex; align-items: center; justify-content: center;
    }
    .persona-card:hover { border-color: #534AB7; box-shadow: 0 6px 24px rgba(83,74,183,0.12); }
    .persona-card.exec:hover { border-color: #0F6E56; box-shadow: 0 6px 24px rgba(15,110,86,0.12); }
    .persona-card.consultant:hover { border-color: #E8A020; box-shadow: 0 6px 24px rgba(232,160,32,0.12); }
    .persona-card.disabled { opacity: 0.4; pointer-events: none; }
    .persona-icon-wrap {
        width: 56px; height: 56px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 14px; font-size: 1.5rem;
    }
    .persona-badge {
        display: inline-block; border-radius: 20px; padding: 3px 12px;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.3px;
        color: #FFFFFF; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = None
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "assessment_done" not in st.session_state:
    st.session_state.assessment_done = False
if "persona" not in st.session_state:
    st.session_state.persona = None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 Supply Chain Health Agent</h1>
    <p>AI-powered end-to-end supply chain diagnostics · Powered by Anthropic Claude SDK</p>
</div>
""", unsafe_allow_html=True)

# ── PERSONA LANDING SCREEN ────────────────────────────────────────────────────
if st.session_state.persona is None:
    st.markdown("## Who are you?")
    st.markdown(
        "Select your profile — the tool tailors the entire experience "
        "to your needs, from inputs to outputs."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5, gap="large")

    with col1:
        st.markdown("""
        <div class="persona-card">
            <div class="persona-icon-wrap" style="background:#EEEDFE;">📊</div>
            <div class="persona-title">SC Manager / Analyst</div>
            <div class="persona-desc">Deep KPI diagnostics, benchmark comparisons,
                domain inputs, and cost-benefit analysis.</div>
            <span class="persona-badge" style="background:#534AB7;">Practitioner</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Select — Analyst", key="btn_analyst",
                     use_container_width=True, type="primary"):
            st.session_state.persona = "analyst"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="persona-card exec">
            <div class="persona-icon-wrap" style="background:#E1F5EE;">🏢</div>
            <div class="persona-title">CSCO / COO / VP SC</div>
            <div class="persona-desc">Strategic scenarios, maturity roadmap,
                and board-ready summaries for investment decisions.</div>
            <span class="persona-badge" style="background:#0F6E56;">Executive</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Select — Executive", key="btn_exec",
                     use_container_width=True, type="primary"):
            st.session_state.persona = "executive"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="persona-card consultant">
            <div class="persona-icon-wrap" style="background:#FEF3C7;">🎯</div>
            <div class="persona-title">SC Consultant</div>
            <div class="persona-desc">Multi-client diagnostics, white-label reports,
                and client intake forms for advisory practices.</div>
            <span class="persona-badge" style="background:#E8A020;">Consultant</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Select — Consultant", key="btn_consultant",
                     use_container_width=True, type="primary"):
            st.session_state.persona = "consultant"
            st.rerun()

    with col4:
        st.markdown("""
        <div class="persona-card disabled">
            <div class="persona-icon-wrap" style="background:#F1EFE8;">⚙️</div>
            <div class="persona-title">Enterprise Config</div>
            <div class="persona-desc">Embed with custom branding, SSO, API access,
                and compliance controls.</div>
            <span class="persona-badge" style="background:#9CA3AF;">Phase 2</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Coming Soon", key="btn_enterprise",
                  use_container_width=True, disabled=True)

    with col5:
        st.markdown("""
        <div class="persona-card disabled">
            <div class="persona-icon-wrap" style="background:#FEF2F2;">🏛️</div>
            <div class="persona-title">Government / Federal</div>
            <div class="persona-desc">FedRAMP, air-gap, GovCloud, and classified
                deployment for federal agencies.</div>
            <span class="persona-badge" style="background:#9CA3AF;">Phase 3</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Register Interest", key="btn_gov",
                  use_container_width=True, disabled=True)

    st.stop()

# ── PERSONA CONFIRMED — show Switch button in sidebar ─────────────────────────
persona = st.session_state.persona

# Domain pills
domains_html = "".join(f'<span class="domain-pill">{d["label"]}</span>' for d in DOMAINS)
st.markdown(domains_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Persona badge
    p_icon  = {"analyst": "📊", "executive": "🏢", "consultant": "🎯"}.get(persona, "📊")
    p_label = {"analyst": "Practitioner", "executive": "Executive", "consultant": "Consultant"}.get(persona, "Practitioner")
    p_color = {"analyst": "#534AB7", "executive": "#0F6E56", "consultant": "#E8A020"}.get(persona, "#534AB7")
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;'>"
        f"<span style='font-size:1.2rem;'>{p_icon}</span>"
        f"<span style='font-weight:600;font-size:0.9rem;'>{p_label} Track</span>"
        f"</div>"
        f"<span style='display:inline-block;background:{p_color};color:#fff;"
        f"font-size:0.65rem;font-weight:600;padding:2px 9px;border-radius:20px;"
        f"text-transform:uppercase;letter-spacing:0.4px;margin-bottom:12px;'>"
        f"{p_label}</span>",
        unsafe_allow_html=True,
    )
    if st.button("← Switch Profile", use_container_width=True):
        st.session_state.persona          = None
        st.session_state.agent            = None
        st.session_state.result           = None
        st.session_state.chat_history     = []
        st.session_state.assessment_done  = False
        st.rerun()
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")

    vertical_labels = {
        "general": "🏭 General",
        "semiconductor": "💾 Semiconductor",
        "automotive": "🚗 Automotive",
        "pharma": "💊 Pharmaceutical",
        "retail": "🛒 Retail & E-commerce",
        "cpg": "📦 Consumer Packaged Goods",
        "aerospace": "✈️ Aerospace & Defense",
        "healthcare": "🏥 Healthcare",
        "food_beverage": "🍔 Food & Beverage",
        "technology": "💻 Technology & Electronics",
        "apparel": "👗 Apparel & Fashion",
    }

    vertical_options = list(vertical_labels.keys())
    vertical = st.selectbox(
        "Industry Vertical",
        vertical_options,
        format_func=lambda x: vertical_labels[x],
        index=0
    )

    mode = st.radio(
        "Assessment Mode",
        ["general", "custom"],
        format_func=lambda x: "⚡ General (instant benchmark)" if x == "general" else "✏️ Custom (describe your org)"
    )

    st.markdown("---")
    st.markdown("### 📊 Score Guide")
    score_guide = [
        ("🟢 80–100", "Excellent — World-class"),
        ("🔵 60–79",  "Good — Above average"),
        ("🟡 40–59",  "Fair — Improvement needed"),
        ("🔴 0–39",   "At Risk — Urgent action"),
    ]
    for band, desc in score_guide:
        st.markdown(f"**{band}** {desc}")

    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("[GitHub Repo](https://github.com/dwnjuguna/supply-chain-health-agent)")
    st.markdown("[Anthropic Docs](https://docs.anthropic.com)")
    st.markdown("[SCOR Model](https://www.ascm.org/learning-development/scor/)")

# ── Custom inputs ─────────────────────────────────────────────────────────────
custom_inputs = {}
exec_customisation = {}
north_star = ""
sourcing_exposure = ""
sourcing_footprint = ""
if mode == "custom":
    # North Star vision — REWIRED framing question, shown for every persona
    st.markdown('<div class="section-header">🌟 Your North Star</div>', unsafe_allow_html=True)
    north_star = st.text_area(
        "What does supply chain excellence look like for your organization in 2 years?",
        placeholder="e.g. 'A resilient, AI-driven network: 98% OTIF, inventory turns up 30%, "
                    "full Tier-2 visibility, and nearshored critical components.'",
        height=80,
        key="north_star",
    )

    if persona == "executive":
        # Executive track — strategic, jargon-light context questions
        st.markdown('<div class="section-header">🏢 Strategic Context</div>', unsafe_allow_html=True)
        st.caption("Answer in plain language — these shape the strategic scenarios and maturity roadmap.")

        for q in EXECUTIVE_CONTEXT_QUESTIONS:
            val = st.text_area(
                q["label"],
                placeholder=q["placeholder"],
                height=q.get("height", 90),
                key=f"exec_{q['key']}",
            )
            if val.strip():
                custom_inputs[q["label"]] = val

        # Customisation preferences → flow into the executive prompt extension
        with st.expander("⚙️ Customise this assessment"):
            for ckey, cfg in EXECUTIVE_CUSTOMISATION_OPTIONS.items():
                default = cfg.get("default")
                idx = cfg["options"].index(default) if default in cfg["options"] else 0
                exec_customisation[ckey] = st.selectbox(
                    cfg["label"],
                    cfg["options"],
                    index=idx,
                    help=cfg.get("help"),
                    key=f"cust_{ckey}",
                )
    else:
        # Analyst / consultant track — granular per-domain inputs
        st.markdown('<div class="section-header">📝 Describe Your Supply Chain</div>', unsafe_allow_html=True)
        st.caption("Fill in as many domains as you can. Leave blank if not applicable — Claude will flag the gap.")

        col1, col2 = st.columns(2)
        for i, domain in enumerate(DOMAINS):
            with col1 if i % 2 == 0 else col2:
                val = st.text_area(
                    domain["label"],
                    placeholder=f"Describe your current {domain['label'].lower()} state, metrics, tools, and challenges...",
                    height=90,
                    key=f"input_{domain['key']}"
                )
                if val.strip():
                    custom_inputs[domain["label"]] = val

        # ── Geopolitical & sourcing footprint (informs Risk & Procurement scoring) ──
        st.markdown('<div class="section-header">🌍 Geopolitical & Sourcing Footprint</div>', unsafe_allow_html=True)
        st.caption("2026 supply chains live or die on sourcing resilience — these feed the Risk and Procurement scores.")
        sourcing_exposure = st.text_area(
            "What is your primary sourcing geography, and what is your exposure to "
            "China-origin inputs or rare earth materials?",
            placeholder="e.g. 'Primary sourcing from China and SE Asia; ~40% of components "
                        "China-origin; two critical magnets depend on rare earths with no "
                        "qualified alternative source.'",
            height=90,
            key="sourcing_exposure",
        )
        sourcing_footprint = st.text_area(
            "What is your current sourcing footprint strategy — offshore, nearshoring "
            "in progress, or reshoring?",
            placeholder="e.g. 'Predominantly offshore today; nearshoring to Mexico in "
                        "progress for two product lines; evaluating reshoring of critical "
                        "components but the cost gap is significant.'",
            height=90,
            key="sourcing_footprint",
        )

# ── Run assessment ─────────────────────────────────────────────────────────────
col_btn1, col_btn2, _ = st.columns([1, 1, 4])
with col_btn1:
    run_clicked = st.button("🚀 Run Assessment", type="primary", use_container_width=True)
with col_btn2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.agent = None
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.assessment_done = False
        st.rerun()

if run_clicked:
    active_persona = st.session_state.persona or "analyst"
    st.session_state.agent = SupplyChainHealthAgent(
        vertical=vertical,
        persona=active_persona,
        include_cba=(active_persona in ("analyst", "consultant")),
        enable_web_search=True,
        customisation=exec_customisation,
        north_star=north_star,
        sourcing_exposure=sourcing_exposure,
        sourcing_footprint=sourcing_footprint,
    )
    st.session_state.chat_history = []
    st.session_state.assessment_done = False

    # ── Multi-step loading experience ─────────────────────────────────────────
    progress_bar     = st.progress(0)
    status_container = st.empty()

    def update_status(message: str, pct: int):
        progress_bar.progress(pct)
        status_container.markdown(
            f'<div style="background:#EEF0FF;border:1px solid #CECBF6;border-radius:10px;padding:0.75rem 1rem;font-size:0.875rem;color:#1A1A2E;">{message}</div>',
            unsafe_allow_html=True,
        )

    update_status("🔍 Initializing assessment engine...", 5)
    import time; time.sleep(0.4)

    update_status("🌐 Searching for latest industry benchmarks and market data...", 20)
    import time; time.sleep(0.3)

    update_status(f"🏭 Analyzing supply chain health for {vertical.upper()} vertical...", 40)

    try:
        if mode == "custom" and custom_inputs:
            result = st.session_state.agent.run_custom_assessment(custom_inputs)
        else:
            result = st.session_state.agent.run_general_assessment()
    except Exception as e:
        progress_bar.empty()
        status_container.empty()
        st.error(f"**Assessment failed:** {e}")
        st.stop()

    update_status("📊 Scoring domains against world-class benchmarks...", 70)
    import time; time.sleep(0.3)

    update_status("✍️ Generating executive summary and recommendations...", 85)
    import time; time.sleep(0.3)

    update_status("📄 Preparing your report...", 95)
    import time; time.sleep(0.2)

    progress_bar.progress(100)
    status_container.empty()
    progress_bar.empty()

    st.session_state.result = result
    st.session_state.assessment_done = True
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.assessment_done and st.session_state.result:
    result = st.session_state.result
    scores_data = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall = scores_data.get("overall", "N/A")

    st.markdown("---")

    # ── Overall score header (always visible above tabs) ───────────────────────
    rating, desc = interpret_score(int(overall)) if isinstance(overall, (int, float)) else ("N/A", "")
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
        st.caption(f"Industry vertical: **{vertical_labels.get(vertical, vertical)}** | {desc}")
        if domain_scores:
            for domain, score in domain_scores.items():
                r, _ = interpret_score(int(score))
                color = "#1D9E75" if score >= 80 else "#3B8BD4" if score >= 60 else "#BA7517" if score >= 40 else "#E24B4A"
                st.markdown(f'**{domain.capitalize()}** — {score}/100 &nbsp; <span style="color:{color};font-weight:600;font-size:0.8rem;">{r}</span>', unsafe_allow_html=True)
                st.progress(score / 100)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Diagnostic Report",
        "🏷️ Domain Deep-Dive",
        "📥 Export",
        "💬 Q&A",
    ])

    # ── TAB 1: Diagnostic Report ───────────────────────────────────────────────
    with tab1:
        narrative = result.get("narrative", "")
        if narrative:
            sections = {
                "EXECUTIVE SUMMARY":        ("📋 Executive Summary",         "info"),
                "TOP RISKS":                ("⚠️ Top Risks",                  "error"),
                "PRIORITY RECOMMENDATIONS": ("✅ Priority Recommendations",   "success"),
            }

            current_section = None
            section_text = {}
            for line in narrative.split("\n"):
                matched = False
                for key in sections:
                    if key in line.upper():
                        current_section = key
                        section_text[key] = []
                        matched = True
                        break
                if not matched and current_section:
                    section_text[current_section].append(line)

            def render_markdown_content(text: str) -> str:
                import re
                # Process line by line for reliable rendering
                lines = text.split(chr(10))
                html_lines = []
                for line in lines:
                    # Fix broken strong> tag — simple replace catches ALL cases
                    line = line.replace("strong>", "<strong>")
                    line = line.replace("<<strong>", "<strong>")  # fix << if over-replaced
                    line = line.replace("<strong><strong>", "<strong>")  # fix duplicates
                    # Bold **text**
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    # Italic *text*
                    line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', line)
                    stripped = line.strip()
                    if not stripped:
                        html_lines.append("<br>")
                    elif re.match(r'^[-•]\s', stripped):
                        html_lines.append("&nbsp;&nbsp;• " + stripped[2:])
                    elif re.match(r'^\d+\.\s', stripped):
                        html_lines.append("&nbsp;&nbsp;" + stripped)
                    else:
                        html_lines.append(stripped)
                result = "<br>".join(html_lines)
                result = re.sub(r'(<br>){3,}', '<br><br>', result)
                # Final safety net for any remaining broken tags
                result = re.sub(r'(?:^|(?<=[^<\/a-z]))strong>', '<strong>', result)
                return result.strip("<br>")

            for key, (title, _) in sections.items():
                if key in section_text:
                    content = "\n".join(section_text[key]).strip()
                    if content:
                        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
                        rendered = render_markdown_content(content)
                        if key == "TOP RISKS":
                            st.markdown(f'<div class="risk-box">{rendered}</div>', unsafe_allow_html=True)
                        elif key == "PRIORITY RECOMMENDATIONS":
                            st.markdown(f'<div class="rec-box">{rendered}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(content)
        else:
            st.info("Run an assessment to see the diagnostic report.")

    # ── TAB 2: Domain Deep-Dive ────────────────────────────────────────────────
    with tab2:
        narrative = result.get("narrative", "")
        if narrative:
            # Extract ONLY the Domain Highlights section — stop at next section
            STOP_MARKERS = [
                "PRIORITY RECOMMENDATIONS", "COST-BENEFIT",
                "STRATEGIC SCENARIO", "MATURITY ROADMAP"
            ]
            in_domain = False
            domain_lines = []
            for line in narrative.split("\n"):
                if "DOMAIN HIGHLIGHTS" in line.upper():
                    in_domain = True
                    continue
                if in_domain:
                    if any(m in line.upper() for m in STOP_MARKERS):
                        break
                    domain_lines.append(line)

            if domain_lines:
                domain_content = "\n".join(domain_lines).strip()
                import re
                # Fix broken strong> tags
                domain_content = re.sub(r'(?<![<\/a-z])strong>', '<strong>', domain_content)
                # Bold
                domain_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', domain_content)
                # Add paragraph breaks between domain entries
                # Pattern 1: **Any Title (Score: XX - Rating)**
                domain_content = re.sub(
                    r'\*\*([^*]+?\((?:Score:\s*)?\d+(?:\/100)?[^)]*\))\*\*',
                    r'<br><br><strong>\1</strong>',
                    domain_content
                )
                # Add paragraph breaks before known domain section headers
                # Simple line-by-line approach — no complex regex
                DOMAIN_KEYWORDS = [
                    "Demand", "Procurement", "Sourcing", "Manufacturing",
                    "Production", "Inventory", "Logistics", "Transportation",
                    "Warehousing", "Fulfillment", "Risk", "Resilience",
                    "Sustainability", "ESG"
                ]
                processed_lines = []
                for line in domain_content.split(chr(10)):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    # Check if line starts with a known domain keyword and contains a score
                    is_header = (
                        any(stripped.startswith(kw) for kw in DOMAIN_KEYWORDS)
                        and ("/" in stripped or "Score" in stripped or "/100" in stripped
                             or any(f"({n}" in stripped for n in range(0,101)))
                    )
                    if is_header:
                        processed_lines.append(f'<br><br><strong>{stripped}</strong><br>')
                    elif stripped.startswith(("•", "-", "*")):
                        processed_lines.append(f'&nbsp;&nbsp;• {stripped[2:].strip()}<br>')
                    else:
                        processed_lines.append(f'{stripped}<br>')
                domain_content = "".join(processed_lines)
                # Line breaks
                domain_content = domain_content.replace(chr(10), "<br>")
                domain_content = re.sub(r'(<br>){3,}', '<br><br>', domain_content)
                st.markdown('<div class="section-header">🏷️ Domain Highlights</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.9rem;line-height:1.7;color:#1A1A2E;">{domain_content}</div>',
                    unsafe_allow_html=True
                )

            # Domain score cards — 2 column grid
            st.markdown('<div class="section-header">📊 Domain Score Cards</div>', unsafe_allow_html=True)
            if domain_scores:
                col_a, col_b = st.columns(2)
                for i, (domain, score) in enumerate(domain_scores.items()):
                    score  = max(0, min(100, int(score)))
                    r, desc_d = interpret_score(score)
                    color  = "#1D9E75" if score >= 80 else "#3B8BD4" if score >= 60 else "#BA7517" if score >= 40 else "#E24B4A"
                    bg     = "#F0FDF4" if score >= 80 else "#EFF6FF" if score >= 60 else "#FFFBEB" if score >= 40 else "#FEF2F2"
                    filled = round(score / 5)
                    bar    = "█" * filled + "░" * (20 - filled)
                    with col_a if i % 2 == 0 else col_b:
                        st.markdown(f"""
                        <div style="background:{bg};border:1px solid #E5E7EB;
                        border-left:5px solid {color};border-radius:10px;
                        padding:1.1rem 1rem;margin:0.4rem 0;">
                            <div style="font-weight:700;font-size:0.95rem;
                            color:#1A1A2E;margin-bottom:4px;">
                                {domain.replace("_"," ").title()}
                            </div>
                            <div style="font-size:2rem;font-weight:800;
                            color:{color};line-height:1;">{score}
                                <span style="font-size:0.9rem;font-weight:400;
                                color:#6B7280;">/100</span>
                            </div>
                            <div style="font-size:0.72rem;color:{color};
                            font-weight:600;margin:4px 0;">{r}</div>
                            <div style="font-family:monospace;font-size:0.65rem;
                            color:{color};letter-spacing:1px;">{bar}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Run an assessment to see domain highlights.")

    # ── TAB 3: Export ──────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">📥 Download Report</div>', unsafe_allow_html=True)
        st.caption("Download your full assessment as a professional PDF report.")
        try:
            from export import generate_pdf
            vertical_val = vertical if "vertical" in dir() else "general"
            persona_val  = st.session_state.agent.persona if st.session_state.agent else "analyst"
            pdf_bytes = generate_pdf(
                result,
                vertical=vertical_val,
                persona=persona_val,
            )
            from datetime import datetime
            filename = f"supply_chain_report_{vertical_val}_{datetime.now().strftime('%Y%m%d')}.pdf"
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "💡 Your PDF includes the overall score, all domain scores, "
                "executive summary, top risks, domain highlights, and priority "
                "recommendations — ready to share with your team or board."
            )
        except Exception as e:
            st.warning(f"PDF export unavailable: {e}")

    # ── TAB 4: Q&A ────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">💬 Follow-up Q&A</div>', unsafe_allow_html=True)
        st.caption("Ask Claude anything about your results — drill into any domain, get board summaries, action plans, and more.")

        def render_chat_markdown(text: str) -> str:
            """Convert markdown to HTML for chat bubbles."""
            import re
            lines = text.split(chr(10))
            html_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    html_lines.append("<br>")
                    continue
                stripped = re.sub(r'#{2,3}\s+(.+)', r'<strong>\1</strong>', stripped)
                stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                stripped = re.sub(r'(?<![<])strong>', r'<strong>', stripped)
                stripped = re.sub(r'(?<![<\/])strong>', r'<strong>', stripped)
                stripped = re.sub(r'(?<![\*])\*(?![\*])(.+?)(?<![\*])\*(?![\*])', r'<em>\1</em>', stripped)
                if re.match(r'^\s{2,}[-•]\s', line):
                    stripped = "&nbsp;&nbsp;&nbsp;&nbsp;◦ " + re.sub(r'^\s*[-•]\s', '', stripped)
                elif re.match(r'^[-•]\s', stripped):
                    stripped = "&nbsp;&nbsp;• " + stripped[2:]
                elif re.match(r'^\d+\.\s', stripped):
                    stripped = "&nbsp;&nbsp;" + stripped
                html_lines.append(stripped)
            result = "<br>".join(html_lines)
            result = re.sub(r'(<br>){3,}', '<br><br>', result)
            result = re.sub(r'(?<![<\/a-z])strong>', '<strong>', result)
            return result.strip("<br>")

        for msg in st.session_state.chat_history:
            rendered = render_chat_markdown(msg["content"])
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user">🧑&nbsp; {rendered}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-agent">🤖&nbsp; {rendered}</div>',
                    unsafe_allow_html=True
                )

        suggestions = [
            "What are the top 3 actions for the next 90 days?",
            "How do we compare to world-class benchmarks?",
            "Give me a board-level summary in 3 bullet points",
            "Which domain has the highest ROI for improvement?",
        ]
        st.markdown("**💡 Suggested questions:**")
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                    with st.spinner(f"🤖 Analyzing: {suggestion[:40]}..."):
                        reply = st.session_state.agent.ask_followup(
                            suggestion,
                            history=st.session_state.chat_history,
                            assessment_context=st.session_state.result.get("narrative", "") if st.session_state.result else None,
                        )
                    st.session_state.chat_history.append({"role": "user", "content": suggestion})
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

        user_q = st.chat_input("Ask a follow-up question about your supply chain health...")
        if user_q:
            with st.spinner("🤖 Claude is researching your question..."):
                reply = st.session_state.agent.ask_followup(
                    user_q,
                    history=st.session_state.chat_history,
                    assessment_context=st.session_state.result.get("narrative", "") if st.session_state.result else None,
                )
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>Built with ❤️ using the Anthropic Claude SDK · "
    "<a href='https://github.com/dwnjuguna/supply-chain-health-agent'>GitHub</a> · MIT License</small></center>",
    unsafe_allow_html=True
)
