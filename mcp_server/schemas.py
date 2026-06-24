"""Tool schemas for the Supply Chain Health Agent (SCHA) MCP server.

This module is the single source of truth for every tool exposed by both the
free (stdio) and Pro (Streamable HTTP) transports. It contains nothing but data:
JSON Schema (draft 2020-12) definitions for each tool's inputs and outputs.

Design constraints (enforced here, relied on by the transports):
  * Model-agnostic. No assumption about which LLM or client calls these tools.
    Schemas describe data, not prompts, and avoid any Claude/Anthropic-specific
    field, convention, or naming.
  * Strictly typed. Every object sets ``additionalProperties: False``, every
    field declares a ``type``, and constrained fields use ``enum``/``format``/
    bounds so invalid payloads are rejected before reaching tool logic.
  * Stateless. Each tool's ``inputSchema`` carries everything the tool needs to
    execute; no tool depends on a prior call within the same session. Server-side
    persistence (assessment history) is addressed by explicit identifiers in the
    input, never by hidden session state.

Each tool entry is a dict with the keys MCP clients expect:
  name, title, description, inputSchema, outputSchema, plus a local ``tier`` key
  ("free" | "pro") the transports use to decide what to advertise.
"""

from __future__ import annotations

from typing import Any, Dict, List

# JSON Schema dialect used by every schema below.
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


# ---------------------------------------------------------------------------
# Reusable sub-schemas
#
# Defined once and referenced inline (by value) so each tool schema remains a
# self-contained document — MCP clients receive fully-expanded schemas with no
# external ``$ref`` resolution required.
# ---------------------------------------------------------------------------

_SEVERITY = {
    "type": "string",
    "enum": ["info", "low", "medium", "high", "critical"],
    "description": "Relative impact of a finding, lowest to highest.",
}

_ISO_TIMESTAMP = {
    "type": "string",
    "format": "date-time",
    "description": "ISO 8601 / RFC 3339 timestamp in UTC, e.g. '2026-06-22T14:30:00Z'.",
}

# Industry vertical the assessment is scoped to.
_VERTICAL = {
    "type": "string",
    "enum": [
        "retail",
        "pharma",
        "automotive",
        "semiconductor",
        "cpg",
        "aerospace",
        "healthcare",
        "general",
        "food_beverage",
        "technology",
        "apparel",
    ],
    "description": "Industry vertical the assessment is scoped to.",
}

# Output persona / track shaping depth and language.
_PERSONA = {
    "type": "string",
    "enum": ["analyst", "executive"],
    "description": "Output track: practitioner analyst or C-suite executive.",
}

# Single supply chain domain key (the 8 SCOR-aligned assessment domains).
_DOMAIN_KEY = {
    "type": "string",
    "enum": [
        "demand",
        "procurement",
        "manufacturing",
        "inventory",
        "logistics",
        "warehousing",
        "risk",
        "sustainability",
    ],
    "description": "Supply chain domain key.",
}

# Free-text organizational inputs keyed by domain. All keys optional; the agent
# scores domains with no input using industry-benchmark assumptions.
_DOMAIN_RESPONSES = {
    "type": "object",
    "additionalProperties": False,
    "description": "Free-text organizational inputs keyed by supply chain domain.",
    "properties": {
        "demand": {"type": "string", "maxLength": 5000, "description": "Demand Planning & Forecasting."},
        "procurement": {"type": "string", "maxLength": 5000, "description": "Procurement & Sourcing."},
        "manufacturing": {"type": "string", "maxLength": 5000, "description": "Manufacturing & Production."},
        "inventory": {"type": "string", "maxLength": 5000, "description": "Inventory Management."},
        "logistics": {"type": "string", "maxLength": 5000, "description": "Logistics & Transportation."},
        "warehousing": {"type": "string", "maxLength": 5000, "description": "Warehousing & Fulfillment."},
        "risk": {"type": "string", "maxLength": 5000, "description": "Risk & Resilience."},
        "sustainability": {"type": "string", "maxLength": 5000, "description": "Sustainability & ESG."},
    },
}

# Per-domain health scores. All eight present on every completed assessment.
_DOMAIN_SCORES = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "demand",
        "procurement",
        "manufacturing",
        "inventory",
        "logistics",
        "warehousing",
        "risk",
        "sustainability",
    ],
    "description": "Health score (0-100) per supply chain domain.",
    "properties": {
        "demand": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Demand Planning & Forecasting."},
        "procurement": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Procurement & Sourcing."},
        "manufacturing": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Manufacturing & Production."},
        "inventory": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Inventory Management."},
        "logistics": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Logistics & Transportation."},
        "warehousing": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Warehousing & Fulfillment."},
        "risk": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Risk & Resilience."},
        "sustainability": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Sustainability & ESG."},
    },
}

# A single assessment finding.
_FINDING = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "title", "severity", "category"],
    "properties": {
        "id": {
            "type": "string",
            "description": "Stable identifier for the finding (e.g. 'SCHA-001').",
        },
        "title": {
            "type": "string",
            "description": "Short summary of the issue.",
        },
        "severity": _SEVERITY,
        "category": {
            "type": "string",
            "enum": [
                "demand_planning",
                "procurement",
                "manufacturing",
                "inventory",
                "logistics",
                "warehousing",
                "risk_resilience",
                "sustainability",
            ],
            "description": "SCOR domain category the finding relates to.",
        },
        "domain": {
            "type": "string",
            "description": "Domain key the finding applies to, if specific.",
        },
        "detail": {
            "type": "string",
            "description": "Full explanation of the finding.",
        },
        "recommendation": {
            "type": "string",
            "description": "Suggested remediation, if any.",
        },
    },
}

# Standard pagination inputs. Stateless cursor-based paging.
_PAGINATION_PROPERTIES = {
    "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 200,
        "default": 25,
        "description": "Maximum number of records to return.",
    },
    "cursor": {
        "type": "string",
        "maxLength": 512,
        "description": "Opaque pagination cursor returned by a previous call. "
        "Omit to start from the first page.",
    },
}

# Standard pagination output block, embedded in list-returning tools.
_PAGE_INFO = {
    "type": "object",
    "additionalProperties": False,
    "required": ["has_more"],
    "properties": {
        "has_more": {
            "type": "boolean",
            "description": "True when more records exist beyond this page.",
        },
        "next_cursor": {
            "type": "string",
            "description": "Cursor to pass on the next call. Present only when has_more is true.",
        },
    },
}

# Summary record for a completed assessment, used in list responses.
_ASSESSMENT_SUMMARY = {
    "type": "object",
    "additionalProperties": False,
    "required": ["assessment_id", "org_name", "created_at", "overall_score"],
    "properties": {
        "assessment_id": {
            "type": "string",
            "description": "Unique identifier for the assessment run.",
        },
        "org_name": {
            "type": "string",
            "description": "Name of the organization that was assessed.",
        },
        "vertical": _VERTICAL,
        "persona": _PERSONA,
        "created_at": _ISO_TIMESTAMP,
        "overall_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Overall health score, 0 (worst) to 100 (best).",
        },
        "finding_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of findings produced by the assessment.",
        },
    },
}


def _object(properties: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    """Build a strict top-level object schema with the shared dialect declared."""
    return {
        "$schema": SCHEMA_DIALECT,
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


# ===========================================================================
# FREE TIER TOOLS
# ===========================================================================

RUN_ASSESSMENT = {
    "name": "run_assessment",
    "title": "Run Supply Chain Assessment",
    "tier": "free",
    "description": (
        "Assess an organization's supply chain health against SCOR and Gartner "
        "benchmarks and return an overall score, per-domain scores, a narrative "
        "report, and a prioritized action pack. All inputs are supplied with the "
        "call; no prior state is required."
    ),
    "inputSchema": _object(
        properties={
            "org_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Name of the organization being assessed.",
            },
            "vertical": _VERTICAL,
            "persona": _PERSONA,
            "north_star": {
                "type": "string",
                "maxLength": 500,
                "description": "Optional guiding objective or strategic priority for the assessment.",
            },
            "domain_responses": _DOMAIN_RESPONSES,
        },
        required=["org_name", "vertical", "persona"],
    ),
    "outputSchema": _object(
        properties={
            "assessment_id": {
                "type": "string",
                "description": "Identifier for this assessment run; usable with get_assessment_history.",
            },
            "created_at": _ISO_TIMESTAMP,
            "overall_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Overall supply chain health score, 0 (worst) to 100 (best).",
            },
            "domain_scores": _DOMAIN_SCORES,
            "narrative": {
                "type": "string",
                "description": "Full natural-language assessment report.",
            },
            "action_pack": {
                "type": "string",
                "description": "Prioritized, actionable recommendations derived from the assessment.",
            },
            "benchmarks_used": {
                "type": "array",
                "description": "Identifiers or names of the benchmarks applied during scoring.",
                "items": {"type": "string"},
            },
            "findings": {
                "type": "array",
                "description": "Individual issues discovered during the assessment.",
                "items": _FINDING,
            },
        },
        required=[
            "assessment_id",
            "created_at",
            "overall_score",
            "domain_scores",
            "narrative",
            "action_pack",
            "benchmarks_used",
        ],
    ),
}

GET_ASSESSMENT_HISTORY = {
    "name": "get_assessment_history",
    "title": "Get Assessment History",
    "tier": "free",
    "description": (
        "List previously persisted assessment runs, most recent first, with "
        "optional filtering by organization name. Pagination is cursor-based."
    ),
    "inputSchema": _object(
        properties={
            "org_name": {
                "type": "string",
                "maxLength": 200,
                "description": "Restrict results to assessments of an organization with this exact name.",
            },
            **_PAGINATION_PROPERTIES,
        },
        required=[],
    ),
    "outputSchema": _object(
        properties={
            "assessments": {
                "type": "array",
                "description": "Matching assessment summaries, newest first.",
                "items": _ASSESSMENT_SUMMARY,
            },
            "page_info": _PAGE_INFO,
        },
        required=["assessments", "page_info"],
    ),
}

GET_BENCHMARKS = {
    "name": "get_benchmarks",
    "title": "Get Benchmarks",
    "tier": "free",
    "description": (
        "List the reference KPI benchmarks SCHA scores supply chains against, "
        "optionally filtered by domain and/or industry vertical. Read-only "
        "catalog lookup."
    ),
    "inputSchema": _object(
        properties={
            "domain": {
                **_DOMAIN_KEY,
                "description": "Restrict the catalog to a single supply chain domain.",
            },
            "vertical": {
                **_VERTICAL,
                "description": "Restrict the catalog to benchmarks relevant to a single vertical.",
            },
            **_PAGINATION_PROPERTIES,
        },
        required=[],
    ),
    "outputSchema": _object(
        properties={
            "benchmarks": {
                "type": "array",
                "description": "Matching benchmark definitions.",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["id", "domain", "metric", "unit"],
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Stable benchmark identifier.",
                        },
                        "domain": _DOMAIN_KEY,
                        "vertical": {
                            **_VERTICAL,
                            "description": "Vertical the benchmark is specific to, if any.",
                        },
                        "metric": {
                            "type": "string",
                            "description": "Human-readable metric name, e.g. 'Forecast Accuracy'.",
                        },
                        "unit": {
                            "type": "string",
                            "description": "Unit of the benchmark value, e.g. '%', 'PPM', 'turns/year'.",
                        },
                        "world_class": {
                            "type": "string",
                            "description": "World-class / top-quartile target value or range.",
                        },
                        "industry_average": {
                            "type": "string",
                            "description": "Typical industry-average value or range.",
                        },
                        "description": {
                            "type": "string",
                            "description": "What the benchmark measures and how.",
                        },
                    },
                },
            },
            "page_info": _PAGE_INFO,
        },
        required=["benchmarks", "page_info"],
    ),
}


# ===========================================================================
# PRO TIER TOOLS
#
# None defined yet — reserved for a future Pro transport. PRO_TOOLS is empty.
# ===========================================================================


# ===========================================================================
# Registries
#
# The transports import these. The free (stdio) server advertises FREE_TOOLS;
# a future Pro server would advertise ALL_TOOLS. Lookups go through TOOLS_BY_NAME.
# ===========================================================================

FREE_TOOLS: List[Dict[str, Any]] = [
    RUN_ASSESSMENT,
    GET_ASSESSMENT_HISTORY,
    GET_BENCHMARKS,
]

PRO_TOOLS: List[Dict[str, Any]] = []

ALL_TOOLS: List[Dict[str, Any]] = FREE_TOOLS + PRO_TOOLS

TOOLS_BY_NAME: Dict[str, Dict[str, Any]] = {tool["name"]: tool for tool in ALL_TOOLS}


__all__ = [
    "SCHEMA_DIALECT",
    "FREE_TOOLS",
    "PRO_TOOLS",
    "ALL_TOOLS",
    "TOOLS_BY_NAME",
    "RUN_ASSESSMENT",
    "GET_ASSESSMENT_HISTORY",
    "GET_BENCHMARKS",
]
