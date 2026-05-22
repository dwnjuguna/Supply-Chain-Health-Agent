"""
export.py
Generates a professional PDF report from a supply chain assessment result.
Version 2 — clean typography, no emoji dependencies, proper score bars.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime

# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#1E1A4E")
PURPLE     = colors.HexColor("#534AB7")
TEAL       = colors.HexColor("#0F6E56")
AMBER      = colors.HexColor("#E8A020")
RED        = colors.HexColor("#E24B4A")
LIGHT_GRAY = colors.HexColor("#F7F6F3")
MID_GRAY   = colors.HexColor("#9CA3AF")
DARK_TEXT  = colors.HexColor("#1A1A2E")
WHITE      = colors.white

def _score_color(score: int):
    if score >= 80: return colors.HexColor("#1D9E75")
    if score >= 60: return colors.HexColor("#3B8BD4")
    if score >= 40: return colors.HexColor("#BA7517")
    return colors.HexColor("#E24B4A")

def _score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "At Risk"

def _bar(score: int) -> str:
    """Build a proportional ASCII score bar."""
    score  = max(0, min(100, score))
    filled = round(score / 5)
    empty  = 20 - filled
    return "|" + ("=" * filled) + ("-" * empty) + "|"

def _styles():
    base = getSampleStyleSheet()
    return {
        "report_title": ParagraphStyle(
            "report_title",
            fontSize=20, fontName="Helvetica-Bold",
            textColor=WHITE, leading=26, spaceAfter=4,
        ),
        "report_meta": ParagraphStyle(
            "report_meta",
            fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#CECBF6"), leading=14,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontSize=12, fontName="Helvetica-Bold",
            textColor=NAVY, spaceBefore=16, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            fontSize=9, fontName="Helvetica",
            textColor=DARK_TEXT, spaceAfter=5, leading=14,
        ),
        "body_bold": ParagraphStyle(
            "body_bold",
            fontSize=9, fontName="Helvetica-Bold",
            textColor=DARK_TEXT, spaceAfter=5, leading=14,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer",
            fontSize=7.5, fontName="Helvetica-Oblique",
            textColor=MID_GRAY, spaceAfter=4, leading=11,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontSize=7.5, fontName="Helvetica",
            textColor=MID_GRAY, alignment=TA_CENTER,
        ),
        "score_big": ParagraphStyle(
            "score_big",
            fontSize=40, fontName="Helvetica-Bold",
            textColor=WHITE, leading=44, alignment=TA_CENTER,
        ),
        "score_label": ParagraphStyle(
            "score_label",
            fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#AFA9EC"), alignment=TA_CENTER,
        ),
        "score_rating": ParagraphStyle(
            "score_rating",
            fontSize=12, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_LEFT, leading=16,
        ),
        "score_meta": ParagraphStyle(
            "score_meta",
            fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#AFA9EC"), alignment=TA_LEFT,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontSize=9, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontSize=9, fontName="Helvetica",
            textColor=DARK_TEXT,
        ),
        "table_cell_bold": ParagraphStyle(
            "table_cell_bold",
            fontSize=9, fontName="Helvetica-Bold",
            textColor=DARK_TEXT,
        ),
    }


def generate_pdf(
    result: dict,
    vertical: str = "general",
    persona: str = "analyst",
    action_pack: dict = None,
) -> bytes:
    """
    Generate a professional PDF report from an assessment result dict.
    Returns raw bytes suitable for st.download_button.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Supply Chain Health Assessment Report",
        author="Supply Chain Health Agent",
    )

    styles      = _styles()
    story       = []
    now         = datetime.now().strftime("%B %d, %Y")
    scores_data   = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall       = scores_data.get("overall", "N/A")
    narrative     = result.get("narrative", "")

    # ── PAGE 1: COVER HEADER ───────────────────────────────────────────────────
    header_content = [
        [
            Paragraph("SUPPLY CHAIN HEALTH AGENT", styles["report_title"]),
        ],
        [
            Paragraph(
                f"Assessment Report  |  {vertical.upper()}  |  {now}",
                styles["report_meta"]
            ),
        ],
        [
            Paragraph(
                f"Track: {persona.capitalize()}  |  Powered by Anthropic Claude",
                styles["report_meta"]
            ),
        ],
    ]
    header_table = Table(
        header_content,
        colWidths=[7 * inch],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1,  0), 24),
        ("BOTTOMPADDING", (0, -1),(-1, -1), 24),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
        ("TOPPADDING",    (0, 1), (-1, -2), 2),
        ("BOTTOMPADDING", (0, 1), (-1, -2), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15 * inch))

    # ── DISCLAIMER ─────────────────────────────────────────────────────────────
    disclaimer_table = Table(
        [[Paragraph(
            "IMPORTANT: Illustrative and Directional Use Only. All assessments, scores, "
            "benchmarks, and financial estimates are for informational purposes only. "
            "This report does not constitute professional financial, legal, or management "
            "consulting advice. Validate all outputs with qualified advisors before making "
            "investment or operational decisions.",
            styles["disclaimer"]
        )]],
        colWidths=[7 * inch],
    )
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
        ("LINEABOVE",     (0, 0), (-1,  0), 1.5, colors.HexColor("#FCD34D")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(disclaimer_table)
    story.append(Spacer(1, 0.2 * inch))

    # ── OVERALL SCORE ──────────────────────────────────────────────────────────
    story.append(Paragraph("Overall Health Score", styles["section_title"]))
    story.append(HRFlowable(
        width="100%", thickness=2, color=PURPLE, spaceAfter=8
    ))

    if isinstance(overall, (int, float)):
        ov_int   = int(overall)
        ov_color = _score_color(ov_int)
        ov_label = _score_label(ov_int)

        score_block = Table(
            [[
                Table(
                    [[Paragraph(str(ov_int), styles["score_big"])],
                     [Paragraph("out of 100", styles["score_label"])]],
                    colWidths=[1.5 * inch],
                ),
                Table(
                    [[Paragraph(ov_label, styles["score_rating"])],
                     [Paragraph(
                         f"Vertical: {vertical.upper()}",
                         styles["score_meta"]
                     )],
                     [Paragraph(
                         f"Track: {persona.capitalize()}  |  Date: {now}",
                         styles["score_meta"]
                     )]],
                    colWidths=[5.5 * inch],
                ),
            ]],
            colWidths=[1.5 * inch, 5.5 * inch],
        )
        score_block.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
            ("TOPPADDING",    (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
            ("LEFTPADDING",   (0, 0), (0,  -1), 16),
            ("LEFTPADDING",   (1, 0), (1,  -1), 20),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEAFTER",     (0, 0), (0,  -1), 1,
             colors.HexColor("#534AB7")),
        ]))
        story.append(score_block)
    story.append(Spacer(1, 0.2 * inch))

    # ── DOMAIN SCORES TABLE ────────────────────────────────────────────────────
    if domain_scores:
        story.append(Paragraph("Domain Scores", styles["section_title"]))
        story.append(HRFlowable(
            width="100%", thickness=2, color=PURPLE, spaceAfter=8
        ))

        rows = [[
            Paragraph("Domain",  styles["table_header"]),
            Paragraph("Score",   styles["table_header"]),
            Paragraph("Rating",  styles["table_header"]),
            Paragraph("Health Bar", styles["table_header"]),
        ]]

        for domain, score in domain_scores.items():
            score  = max(0, min(100, int(score)))
            label  = _score_label(score)
            col    = _score_color(score)
            bar    = _bar(score)

            rows.append([
                Paragraph(
                    domain.replace("_", " ").title(),
                    styles["table_cell_bold"]
                ),
                Paragraph(
                    f"{score}/100",
                    ParagraphStyle(
                        "ts", fontSize=9, fontName="Helvetica-Bold",
                        textColor=col, alignment=TA_CENTER
                    )
                ),
                Paragraph(
                    label,
                    ParagraphStyle(
                        "tl", fontSize=8, fontName="Helvetica",
                        textColor=col, alignment=TA_CENTER
                    )
                ),
                Paragraph(
                    bar,
                    ParagraphStyle(
                        "tb", fontSize=7.5, fontName="Courier",
                        textColor=col
                    )
                ),
            ])

        domain_table = Table(
            rows,
            colWidths=[1.6*inch, 0.8*inch, 0.9*inch, 3.7*inch]
        )
        domain_table.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1,  0), PURPLE),
            ("TOPPADDING",     (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 8),
            ("LEFTPADDING",    (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [WHITE, colors.HexColor("#F0EFF9")]),
            ("GRID",           (0, 0), (-1, -1),
             0.3, colors.HexColor("#E5E7EB")),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW",      (0, 0), (-1,  0), 1.5, PURPLE),
        ]))
        story.append(domain_table)

    # ── PAGE 2+: NARRATIVE SECTIONS ────────────────────────────────────────────
    if narrative:
        story.append(PageBreak())

        SECTION_MAP = {
            "EXECUTIVE SUMMARY":        ("EXECUTIVE SUMMARY",         PURPLE),
            "TOP RISKS":                ("TOP RISKS",                  RED),
            "DOMAIN HIGHLIGHTS":        ("DOMAIN HIGHLIGHTS",          NAVY),
            "PRIORITY RECOMMENDATIONS": ("PRIORITY RECOMMENDATIONS",   TEAL),
            "COST-BENEFIT ANALYSIS":    ("COST-BENEFIT ANALYSIS",      AMBER),
            "STRATEGIC SCENARIO":       ("STRATEGIC SCENARIO COMPARISON", TEAL),
            "SUPPLY CHAIN MATURITY":    ("SUPPLY CHAIN MATURITY ROADMAP", NAVY),
        }

        current_key    = None
        current_title  = None
        current_accent = PURPLE
        section_lines  = []

        def _flush(title, accent, lines):
            if not lines:
                return
            block = []
            block.append(HRFlowable(
                width="100%", thickness=2.5,
                color=accent, spaceAfter=6
            ))
            block.append(Paragraph(title, styles["section_title"]))
            content = "\n".join(lines).strip()
            for para in content.split("\n"):
                para = para.strip()
                if not para:
                    continue
                if para.startswith(("•", "-", "*")):
                    block.append(Paragraph(
                        "&nbsp;&nbsp;&nbsp;" + para,
                        styles["body"]
                    ))
                else:
                    block.append(Paragraph(para, styles["body"]))
            block.append(Spacer(1, 0.1 * inch))
            story.append(KeepTogether(block[:6]))
            for item in block[6:]:
                story.append(item)

        for line in narrative.split("\n"):
            matched = False
            for key, (title, accent) in SECTION_MAP.items():
                if key in line.upper():
                    if current_key:
                        _flush(current_title, current_accent, section_lines)
                    current_key    = key
                    current_title  = title
                    current_accent = accent
                    section_lines  = []
                    matched = True
                    break
            if not matched and current_key:
                section_lines.append(line)

        if current_key:
            _flush(current_title, current_accent, section_lines)

    # ── ACTION PACK (if provided) ──────────────────────────────────────────────
    if action_pack:
        story.append(PageBreak())
        story.append(Paragraph("ACTION PACK", styles["section_title"]))
        story.append(HRFlowable(
            width="100%", thickness=2.5, color=TEAL, spaceAfter=8
        ))
        for section_key, section_title in [
            ("board_summary",  "Board Summary"),
            ("action_plan",    "90-Day Action Plan"),
            ("risk_watchlist", "Risk Watch List"),
        ]:
            content = action_pack.get(section_key, "")
            if content:
                story.append(Paragraph(section_title, styles["body_bold"]))
                story.append(HRFlowable(
                    width="100%", thickness=0.5,
                    color=MID_GRAY, spaceAfter=4
                ))
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        story.append(Paragraph(para, styles["body"]))
                story.append(Spacer(1, 0.15 * inch))

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=6
    ))
    story.append(Paragraph(
        f"Supply Chain Health Agent  |  Powered by Anthropic Claude  |  "
        f"Generated: {now}  |  For informational purposes only.",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()
