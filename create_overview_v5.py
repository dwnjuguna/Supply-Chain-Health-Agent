"""
SC Health Agent — Product Overview PDF v5.0
Clean, professional, design-first rebuild.
No emoji dependencies — pure typography and color.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# ── Fonts ─────────────────────────────────────────────────────────────────────
try:
    pdfmetrics.registerFont(TTFont("AU", "/Library/Fonts/Arial Unicode.ttf"))
    BODY = "AU"
except:
    BODY = "Helvetica"
BOLD = "Helvetica-Bold"

# ── Brand palette ─────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#1E1A4E")
PURPLE  = colors.HexColor("#534AB7")
TEAL    = colors.HexColor("#0F6E56")
AMBER   = colors.HexColor("#D97706")
BLUE    = colors.HexColor("#2563EB")
RED     = colors.HexColor("#DC2626")
SLATE   = colors.HexColor("#374151")
LGRAY   = colors.HexColor("#F8F9FA")
MGRAY   = colors.HexColor("#E5E7EB")
DGRAY   = colors.HexColor("#6B7280")
WHITE   = colors.white
LPURPLE = colors.HexColor("#EEF2FF")
LTEAL   = colors.HexColor("#ECFDF5")
LAMBER  = colors.HexColor("#FFFBEB")
LRED    = colors.HexColor("#FEF2F2")

now = datetime.now().strftime("%B %d, %Y")
W = 7.0 * inch  # usable width

doc = SimpleDocTemplate(
    "SC_Health_Agent_Overview_v4_2.pdf",
    pagesize=letter,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.55*inch,  bottomMargin=0.55*inch,
)
story = []

# ── Style helpers ─────────────────────────────────────────────────────────────
def ps(size=9, bold=False, color=SLATE, align=TA_LEFT, leading=None, indent=0):
    return ParagraphStyle("x",
        fontName=BOLD if bold else BODY,
        fontSize=size, textColor=color,
        leading=leading or size*1.45,
        alignment=align, leftIndent=indent,
        spaceAfter=0)

def rule(c=PURPLE, thick=1.5, before=10, after=8):
    story.append(Spacer(1, before))
    story.append(HRFlowable(width="100%", thickness=thick,
        color=c, spaceAfter=after))

def section(title, color=NAVY):
    story.append(Spacer(1, 12))
    t = Table([[
        Paragraph(
            f'<font color="#AFA9EC">|</font>  {title}',
            ps(11, bold=True, color=WHITE)),
    ]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), color),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 7))

def tbl(data, widths, extras=None, row_bg=True):
    base = [
        ("FONTNAME",      (0,0),  (-1,0),  BOLD),
        ("FONTNAME",      (0,1),  (-1,-1), BODY),
        ("FONTSIZE",      (0,0),  (-1,-1), 8.5),
        ("TOPPADDING",    (0,0),  (-1,-1), 6),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 6),
        ("LEFTPADDING",   (0,0),  (-1,-1), 9),
        ("RIGHTPADDING",  (0,0),  (-1,-1), 9),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("LINEBELOW",     (0,0),  (-1,0),  0.8, PURPLE),
        ("LINEBELOW",     (0,1),  (-1,-1), 0.3, MGRAY),
        ("TEXTCOLOR",     (0,0),  (-1,0),  NAVY),
    ]
    if row_bg:
        base.append(("ROWBACKGROUNDS", (0,1), (-1,-1),
            [WHITE, LGRAY]))
    if extras:
        base.extend(extras)
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle(base))
    story.append(t)
    story.append(Spacer(1, 10))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE 1 — COVER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Cover block
cover = Table([[
    Paragraph("SUPPLY CHAIN HEALTH AGENT",
        ps(22, bold=True, color=WHITE, align=TA_LEFT)),
],[
    Paragraph("v4.2  —  Product Overview",
        ps(13, color=colors.HexColor("#AFA9EC"), align=TA_LEFT)),
],[
    Spacer(1, 8),
],[
    Paragraph(
        "AI-powered end-to-end supply chain diagnostics  ·  "
        "Powered by Anthropic Claude SDK",
        ps(9.5, color=colors.HexColor("#C7C3EC"), align=TA_LEFT)),
],[
    Paragraph(
        "MCP Server  ·  Browser-based  ·  No login required  ·  "
        "supply-chain-health-agent.streamlit.app",
        ps(9, color=colors.HexColor("#9B97D4"), align=TA_LEFT)),
],[
    Spacer(1, 4),
],[
    Paragraph(f"June 2026  ·  MIT License  ·  Open Source",
        ps(8, color=colors.HexColor("#7C78C4"), align=TA_LEFT)),
]], colWidths=[W])
cover.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), NAVY),
    ("TOPPADDING",    (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 28),
    ("RIGHTPADDING",  (0,0), (-1,-1), 28),
    ("TOPPADDING",    (0,0), (0,0),   28),
    ("BOTTOMPADDING", (0,-1),(0,-1),  24),
]))
story.append(cover)
story.append(Spacer(1, 0.15*inch))

# Stats bar — large number + small label, equal columns
stat_style_num = ps(18, bold=True, align=TA_CENTER, color=NAVY)
stat_style_lbl = ps(7.5, align=TA_CENTER, color=DGRAY)

def stat(num, lbl, accent):
    return Table([[
        Paragraph(num, ps(18, bold=True, align=TA_CENTER, color=accent)),
    ],[
        Paragraph(lbl, ps(7.5, align=TA_CENTER, color=DGRAY)),
    ]], colWidths=[W/6])

stats_cells = [
    stat("60s",   "Time to Assessment",  PURPLE),
    stat("8",     "SCOR Domains",        TEAL),
    stat("11",    "Industry Verticals",  AMBER),
    stat("5",     "User Personas",       BLUE),
    stat("MCP",   "AI-Native Access",    BLUE),
    stat("Free",  "Open Source MIT",     TEAL),
]

stats_row = Table([stats_cells], colWidths=[W/6]*6)
stats_row.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), LGRAY),
    ("TOPPADDING",    (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ("LINEBEFORE",    (1,0), (-1,-1), 0.5, MGRAY),
    ("BOX",           (0,0), (-1,-1), 0.5, MGRAY),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
]))
story.append(stats_row)
story.append(Spacer(1, 0.18*inch))

# Problem section
section("The Problem")
story.append(Paragraph(
    "Supply chain failures cost the average enterprise <b>$100M–$300M annually</b> — "
    "yet diagnosis still takes 8–12 weeks and $150K–$500K in consulting fees. "
    "The Supply Chain Health Agent delivers in 60 seconds what traditionally takes "
    "12 weeks — browser-based, no technical setup required.",
    ps(9.5, color=SLATE)))
story.append(Spacer(1, 10))

tbl([
    ["Alternative",           "Cost",          "Time to Insight", "Live Data", "Always On"],
    ["McKinsey / Big 4",      "$150K–$500K",   "8–12 weeks",      "No",        "No"],
    ["Gartner Membership",    "$25K–$60K/yr",  "Weeks",           "No",        "No"],
    ["Internal Team",         "$30K–$80K",     "4–8 weeks",       "No",        "No"],
    ["ASCM Free Tool",        "$0",            "1 hour",          "No",        "No"],
    ["SC Health Agent",       "See tiers",     "60 seconds",      "Yes",       "Yes"],
], widths=[2.1*inch, 1.3*inch, 1.3*inch, 1.0*inch, 1.3*inch],
extras=[
    ("FONTNAME",    (0,-1), (-1,-1), BOLD),
    ("TEXTCOLOR",   (0,-1), (-1,-1), TEAL),
    ("BACKGROUND",  (0,-1), (-1,-1), LTEAL),
    ("LINEABOVE",   (0,-1), (-1,-1), 1.0, TEAL),
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE 2 — WHAT IT DOES + PERSONAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(PageBreak())

section("What It Does")
story.append(Paragraph(
    "Evaluates your supply chain across 8 SCOR-aligned domains, benchmarks performance "
    "against 2026 world-class standards, autonomously searches for live market intelligence, "
    "and delivers a prioritised assessment with actionable recommendations — all in under 60 seconds.",
    ps(9.5, color=SLATE)))
story.append(Spacer(1, 10))

tbl([
    ["Capability",              "What It Does"],
    ["Instant Diagnostics",     "Scores 8 domains 0–100 vs 2026 Gartner and SCOR benchmarks"],
    ["Live Market Intelligence","Autonomously searches for freight rates, regulatory updates, geopolitical risks"],
    ["Auto Action Pack",        "Generates board summary, 90-day plan and risk watch list automatically"],
    ["Context-Aware Q&A",       "Follow-up answers reference your specific scores — not generic advice"],
    ["Professional PDF Export", "Multi-page report with scores, narrative, and recommendations — board-ready"],
    ["Phase 2 Risk Alerts",     "Proactive risk monitoring via Claude + web search, delivered to Slack and email"],
], widths=[2.0*inch, 5.0*inch],
extras=[
    ("BACKGROUND", (0,0), (-1,0), LPURPLE),
    ("TEXTCOLOR",  (0,0), (-1,0), PURPLE),
])

section("Five User Personas")

personas = [
    ("SC MANAGER / ANALYST",  "Practitioner Track  —  Live Now",   PURPLE, LPURPLE,
     "Deep KPI diagnostics across all 8 SCOR domains. Custom assessment mode — describe "
     "your org, get tailored scores. Benchmark gaps vs 2026 Gartner Top 25. "
     "Cost-benefit analysis with your real financial figures. Follow-up Q&amp;A with live web search."),
    ("CSCO / COO / VP SC",    "Executive Track  —  Live Now",       TEAL,   LTEAL,
     "Strategic scenario comparison — 3 named paths with trade-offs, investment ranges, "
     "and KPI targets. 36-month phased maturity roadmap. Board-ready language throughout. "
     "Customisable orientation: growth-first vs cost-out vs balanced."),
    ("SC CONSULTANT",         "Consultant Track  —  Live Now",      AMBER,  LAMBER,
     "Multi-client diagnostics across all 11 verticals. White-label PDF reports with "
     "client branding. Client intake forms — shareable pre-assessment questionnaires. "
     "Side-by-side client comparison and benchmarking."),
    ("ENTERPRISE IT / CONFIG","Enterprise Track  —  Phase 2",
     colors.HexColor("#6B7280"), colors.HexColor("#F3F4F6"),
     "SSO / SAML authentication. API access and webhook integrations. Custom vertical "
     "definitions and branded outputs. Audit logs, admin panel, SLA guarantee. "
     "On-premise deployment option."),
    ("GOVERNMENT / FEDERAL",  "Federal Track  —  Phase 3",         RED,    LRED,
     "Air-gapped and GovCloud AWS deployment. FedRAMP authorization pathway. "
     "ITAR controls and FIPS 140-2 compliance. Classified mode with dedicated "
     "infrastructure. Federal SI partner model."),
]

for name, track, accent, bg, desc in personas:
    row = Table([[
        Paragraph(f'<b>{name}</b>',  ps(9, bold=True, color=accent)),
        Paragraph(track, ps(7.5, color=DGRAY, align=TA_RIGHT)),
    ],[
        Paragraph(desc, ps(8.5, color=SLATE)),
        Paragraph("", ps(8)),
    ]], colWidths=[4.5*inch, 2.5*inch])
    row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("LINEABOVE",     (0,0), (-1,0),  2.5, accent),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("SPAN",          (0,1), (-1,1)),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.3, MGRAY),
    ]))
    story.append(KeepTogether([row, Spacer(1, 3)]))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE 3 — DOMAINS + VERTICALS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(PageBreak())

section("8 Health Domains Assessed")

# Score band legend
story.append(Paragraph(
    '<font color="#0F6E56"><b>80–100 Excellent</b></font>  &nbsp;&nbsp;'
    '<font color="#2563EB"><b>60–79 Good</b></font>  &nbsp;&nbsp;'
    '<font color="#D97706"><b>40–59 Fair</b></font>  &nbsp;&nbsp;'
    '<font color="#DC2626"><b>0–39 At Risk</b></font>',
    ps(9, color=SLATE)))
story.append(Spacer(1, 10))

tbl([
    ["Domain",                         "Key KPIs",                                  "World-Class Target"],
    ["Demand Planning & Forecasting",  "Forecast accuracy, MAPE, S&OP maturity",    "FA 85–90%+, MAPE <10%"],
    ["Procurement & Sourcing",         "Supplier OTD, spend under management, PPM", "OTD 95%+, <500 PPM"],
    ["Manufacturing & Production",     "OEE, first-pass yield, schedule adherence", "OEE 85%+, FPY 98%+"],
    ["Inventory Management",           "Turns, stockout rate, E&O%, cash-to-cash",  "8–12x turns, <1% stockout"],
    ["Logistics & Transportation",     "OTIF, freight cost %, perfect order rate",  "OTIF 95–98%"],
    ["Warehousing & Fulfillment",      "Order accuracy, utilisation, lines/hour",   "Accuracy 99.9%+"],
    ["Risk & Resilience",              "BCP coverage, TTR, supplier risk tiers",    "BCP 95%+ critical nodes"],
    ["Sustainability & ESG",           "Scope 3 tracking, ESG audit coverage",      "Scope 3 80%+ tracked"],
], widths=[2.1*inch, 2.9*inch, 2.0*inch],
extras=[
    ("BACKGROUND", (0,0), (-1,0), LPURPLE),
    ("TEXTCOLOR",  (0,0), (-1,0), PURPLE),
])

section("11 Industry Verticals")
tbl([
    ["Vertical",                   "Focus Areas",                                    "Reference Orgs"],
    ["General Manufacturing",      "Standard SCOR + Gartner benchmarks",             "Gartner Top 25"],
    ["Semiconductor",              "Fab utilisation, CHIPS Act, rare earth risk",    "TSMC, Intel, NVIDIA"],
    ["Automotive",                 "JIT/JIS delivery, EV transition readiness",      "Toyota, BMW, Tesla"],
    ["Pharmaceutical",             "Cold chain, GDP compliance, DSCSA",              "Pfizer, Roche, J&J"],
    ["Retail & E-commerce",        "OTIF, last-mile, omnichannel, seasonal peaks",   "Amazon, Walmart, Zara"],
    ["Consumer Packaged Goods",    "Case fill rate, trade promotion, ESG",           "P&G, Unilever, Nestlé"],
    ["Aerospace & Defense",        "AS9100D, long-lead parts, ITAR/EAR controls",   "Boeing, Airbus, Lockheed"],
    ["Healthcare",                 "UDI traceability, sterile supply chain, GPO",   "Medtronic, Stryker, BD"],
    ["Food & Beverage",            "FSMA compliance, cold chain, shelf-life",        "Nestlé, Coca-Cola, Tyson"],
    ["Technology & Electronics",   "Short lifecycles, component obsolescence, NPI", "Apple, Samsung, Dell"],
    ["Apparel & Fashion",          "Seasonal cycles, fast fashion, EPR compliance", "Zara, Nike, H&M"],
], widths=[1.8*inch, 3.1*inch, 2.1*inch],
extras=[
    ("BACKGROUND", (0,0), (-1,0), LPURPLE),
    ("TEXTCOLOR",  (0,0), (-1,0), PURPLE),
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE 4 — PHASE 2 + TIER TABLE + GETTING STARTED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(PageBreak())

section("Phase 2 — Enterprise Infrastructure  (Built & Ready)")
story.append(Paragraph(
    "Phase 2 infrastructure is fully built and ready for activation. "
    "Available to self-hosters today — unlocked on the hosted service by tier.",
    ps(9.5, color=SLATE)))
story.append(Spacer(1, 8))

tbl([
    ["Capability",             "What It Does",                                          "Tier"],
    ["Cross-Session Memory",   "SQLite engine — tracks org profiles, scores, KPI trends over time", "Pro+"],
    ["Proactive Risk Alerts",  "Claude + web search scans for live risks before you ask",           "Pro+"],
    ["Slack Integration",      "Push assessments, action plans, risk alerts to channels",           "Pro+"],
    ["Email Dispatcher",       "Branded HTML email reports with domain scores and risk alerts",     "Pro+"],
    ["Jira Integration",       "Create tickets from 90-day action plan automatically",             "Team+"],
    ["Feature Flags",          "60+ features gated across 6 tiers without pricing in code",        "All"],
], widths=[1.8*inch, 4.0*inch, 1.2*inch],
extras=[
    ("BACKGROUND", (0,0), (-1,0), LPURPLE),
    ("TEXTCOLOR",  (0,0), (-1,0), PURPLE),
])

section("Open Source vs Hosted Tiers")
story.append(Paragraph(
    "The code is MIT — free forever. "
    "The hosted service is where advanced features live.",
    ps(9.5, color=SLATE)))
story.append(Spacer(1, 8))

def tier_yes():
    return Paragraph("Yes", ps(8, bold=True, color=TEAL, align=TA_CENTER))
def tier_no():
    return Paragraph("—", ps(8, color=DGRAY, align=TA_CENTER))
def tier_lock():
    return Paragraph("Pro+", ps(8, bold=True, color=PURPLE, align=TA_CENTER))
def tier_team():
    return Paragraph("Team+", ps(8, bold=True, color=BLUE, align=TA_CENTER))
def tier_ent():
    return Paragraph("Ent+", ps(8, bold=True, color=AMBER, align=TA_CENTER))
def tier_gov():
    return Paragraph("Gov", ps(8, bold=True, color=RED, align=TA_CENTER))
def tier_self():
    return Paragraph("Self", ps(8, color=DGRAY, align=TA_CENTER))
def tier_txt(t):
    return Paragraph(t, ps(8, color=DGRAY, align=TA_CENTER))

def hdr(t):
    return Paragraph(t, ps(8, bold=True, color=NAVY, align=TA_CENTER))

tier_tbl = Table([
    [Paragraph("Feature", ps(8, bold=True, color=NAVY)),
     hdr("Open\nSource"), hdr("Hosted\nFree"),
     hdr("Pro"),  hdr("Team"), hdr("Ent."), hdr("Gov")],
    [Paragraph("Core assessment (8 domains)", ps(8, color=SLATE)),
     tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes()],
    [Paragraph("All 11 verticals",            ps(8, color=SLATE)),
     tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes()],
    [Paragraph("PDF export",                  ps(8, color=SLATE)),
     tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes()],
    [Paragraph("Assessments / month",         ps(8, color=SLATE)),
     tier_txt("Unlimited"), tier_txt("3/mo"),
     tier_txt("Unltd."), tier_txt("Unltd."),
     tier_txt("Unltd."), tier_txt("Unltd.")],
    [Paragraph("Cross-session memory",        ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_lock(), tier_lock(), tier_lock(), tier_lock()],
    [Paragraph("Proactive risk alerts",       ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_lock(), tier_lock(), tier_lock(), tier_lock()],
    [Paragraph("Slack + Email delivery",      ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_lock(), tier_lock(), tier_lock(), tier_lock()],
    [Paragraph("Jira integration",            ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_no(), tier_team(), tier_team(), tier_team()],
    [Paragraph("MCP server access",           ps(8, color=SLATE)),
     tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes(), tier_yes()],
    [Paragraph("White-label reports",         ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_no(), tier_team(), tier_team(), tier_team()],
    [Paragraph("API access + webhooks",       ps(8, color=SLATE)),
     tier_self(), tier_no(), tier_no(), tier_team(), tier_team(), tier_team()],
    [Paragraph("SSO / SAML",                  ps(8, color=SLATE)),
     tier_no(), tier_no(), tier_no(), tier_no(), tier_ent(), tier_ent()],
    [Paragraph("On-premise deployment",       ps(8, color=SLATE)),
     tier_no(), tier_no(), tier_no(), tier_no(), tier_ent(), tier_ent()],
    [Paragraph("FedRAMP / GovCloud",          ps(8, color=SLATE)),
     tier_no(), tier_no(), tier_no(), tier_no(), tier_no(), tier_gov()],
], colWidths=[2.4*inch, 0.7*inch, 0.7*inch, 0.6*inch,
              0.6*inch, 0.6*inch, 0.6*inch])

tier_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),  (-1,0),  LGRAY),
    ("LINEBELOW",     (0,0),  (-1,0),  1.0, PURPLE),
    ("LINEBELOW",     (0,1),  (-1,-1), 0.3, MGRAY),
    ("FONTSIZE",      (0,0),  (-1,-1), 8),
    ("TOPPADDING",    (0,0),  (-1,-1), 5),
    ("BOTTOMPADDING", (0,0),  (-1,-1), 5),
    ("LEFTPADDING",   (0,0),  (-1,-1), 7),
    ("RIGHTPADDING",  (0,0),  (-1,-1), 7),
    ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS",(0,1),  (-1,-1), [WHITE, LGRAY]),
    # Highlight the Pro+ column
    ("BACKGROUND",    (3,1),  (3,-1),  colors.HexColor("#F5F3FF")),
]))
story.append(tier_tbl)

story.append(Spacer(1, 14))
section("Getting Started — Four Steps")
story.append(Spacer(1, 4))

steps = Table([[
    Table([[
        Paragraph("1", ps(20, bold=True, color=WHITE, align=TA_CENTER)),
    ],[
        Paragraph("Open", ps(9, bold=True, color=WHITE, align=TA_CENTER)),
    ]], colWidths=[1.6*inch]),
    Table([[
        Paragraph("2", ps(20, bold=True, color=WHITE, align=TA_CENTER)),
    ],[
        Paragraph("Select", ps(9, bold=True, color=WHITE, align=TA_CENTER)),
    ]], colWidths=[1.6*inch]),
    Table([[
        Paragraph("3", ps(20, bold=True, color=WHITE, align=TA_CENTER)),
    ],[
        Paragraph("Assess", ps(9, bold=True, color=WHITE, align=TA_CENTER)),
    ]], colWidths=[1.6*inch]),
    Table([[
        Paragraph("4", ps(20, bold=True, color=WHITE, align=TA_CENTER)),
    ],[
        Paragraph("MCP", ps(9, bold=True, color=WHITE, align=TA_CENTER)),
    ]], colWidths=[1.6*inch]),
],[
    Paragraph(
        "Visit supply-chain-health-agent.streamlit.app "
        "— no login, no download, no IT ticket.",
        ps(8.5, color=SLATE, align=TA_CENTER)),
    Paragraph(
        "Choose your persona and industry vertical. "
        "Optionally describe your organisation.",
        ps(8.5, color=SLATE, align=TA_CENTER)),
    Paragraph(
        "Click Run Assessment. Claude searches the web "
        "and delivers full results in under 60 seconds.",
        ps(8.5, color=SLATE, align=TA_CENTER)),
    Paragraph(
        "Or add one config block to Claude Desktop and run "
        "assessments directly from your AI assistant — no browser needed.",
        ps(8.5, color=SLATE, align=TA_CENTER)),
]], colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])

steps.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (0,0),  PURPLE),
    ("BACKGROUND",    (1,0), (1,0),  TEAL),
    ("BACKGROUND",    (2,0), (2,0),  AMBER),
    ("BACKGROUND",    (3,0), (3,0),  BLUE),
    ("BACKGROUND",    (0,1), (-1,1), LGRAY),
    ("TOPPADDING",    (0,0), (-1,0), 12),
    ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ("TOPPADDING",    (0,1), (-1,1), 10),
    ("BOTTOMPADDING", (0,1), (-1,1), 10),
    ("ALIGN",         (0,0), (-1,-1), "CENTER"),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ("LINEBEFORE",    (1,0), (-1,-1), 0.5, WHITE),
    ("BOX",           (0,0), (-1,-1), 0.5, MGRAY),
]))
story.append(steps)

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.15*inch))
story.append(HRFlowable(width="100%", thickness=0.5,
    color=MGRAY, spaceAfter=5))
story.append(Paragraph(
    "Supply Chain Health Agent v4.2  ·  "
    "supply-chain-health-agent.streamlit.app  ·  "
    "github.com/dwnjuguna/Supply-Chain-Health-Agent  ·  "
    f"MIT License  ·  {now}  ·  "
    "All assessments are illustrative and directional only. "
    "Not professional financial or consulting advice.",
    ps(7, color=DGRAY, align=TA_CENTER)))

doc.build(story)
print("✅ SC_Health_Agent_Overview_v4_2.pdf — v4.2 overview complete")
