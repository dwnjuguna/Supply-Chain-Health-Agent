import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent import SupplyChainHealthAgent
from scoring import interpret_score
from domains import DOMAINS
from verticals import VERTICAL_PRESETS

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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 Supply Chain Health Agent</h1>
    <p>AI-powered end-to-end supply chain diagnostics · Powered by Anthropic Claude SDK</p>
</div>
""", unsafe_allow_html=True)

# Domain pills
domains_html = "".join(f'<span class="domain-pill">{d["label"]}</span>' for d in DOMAINS)
st.markdown(domains_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
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
if mode == "custom":
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
    st.session_state.agent = SupplyChainHealthAgent(
        vertical=vertical,
        persona="analyst",
        include_cba=False,
        enable_web_search=True,
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
                st.markdown(f"**{domain.capitalize()}** — {score}/100 &nbsp; `{r}`")
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
                # Fix broken strong> tags from web search citations
                text = re.sub(r'(?<![<\/a-z])strong>', '<strong>', text)
                # Bold
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                # Italic
                text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
                # Numbered list items
                text = re.sub(r'^(\d+\.\s)', r'<br>\1', text, flags=re.MULTILINE)
                # Bullet points
                text = re.sub(r'^[-•]\s', r'<br>• ', text, flags=re.MULTILINE)
                # Line breaks
                text = text.replace(chr(10), "<br>")
                # Clean up excessive breaks
                text = re.sub(r'(<br>){3,}', '<br><br>', text)
                # Final strong tag cleanup
                text = re.sub(r'(?<![<\/a-z])strong>', '<strong>', text)
                return text.strip("<br>")

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
