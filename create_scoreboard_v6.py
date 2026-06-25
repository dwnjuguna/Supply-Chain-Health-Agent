"""
SC Health Agent — Executive Scoreboard One-Pager v6
Full redesign: Ive/Fadell principles. One clear story, instant comprehension,
passes both executive and 4th grader tests.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, white

W, H = landscape(letter)   # 792 x 612 pts

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY      = HexColor("#12103C")   # background
CARD      = HexColor("#1A1745")   # card surface
HEADER    = HexColor("#0A0828")   # header — darkest
PURPLE    = HexColor("#6C63E0")   # brand
PUR_DIM   = HexColor("#3D3880")   # dimmed purple
GREEN     = HexColor("#22C55E")   # winning
AMBER     = HexColor("#F59E0B")   # needs work
RED       = HexColor("#EF4444")   # danger
WHITE     = white
OFFWHITE  = HexColor("#E8E6F8")   # primary text
DIM       = HexColor("#8B88B8")   # secondary text
DIVIDER   = HexColor("#252255")   # card borders

def sc(s): return GREEN if s >= 80 else AMBER if s >= 60 else RED
def sr(s): return "EXCELLENT" if s >= 80 else "FAIR" if s >= 60 else "AT RISK"

def rct(c, x, y, w, h, fill, rad=0, border=None, bw=0.6):
    c.setFillColor(fill)
    c.setLineWidth(bw if border else 0)
    if border: c.setStrokeColor(border)
    fn = c.roundRect if rad else c.rect
    fn(*([x,y,w,h]+([rad] if rad else [])), fill=1, stroke=1 if border else 0)

def t(c, s, x, y, font="Helvetica-Bold", sz=10, col=None, align="left"):
    col = col or WHITE
    c.setFont(font, sz)
    c.setFillColor(col)
    {"left":c.drawString,"center":c.drawCentredString,"right":c.drawRightString}[align](x,y,s)

def hl(c, x1, y1, x2, y2=None, col=None, w=0.5):
    c.setStrokeColor(col or DIVIDER)
    c.setLineWidth(w)
    c.line(x1, y1, x2, y2 if y2 is not None else y1)

# ── Data ──────────────────────────────────────────────────────────────────────
DOMAINS = [
    ("Demand Planning",   72, "85–90%",  "How well we predict\nwhat customers need"),
    ("Procurement",       88, "95%+",    "Getting the best deals\nfrom our suppliers"),
    ("Manufacturing",     65, "85%+",    "How well our\nfactories perform"),
    ("Inventory",         54, "8–12x",   "How fast products\nmove off our shelves"),
    ("Logistics",         79, "95–98%",  "Delivering orders\non time, every time"),
    ("Warehousing",       91, "99.9%",   "Running our warehouses\nwith precision"),
    ("Risk & Resilience", 48, "95%+",    "How ready we are\nif things go wrong"),
    ("Sustainability",    63, "80%+",    "How green our\nsupply chain is"),
]
OVERALL  = 70
ORG      = "Acme Manufacturing"

# ── Layout ────────────────────────────────────────────────────────────────────
HDR_H  = 64    # header
TOP_H  = 76    # reduced — gives header text breathing room, more space for cards
FOOT_H = 72    # footer strip — legend sits clearly below card bottoms
GRID_H = H - HDR_H - TOP_H - FOOT_H   # remaining for cards
MX     = 18    # side margins
GAP    = 9     # gap between cards
COLS   = 4
ROWS   = 2
CW     = (W - 2*MX - (COLS-1)*GAP) / COLS
CH     = (GRID_H - GAP) / ROWS

def build(filename, pagesize=landscape(letter)):
    pw, ph = pagesize  # page width, height
    c = canvas.Canvas(filename, pagesize=pagesize)

    # Recompute layout for this page size
    cw = (pw - 2*MX - (COLS-1)*GAP) / COLS
    grid_h = ph - HDR_H - TOP_H - FOOT_H
    ch = (grid_h - GAP) / ROWS

    # ── BACKGROUND ────────────────────────────────────────────────────────────
    rct(c, 0, 0, pw, ph, NAVY)

    # ── HEADER ────────────────────────────────────────────────────────────────
    rct(c, 0, ph-HDR_H, pw, HDR_H, HEADER)
    rct(c, 0, ph-HDR_H, pw, 3, PURPLE)

    t(c, "SUPPLY CHAIN HEALTH AGENT",
      28, ph-28, sz=16, col=OFFWHITE)
    t(c, f"Executive Scoreboard  ·  {ORG}  ·  June 2026",
      28, ph-46, font="Helvetica", sz=10, col=DIM)
    t(c, "Scored 0–100 vs 2026 world-class benchmarks  ·  Powered by Anthropic Claude SDK",
      28, ph-61, font="Helvetica", sz=7.5, col=HexColor("#8B88B8"))

    # ── TOP SECTION: OVERALL SCORE + TAGLINE ─────────────────────────────────
    TOP_Y = ph - HDR_H

    # Color swatch bar
    OV_X = MX
    rct(c, OV_X, TOP_Y-TOP_H+14, 5, TOP_H-28, sc(OVERALL), rad=2)

    t(c, "OVERALL HEALTH SCORE", OV_X+14, TOP_Y-16,
      font="Helvetica", sz=8, col=DIM)
    t(c, str(OVERALL), OV_X+14, TOP_Y-54, sz=44, col=sc(OVERALL))
    t(c, "/ 100", OV_X+74, TOP_Y-42, font="Helvetica", sz=12, col=DIM)
    t(c, sr(OVERALL), OV_X+14, TOP_Y-70,
      font="Helvetica-Bold", sz=10, col=sc(OVERALL))

    # Vertical divider
    hl(c, OV_X+160, TOP_Y-8, OV_X+160, TOP_Y-TOP_H+8, col=DIVIDER, w=1.0)

    # Tagline — centered in remaining width
    TAG_X  = OV_X + 175
    TAG_CX = TAG_X + (pw - TAG_X - MX - 20) / 2

    t(c, "Every great team", TAG_CX, TOP_Y-20,
      font="Helvetica-Oblique", sz=14, col=OFFWHITE, align="center")
    t(c, "knows the score.", TAG_CX, TOP_Y-40,
      font="Helvetica-Oblique", sz=14, col=OFFWHITE, align="center")
    t(c, "Now your supply chain does too.",
      TAG_CX, TOP_Y-60,
      font="Helvetica-Oblique", sz=10, col=HexColor("#AFA9EC"), align="center")

    # Separator line below top section
    hl(c, MX, TOP_Y-TOP_H, pw-MX, col=DIVIDER, w=0.8)

    # ── SCOREBOARD GRID ───────────────────────────────────────────────────────
    GRID_TOP = TOP_Y - TOP_H - 6

    for i, (name, score, benchmark, plain) in enumerate(DOMAINS):
        col_i = i % COLS
        row_i = i // COLS
        cx = MX + col_i*(cw+GAP)
        cy = GRID_TOP - row_i*(ch+GAP) - ch

        color  = sc(score)
        rating = sr(score)

        # Card
        rct(c, cx, cy, cw, ch, CARD, rad=4, border=DIVIDER, bw=0.6)
        rct(c, cx, cy+ch-5, cw, 5, color, rad=0)

        # Domain name
        t(c, name.upper(), cx+cw/2, cy+ch-19,
          font="Helvetica-Bold", sz=6.5, col=OFFWHITE, align="center")

        # Score number
        t(c, str(score), cx+cw/2-10, cy+ch-54,
          sz=28, col=color, align="center")
        t(c, "/ 100", cx+cw/2+20, cy+ch-48,
          font="Helvetica", sz=7.5, col=DIM, align="left")

        # Status pill
        pill_w = 60
        pill_x = cx+cw/2-pill_w/2
        pill_y = cy+ch-69
        rct(c, pill_x, pill_y, pill_w, 12, color, rad=2)
        t(c, rating, cx+cw/2, pill_y+4,
          font="Helvetica-Bold", sz=5.5, col=WHITE, align="center")

        # Divider
        hl(c, cx+8, cy+ch-77, cx+cw-8)

        # World class
        t(c, "WORLD CLASS", cx+8, cy+ch-88,
          font="Helvetica", sz=5.5, col=DIM)
        t(c, benchmark, cx+cw-8, cy+ch-88,
          font="Helvetica-Bold", sz=7, col=OFFWHITE, align="right")

        # Plain English — 4th grader anchor
        lines = plain.split("\n")
        line_y = cy + 32
        for ln in lines:
            t(c, ln, cx+cw/2, line_y,
              font="Helvetica-Oblique", sz=6.5, col=DIM, align="center")
            line_y -= 11

    # ── LEGEND STRIP ─────────────────────────────────────────────────────────
    rct(c, 0, 16, pw, FOOT_H-16, HEADER)
    rct(c, 0, FOOT_H-2, pw, 2, PURPLE)

    LEGY = FOOT_H - 22
    legend_items = [
        (GREEN, "80–100  EXCELLENT", "World-class — sustain and innovate"),
        (AMBER, "60–79   FAIR",      "On track — focused improvement needed"),
        (RED,   "0–59    AT RISK",   "Urgent — act now"),
    ]
    lx = MX
    for col_c, label, desc in legend_items:
        rct(c, lx, LEGY+3, 9, 9, col_c, rad=1)
        t(c, label, lx+13, LEGY+10, font="Helvetica-Bold", sz=7.5, col=OFFWHITE)
        t(c, desc,  lx+13, LEGY+1,  font="Helvetica",      sz=6.5, col=DIM)
        lx += 210

    t(c, "Get your score free — 60 seconds  →",
      pw-MX, LEGY+10, font="Helvetica-Bold", sz=8, col=PURPLE, align="right")
    t(c, "supply-chain-health-agent.streamlit.app",
      pw-MX, LEGY+1, font="Helvetica", sz=6.5, col=DIM, align="right")

    # ── FOOTER ───────────────────────────────────────────────────────────────
    rct(c, 0, 0, pw, 16, HEADER)
    t(c, "supply-chain-health-agent.streamlit.app  ·  "
         "github.com/dwnjuguna/Supply-Chain-Health-Agent  ·  "
         "MIT License  ·  Results are illustrative and directional only.",
      pw/2, 4, font="Helvetica", sz=6, col=PUR_DIM, align="center")

    c.save()
    print(f"✅ {filename}")

from reportlab.lib.pagesizes import A4

build("/home/claude/SC_Health_Agent_Scoreboard_Letter.pdf", landscape(letter))
build("/home/claude/SC_Health_Agent_Scoreboard_A4.pdf",     landscape(A4))
