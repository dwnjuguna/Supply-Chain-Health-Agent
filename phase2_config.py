"""
phase2_config.py

Feature flag configuration for Supply Chain Health Agent Phase 2.
Controls which capabilities are available per tier.

TRADE SECRET — NOT FOR DISTRIBUTION.
Tier definitions, pricing, and business logic are maintained
separately and never committed to the public repository.

Author: David Njuguna
"""

# ── Tier keys ─────────────────────────────────────────────────────────────────
# These are internal identifiers only — no pricing information here.

TIER_OPEN_SOURCE   = "open_source"
TIER_HOSTED_FREE   = "hosted_free"
TIER_PRO           = "pro"
TIER_TEAM          = "team"
TIER_ENTERPRISE    = "enterprise"
TIER_GOVERNMENT    = "government"

ALL_TIERS = [
    TIER_OPEN_SOURCE,
    TIER_HOSTED_FREE,
    TIER_PRO,
    TIER_TEAM,
    TIER_ENTERPRISE,
    TIER_GOVERNMENT,
]

# ── Persona keys ──────────────────────────────────────────────────────────────

PERSONA_ANALYST      = "analyst"         # Supply Chain Manager / Analyst
PERSONA_EXECUTIVE    = "executive"       # CSCO / COO / VP Supply Chain
PERSONA_CONSULTANT   = "consultant"      # Supply Chain Consultant
PERSONA_ENTERPRISE   = "enterprise_it"  # Enterprise IT / Configurator
PERSONA_GOVERNMENT   = "government"      # Government / Federal

ALL_PERSONAS = [
    PERSONA_ANALYST,
    PERSONA_EXECUTIVE,
    PERSONA_CONSULTANT,
    PERSONA_ENTERPRISE,
    PERSONA_GOVERNMENT,
]

# ── Feature definitions ───────────────────────────────────────────────────────
# Each feature maps to the minimum tier required to access it.
# "open_source" = available to everyone including self-hosters.

FEATURES = {

    # ── Core assessment ───────────────────────────────────────────────────────
    "general_assessment":        TIER_OPEN_SOURCE,
    "custom_assessment":         TIER_OPEN_SOURCE,
    "domain_scores":             TIER_OPEN_SOURCE,
    "narrative_report":          TIER_OPEN_SOURCE,
    "priority_recommendations":  TIER_OPEN_SOURCE,
    "basic_pdf_export":          TIER_OPEN_SOURCE,
    "followup_qa":               TIER_OPEN_SOURCE,
    "web_search":                TIER_OPEN_SOURCE,

    # ── Verticals ─────────────────────────────────────────────────────────────
    "verticals_basic":           TIER_OPEN_SOURCE,   # general, retail, pharma, automotive
    "verticals_full":            TIER_HOSTED_FREE,   # all 11 verticals
    "verticals_custom":          TIER_ENTERPRISE,    # org-defined custom verticals

    # ── Personas ──────────────────────────────────────────────────────────────
    "persona_analyst":           TIER_OPEN_SOURCE,
    "persona_executive":         TIER_HOSTED_FREE,
    "persona_consultant":        TIER_PRO,
    "persona_enterprise_it":     TIER_ENTERPRISE,
    "persona_government":        TIER_GOVERNMENT,

    # ── Export & reports ──────────────────────────────────────────────────────
    "pdf_export_basic":          TIER_OPEN_SOURCE,
    "pdf_export_branded":        TIER_PRO,
    "pdf_export_white_label":    TIER_TEAM,
    "word_export":               TIER_PRO,
    "csv_export":                TIER_PRO,

    # ── Assessment limits ─────────────────────────────────────────────────────
    "assessments_per_month_3":   TIER_HOSTED_FREE,   # 3/month cap
    "assessments_unlimited":     TIER_PRO,           # unlimited

    # ── Cost-benefit analysis ─────────────────────────────────────────────────
    "cba_basic":                 TIER_HOSTED_FREE,
    "cba_advanced":              TIER_PRO,           # full financial inputs + ROI matrix

    # ── Action pack ───────────────────────────────────────────────────────────
    "action_pack_basic":         TIER_HOSTED_FREE,
    "action_pack_full":          TIER_PRO,           # board summary + 90-day plan + risk list

    # ── Market intelligence ───────────────────────────────────────────────────
    "market_intelligence":       TIER_PRO,

    # ── Phase 2: Memory ───────────────────────────────────────────────────────
    "session_memory":            TIER_PRO,           # remember within session
    "cross_session_memory":      TIER_PRO,           # remember across sessions
    "org_memory":                TIER_TEAM,          # shared org-level memory
    "kpi_trend_tracking":        TIER_PRO,           # track scores over time
    "assessment_history":        TIER_PRO,           # full history + comparison

    # ── Phase 2: Alerts ───────────────────────────────────────────────────────
    "proactive_risk_alerts":     TIER_PRO,           # Claude monitors + alerts
    "alert_slack":               TIER_PRO,           # Slack webhook delivery
    "alert_email":               TIER_PRO,           # Email delivery
    "alert_scheduling":          TIER_TEAM,          # scheduled recurring scans
    "alert_custom_rules":        TIER_ENTERPRISE,    # custom alert thresholds

    # ── Phase 2: Integrations ─────────────────────────────────────────────────
    "integration_slack":         TIER_PRO,           # push summaries to Slack
    "integration_jira":          TIER_TEAM,          # create Jira tickets
    "integration_email":         TIER_PRO,           # email reports
    "integration_webhook":       TIER_TEAM,          # generic webhooks
    "integration_api":           TIER_TEAM,          # REST API access
    "integration_mcp":           TIER_ENTERPRISE,    # MCP server access

    # ── Phase 2: Consultant features ─────────────────────────────────────────
    "multi_client_dashboard":    TIER_TEAM,          # manage multiple clients
    "client_intake_form":        TIER_PRO,           # shareable intake forms
    "consultant_branding":       TIER_TEAM,          # white-label with logo
    "client_comparison":         TIER_TEAM,          # compare clients side-by-side

    # ── Phase 2: Enterprise features ─────────────────────────────────────────
    "sso_saml":                  TIER_ENTERPRISE,
    "audit_logs":                TIER_ENTERPRISE,
    "admin_panel":               TIER_ENTERPRISE,
    "custom_branding":           TIER_ENTERPRISE,
    "sla_guarantee":             TIER_ENTERPRISE,
    "dedicated_csm":             TIER_ENTERPRISE,
    "on_premise_deploy":         TIER_ENTERPRISE,

    # ── Government features ───────────────────────────────────────────────────
    "govcloud_deploy":           TIER_GOVERNMENT,
    "airgap_mode":               TIER_GOVERNMENT,
    "fedramp_compliance":        TIER_GOVERNMENT,
    "itar_controls":             TIER_GOVERNMENT,
    "fips_140_2":                TIER_GOVERNMENT,
    "classified_mode":           TIER_GOVERNMENT,
}

# ── Tier ordering for comparisons ─────────────────────────────────────────────
TIER_ORDER = {
    TIER_OPEN_SOURCE:  0,
    TIER_HOSTED_FREE:  1,
    TIER_PRO:          2,
    TIER_TEAM:         3,
    TIER_ENTERPRISE:   4,
    TIER_GOVERNMENT:   5,
}

# ── Helper functions ──────────────────────────────────────────────────────────

def has_feature(feature: str, user_tier: str) -> bool:
    """
    Returns True if the given tier has access to the feature.
    Tiers are additive — higher tiers include all lower tier features.
    """
    if feature not in FEATURES:
        return False
    required_tier = FEATURES[feature]
    return TIER_ORDER.get(user_tier, -1) >= TIER_ORDER.get(required_tier, 999)


def get_available_features(user_tier: str) -> list:
    """Returns all features available to the given tier."""
    return [
        feature for feature in FEATURES
        if has_feature(feature, user_tier)
    ]


def get_locked_features(user_tier: str) -> list:
    """Returns features not yet available at the given tier."""
    return [
        feature for feature in FEATURES
        if not has_feature(feature, user_tier)
    ]


def get_minimum_tier_for(feature: str) -> str:
    """Returns the minimum tier required to access a feature."""
    return FEATURES.get(feature, "unknown")


def tier_can_access_persona(user_tier: str, persona: str) -> bool:
    """Returns True if the tier can access the given persona."""
    feature_key = f"persona_{persona}"
    return has_feature(feature_key, user_tier)


# ── Assessment limits ─────────────────────────────────────────────────────────

ASSESSMENT_LIMITS = {
    TIER_OPEN_SOURCE:  None,   # self-hosted: unlimited
    TIER_HOSTED_FREE:  3,      # 3 per month
    TIER_PRO:          None,   # unlimited
    TIER_TEAM:         None,   # unlimited
    TIER_ENTERPRISE:   None,   # unlimited
    TIER_GOVERNMENT:   None,   # unlimited
}


def get_assessment_limit(user_tier: str):
    """Returns monthly assessment limit. None = unlimited."""
    return ASSESSMENT_LIMITS.get(user_tier, 3)


# ── Vertical access ───────────────────────────────────────────────────────────

BASIC_VERTICALS = ["general", "retail", "pharma", "automotive"]

def get_available_verticals(user_tier: str) -> list:
    """Returns list of available vertical keys for the tier."""
    from verticals import VERTICAL_PRESETS
    if has_feature("verticals_full", user_tier):
        return list(VERTICAL_PRESETS.keys())
    return BASIC_VERTICALS


# ── Phase 2 feature availability ─────────────────────────────────────────────

PHASE2_FEATURES = {
    "memory":       ["cross_session_memory", "kpi_trend_tracking", "assessment_history"],
    "alerts":       ["proactive_risk_alerts", "alert_slack", "alert_email"],
    "integrations": ["integration_slack", "integration_jira", "integration_api"],
    "consultant":   ["multi_client_dashboard", "client_intake_form", "consultant_branding"],
    "enterprise":   ["sso_saml", "audit_logs", "admin_panel", "on_premise_deploy"],
    "government":   ["govcloud_deploy", "airgap_mode", "fedramp_compliance"],
}


def get_phase2_status(user_tier: str) -> dict:
    """
    Returns Phase 2 feature availability summary for a given tier.
    Useful for rendering upgrade prompts in the UI.
    """
    status = {}
    for category, features in PHASE2_FEATURES.items():
        available = [f for f in features if has_feature(f, user_tier)]
        locked    = [f for f in features if not has_feature(f, user_tier)]
        status[category] = {
            "available": available,
            "locked":    locked,
            "unlocked":  len(available) > 0,
            "full":      len(locked) == 0,
        }
    return status
