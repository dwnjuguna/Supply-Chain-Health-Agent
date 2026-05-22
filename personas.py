# personas.py
# Defines the two user-facing tracks and their associated prompt extensions,
# UI configuration, and output expectations.
# A third persona (Enterprise IT / Configurator) is reserved for Phase 2.

# ── Persona registry ──────────────────────────────────────────────────────────

PERSONAS = {
    "analyst": {
        "key":         "analyst",
        "title":       "Supply Chain Manager / Analyst",
        "icon":        "📊",
        "description": (
            "Deep KPI diagnostics, benchmark comparisons, domain-level inputs, "
            "and cost-benefit analysis. Built for practitioners who speak the language."
        ),
        "badge":       "Practitioner Track",
        "badge_color": "#534AB7",
    },
    "executive": {
        "key":         "executive",
        "title":       "C-Suite / Board Member",
        "icon":        "🏢",
        "description": (
            "Strategic scenario comparison, maturity roadmap, and board-ready summaries. "
            "Built for leaders making investment and transformation decisions."
        ),
        "badge":       "Executive Track",
        "badge_color": "#0F6E56",
    },
    "configurator": {
        "key":         "configurator",
        "title":       "Enterprise Configuration",
        "icon":        "⚙️",
        "description": (
            "Embed and configure this agent within your organisation's systems. "
            "Set access controls, presets, branding, and compliance guardrails."
        ),
        "badge":       "Coming Soon — Phase 2",
        "badge_color": "#9CA3AF",
        "disabled":    True,
    },
}

# ── Executive track: strategic context questions ──────────────────────────────
# Shown instead of the granular domain text areas when the user is on the
# executive track. These are higher-level, jargon-light inputs.

EXECUTIVE_CONTEXT_QUESTIONS = [
    {
        "key":         "org_context",
        "label":       "Tell us about your organisation",
        "placeholder": (
            "e.g. 'We are a $2B automotive parts manufacturer operating across "
            "12 countries, with 3 major distribution centres and ~200 suppliers. "
            "We have been growing 15% YoY but our supply chain hasn't kept pace.'"
        ),
        "height": 100,
    },
    {
        "key":         "strategic_pressure",
        "label":       "What is driving the need for change?",
        "placeholder": (
            "e.g. 'Increasing customer complaints about delivery reliability, "
            "rising freight costs, a major competitor investing in automation, "
            "or board pressure to improve working capital and reduce inventory.'"
        ),
        "height": 90,
    },
    {
        "key":         "investment_horizon",
        "label":       "What is your investment horizon and appetite?",
        "placeholder": (
            "e.g. 'We have budget approval for up to $5M over the next 18 months "
            "and need to show ROI within 2 years. The board prefers phased investments "
            "over big-bang transformation.'"
        ),
        "height": 90,
    },
    {
        "key":         "risk_appetite",
        "label":       "How would you describe your organisation's risk appetite?",
        "placeholder": (
            "e.g. 'Conservative — we prefer proven solutions with low disruption risk. "
            "Or: Aggressive — we are willing to pilot emerging technologies if the "
            "upside is significant.'"
        ),
        "height": 80,
    },
    {
        "key":         "top_priorities",
        "label":       "What are your top 2–3 strategic priorities right now?",
        "placeholder": (
            "e.g. 'Improve customer service levels (OTIF), reduce working capital tied "
            "up in inventory, and build resilience against geopolitical supply disruptions.'"
        ),
        "height": 80,
    },
]

# ── Executive track: customisation options ────────────────────────────────────
# Shown when the user toggles "Customise this assessment" on the executive track.

EXECUTIVE_CUSTOMISATION_OPTIONS = {
    "growth_vs_cost": {
        "label":   "Strategic orientation",
        "options": ["Balanced", "Growth-first", "Cost-out / Efficiency-first"],
        "default": "Balanced",
        "help":    "Shapes which recommendations are prioritised.",
    },
    "timeline_preference": {
        "label":   "Transformation timeline preference",
        "options": ["Quick wins only (0–12 months)", "Medium-term (12–24 months)",
                    "Long-term transformation (24–36+ months)", "All horizons"],
        "default": "All horizons",
        "help":    "Filters the maturity roadmap to your preferred horizon.",
    },
    "benchmark_peer": {
        "label":   "Benchmark against",
        "options": ["Gartner Top 25 world-class", "Industry average",
                    "Top quartile for my sector", "Direct competitors"],
        "default": "Gartner Top 25 world-class",
        "help":    "Sets the comparison standard used throughout the report.",
    },
    "output_style": {
        "label":   "Report language style",
        "options": ["Board presentation (concise, visual-friendly)",
                    "Executive briefing (narrative, 2–3 pages)",
                    "Full strategic report (comprehensive)"],
        "default": "Executive briefing (narrative, 2–3 pages)",
        "help":    "Controls the depth and format of the output.",
    },
}

# ── Executive track: system prompt extension ──────────────────────────────────
# Appended to the base system prompt when the executive track is active.
# Instructs Claude on tone, output structure, and the two new sections.

EXECUTIVE_SYSTEM_PROMPT_EXTENSION = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE TRACK — OUTPUT REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are producing a strategic supply chain assessment for C-suite executives
and board members. Adjust your output accordingly:

LANGUAGE & TONE:
  • Avoid operational jargon and unexplained acronyms. Write for a CFO or CEO,
    not a supply chain practitioner. When technical terms are necessary,
    briefly define them in plain language.
  • Lead with business impact, not process detail. "This is costing you an
    estimated $X–$Y per year" before "your MAPE is 24%".
  • Be direct and confident. Executives need clear recommendations, not hedged
    observations. Use ranges honestly, but commit to a recommended path.
  • Every section should answer the question a board member would ask:
    "So what? What does this mean for our strategy and our P&L?"

OUTPUT STRUCTURE:
After the standard four sections (Executive Summary, Top Risks, Domain Highlights,
Priority Recommendations), add these two additional sections:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: STRATEGIC SCENARIO COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Present THREE named strategic paths tailored to this organisation's context,
priorities, and the domains where the largest gaps were identified.
Name each scenario descriptively (not just "Option A/B/C").

For EACH scenario provide:

  NAME & ONE-LINE DESCRIPTION
  What it means: A 3–4 sentence plain-English description of the strategic
    approach — what changes, what stays the same, and why someone would choose it.

  Domains addressed: Which of the 8 domains this scenario meaningfully improves.

  Investment range: Low / Medium / High with indicative $ range and timeframe.
    If financial data was provided by the user, scale to their context.
    Otherwise use industry-typical ranges and state the assumption.

  Expected KPI movement: For the 2–3 most impacted domains, show the expected
    score improvement (e.g. "Logistics: 62 → 80–85 within 18 months").

  Key trade-offs: What this scenario sacrifices or accepts as a risk
    (e.g. "Requires 12–18 months of elevated operational disruption during
    transition", or "Does not address the sustainability gap").

  Best suited for: The type of organisation or leadership mandate that makes
    this the right choice (e.g. "Organisations prioritising speed to ROI with
    limited transformation appetite").

Close the section with a RECOMMENDED SCENARIO — state clearly which of the three
you recommend for this organisation and the 2–3 reasons why, given what they
have shared about their priorities, risk appetite, and investment horizon.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: SUPPLY CHAIN MATURITY ROADMAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Present a phased maturity roadmap aligned to the recommended scenario above.
Use four phases. For each phase provide:

  PHASE 0 — NOW (Current State)
  A one-paragraph honest assessment of where the organisation sits today.
  Reference the domain scores. Name the 2–3 most urgent vulnerabilities.
  What is the cost of staying here? (Annual run-rate of current performance gaps.)

  PHASE 1 — STABILISE (Months 0–6)
  Focus: Fix the most critical failures and establish a reliable baseline.
  Key actions (3–5 specific, named initiatives — not generic advice).
  Investment: $ range and effort level.
  Milestone: What does success look like at the 6-month mark?
    Express as measurable KPI targets (e.g. "OTIF from 82% → 90%").
  Quick wins: Call out any actions in this phase with payback < 6 months.

  PHASE 2 — BUILD (Months 6–18)
  Focus: Close the gap to industry-average performance; build capability.
  Key actions (3–5 initiatives, more strategic than Phase 1).
  Investment: $ range and effort level.
  Milestone: KPI targets at the 18-month mark.
  Interdependencies: Which Phase 1 foundations must be in place first.

  PHASE 3 — LEAD (Months 18–36+)
  Focus: Reach top-quartile or world-class performance; build competitive advantage.
  Key actions (3–5 initiatives, including technology and structural changes).
  Investment: $ range and effort level.
  Milestone: KPI targets at the 36-month mark.
  Strategic outcome: What does the supply chain look like at the end of this phase,
    and what competitive advantage does it unlock?

  TOTAL PROGRAMME SUMMARY
  Aggregate investment range across all phases.
  Aggregate benefit range (annual, once Phase 3 is realised).
  Overall payback period estimate.
  One sentence on the cost of inaction (what happens if nothing changes).

CUSTOMISATION NOTE:
If the user has provided customisation preferences (strategic orientation,
timeline preference, benchmark peer, output style), honour them throughout.
For example: if they selected "Quick wins only", compress the roadmap to
Phase 0 and Phase 1 only and expand the quick-wins detail.
If they selected "Cost-out", weight recommendations toward working capital
and efficiency initiatives over growth-enabling investments.
"""


def get_executive_prompt_extension(customisation: dict = None) -> str:
    """
    Returns the executive system prompt extension, optionally appending
    any customisation preferences the user has selected.
    """
    base = EXECUTIVE_SYSTEM_PROMPT_EXTENSION

    if customisation:
        lines = ["CUSTOMISATION PREFERENCES SET BY THIS USER:"]
        for k, v in customisation.items():
            label = EXECUTIVE_CUSTOMISATION_OPTIONS.get(k, {}).get("label", k)
            lines.append(f"  • {label}: {v}")
        base += "\n" + "\n".join(lines) + "\n"

    return base
