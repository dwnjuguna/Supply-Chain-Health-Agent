"""Supply Chain Health Agent (SCHA) — free-tier MCP server (stdio transport).

Exposes the three free tools (run_assessment, get_assessment_history,
get_benchmarks) over the Model Context Protocol on the stdio transport. No HTTP,
no auth — that is the Pro server's job (a future pro_server.py).

This module is a thin, stateless bridge. All real work lives in the existing
engine (``agent.py`` / ``domains.py`` / ``scoring.py`` / ``verticals.py``); every
tool here just validates intent, calls the corresponding engine function(s), and
shapes the result to match the ``outputSchema`` declared in ``schemas.py``. Each
tool call is fully self-contained: it carries everything it needs and leaves no
session state behind.

Run directly (``python -m mcp_server.server`` or ``python server.py``) to serve
on stdio, e.g. from a desktop MCP client's launch config.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Make the engine importable and relative paths resolve, regardless of the
# working directory the MCP client launches us from.
#
# Layout:  <nested>/agent.py, domains.py, scoring.py, verticals.py, personas.py
#          <nested>/mcp_server/server.py    <- this file
#          <nested>/mcp_server/schemas.py
#
# _REPO_ROOT is the nested project folder (parent of mcp_server/). The engine
# loads its API key via dotenv relative to the process CWD, so we both add the
# root to sys.path AND chdir into it so .env discovery and any future
# persistence resolve predictably.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
os.chdir(_REPO_ROOT)

from mcp.server import Server  # noqa: E402
from mcp.server.stdio import stdio_server  # noqa: E402
from mcp.types import CallToolResult, TextContent, Tool  # noqa: E402

# Tool definitions (single source of truth) ---------------------------------
from mcp_server.schemas import FREE_TOOLS, TOOLS_BY_NAME  # noqa: E402

# The engine. Importing is side-effect-light: SupplyChainHealthAgent constructs
# an Anthropic client only when instantiated, and makes no network call until an
# assessment actually runs.
from agent import SupplyChainHealthAgent  # noqa: E402
from domains import DOMAINS  # noqa: E402
from scoring import parse_scores, interpret_score  # noqa: E402
from verticals import VERTICAL_PRESETS  # noqa: E402


SERVER_NAME = "supply-chain-health-agent"
SERVER_VERSION = "1.0.0"

# Free tier only ever serves these three.
_FREE_TOOL_NAMES = {tool["name"] for tool in FREE_TOOLS}


# ===========================================================================
# Errors
# ===========================================================================

class ToolError(Exception):
    """Raised by a tool handler to signal a clean, user-facing failure.

    The dispatcher converts this into a well-formed MCP error result
    (isError=True) rather than letting a raw traceback escape.
    """


# ===========================================================================
# Input validation helpers (lightweight, schema-aligned)
#
# The JSON Schema in schemas.py is the contract; many MCP clients validate
# against it before dispatch. We re-check the handful of invariants each tool
# actually depends on so the server fails cleanly even for clients that don't.
# ===========================================================================

def _require_dict(arguments: Any) -> Dict[str, Any]:
    if arguments is None:
        return {}
    if not isinstance(arguments, dict):
        raise ToolError("Tool arguments must be a JSON object.")
    return arguments


def _opt_str(args: Dict[str, Any], key: str) -> str | None:
    val = args.get(key)
    if val is None:
        return None
    if not isinstance(val, str):
        raise ToolError(f"'{key}' must be a string.")
    return val


def _opt_int(args: Dict[str, Any], key: str, *, minimum: int, maximum: int) -> int | None:
    val = args.get(key)
    if val is None:
        return None
    if isinstance(val, bool) or not isinstance(val, int):
        raise ToolError(f"'{key}' must be an integer.")
    if not (minimum <= val <= maximum):
        raise ToolError(f"'{key}' must be between {minimum} and {maximum}.")
    return val


# ===========================================================================
# SCHA reference data
#
# The 8 domain keys map onto the SCOR finding categories the schema exposes.
# The 2026 world-class KPI benchmarks are the structured form of the benchmark
# prose carried in domains.SYSTEM_PROMPT_BASE — kept here so get_benchmarks can
# return strictly-typed records (the engine has no structured benchmark table).
# ===========================================================================

_DOMAIN_CATEGORY = {
    "demand": "demand_planning",
    "procurement": "procurement",
    "manufacturing": "manufacturing",
    "inventory": "inventory",
    "logistics": "logistics",
    "warehousing": "warehousing",
    "risk": "risk_resilience",
    "sustainability": "sustainability",
}

_DOMAIN_BENCHMARKS: Dict[str, List[Dict[str, str]]] = {
    "demand": [
        {"metric": "Forecast Accuracy", "unit": "%", "world_class": "≥85–90%", "industry_average": "60–70%"},
        {"metric": "MAPE", "unit": "%", "world_class": "<10%", "industry_average": "20–30%"},
        {"metric": "Forecast Bias", "unit": "%", "world_class": "within ±2%", "industry_average": "±8–15%"},
    ],
    "procurement": [
        {"metric": "Supplier On-Time Delivery (OTD)", "unit": "%", "world_class": "≥95%", "industry_average": "80–85%"},
        {"metric": "Spend Under Management", "unit": "%", "world_class": "≥80%", "industry_average": "50–60%"},
        {"metric": "Supplier Defect Rate", "unit": "PPM", "world_class": "<500 PPM", "industry_average": "1,500–3,000 PPM"},
        {"metric": "Supplier ESG Assessment Coverage", "unit": "% of Tier-1", "world_class": "≥80%", "industry_average": "n/a"},
    ],
    "manufacturing": [
        {"metric": "Overall Equipment Effectiveness (OEE)", "unit": "%", "world_class": "≥85%", "industry_average": "60–65%"},
        {"metric": "First-Pass Yield (FPY)", "unit": "%", "world_class": "≥98%", "industry_average": "92–95%"},
        {"metric": "Schedule Adherence", "unit": "%", "world_class": "≥95%", "industry_average": "n/a"},
        {"metric": "Capacity Utilization", "unit": "%", "world_class": "75–85%", "industry_average": "n/a"},
    ],
    "inventory": [
        {"metric": "Inventory Turns", "unit": "turns/year", "world_class": "8–12x (fast-moving)", "industry_average": "3–5x (pharma/capital)"},
        {"metric": "Stockout Rate", "unit": "%", "world_class": "<1%", "industry_average": "4–8%"},
        {"metric": "Excess & Obsolete (E&O)", "unit": "% of total", "world_class": "<2%", "industry_average": "5–10%"},
        {"metric": "Inventory Accuracy", "unit": "%", "world_class": "≥99%", "industry_average": "85–95%"},
    ],
    "logistics": [
        {"metric": "OTIF", "unit": "%", "world_class": "95–98%", "industry_average": "n/a"},
        {"metric": "Freight Cost as % of Revenue", "unit": "%", "world_class": "<5% (B2C); <3% (B2B)", "industry_average": "n/a"},
        {"metric": "Perfect Order Rate", "unit": "%", "world_class": "≥98%", "industry_average": "90–95%"},
    ],
    "warehousing": [
        {"metric": "Order Accuracy Rate", "unit": "%", "world_class": "≥99.9%", "industry_average": "96–98%"},
        {"metric": "Warehouse Utilization", "unit": "%", "world_class": "80–85%", "industry_average": "n/a"},
        {"metric": "Lines Picked per Hour", "unit": "lines/hr", "world_class": "500–1000+ (automated)", "industry_average": "150–250 (manual)"},
    ],
    "risk": [
        {"metric": "BCP Coverage", "unit": "% of critical nodes", "world_class": "≥95%", "industry_average": "n/a"},
        {"metric": "Time-to-Recover (TTR)", "unit": "weeks", "world_class": "2–4 weeks", "industry_average": "n/a"},
        {"metric": "Single-Source Dependency", "unit": "% of critical components", "world_class": "<15%", "industry_average": "n/a"},
    ],
    "sustainability": [
        {"metric": "Scope 3 Emissions Tracking", "unit": "% of supply chain", "world_class": "≥80%", "industry_average": "n/a"},
        {"metric": "Supplier ESG Audit Coverage", "unit": "% of Tier-1", "world_class": "≥80%", "industry_average": "n/a"},
        {"metric": "Sustainable Procurement Spend", "unit": "%", "world_class": ">70%", "industry_average": "n/a"},
    ],
}


# ===========================================================================
# Tool implementations
#
# Each returns a plain dict conforming to its tool's outputSchema. The
# dispatcher serializes the dict to JSON for the MCP result payload.
# ===========================================================================

def _tool_run_assessment(args: Dict[str, Any]) -> Dict[str, Any]:
    """Bridge run_assessment -> SupplyChainHealthAgent assessment run."""
    org_name = args.get("org_name")
    if not isinstance(org_name, str) or not org_name.strip():
        raise ToolError("'org_name' is required and must be a non-empty string.")
    org_name = org_name.strip()

    vertical = args.get("vertical")
    if not isinstance(vertical, str) or vertical not in VERTICAL_PRESETS:
        raise ToolError(
            "'vertical' is required and must be one of: "
            + ", ".join(sorted(VERTICAL_PRESETS))
        )

    persona = args.get("persona")
    if persona not in ("analyst", "executive"):
        raise ToolError("'persona' is required and must be 'analyst' or 'executive'.")

    # Accepted and validated; the engine has no north_star parameter yet, so it
    # is reserved for a future wiring rather than silently dropped.
    _opt_str(args, "north_star")

    domain_responses = args.get("domain_responses")
    if domain_responses is not None:
        if not isinstance(domain_responses, dict):
            raise ToolError("'domain_responses' must be an object.")
        for k, v in domain_responses.items():
            if not isinstance(v, str):
                raise ToolError(f"domain_responses['{k}'] must be a string.")

    agent = SupplyChainHealthAgent(vertical=vertical, persona=persona)

    try:
        if domain_responses:
            result = agent.run_custom_assessment(domain_responses)
        else:
            result = agent.run_general_assessment()
    except Exception as exc:  # engine/LLM/network failure
        raise ToolError(f"Assessment failed while running the engine: {exc}") from exc

    # The engine swallows API errors into an envelope with empty raw + None
    # scores; surface that as a clean tool error instead of an all-zero report.
    if not (result.get("raw") or "").strip() and result.get("scores") is None:
        raise ToolError(result.get("narrative") or "Assessment engine returned no result.")

    # Parse scores from the result. The engine pre-parses into result['scores'];
    # fall back to parse_scores() on the raw text if that came back empty.
    parsed = result.get("scores") or parse_scores(result.get("raw", "") or "")
    inner = parsed.get("scores", {}) if isinstance(parsed, dict) else {}
    overall = parsed.get("overall") if isinstance(parsed, dict) else None

    # Build a strictly-typed domain_scores map: all 8 keys, ints clamped 0-100.
    domain_scores: Dict[str, int] = {}
    for d in DOMAINS:
        key = d["key"]
        try:
            domain_scores[key] = max(0, min(100, int(inner.get(key))))
        except (TypeError, ValueError):
            domain_scores[key] = 0

    if overall is None:
        overall = round(sum(domain_scores.values()) / len(domain_scores)) if domain_scores else 0
    overall = max(0, min(100, int(overall)))

    narrative = result.get("narrative", "") or ""
    action_pack = _extract_action_pack(narrative)

    # One finding per domain; severity mapped via interpret_score().
    findings: List[Dict[str, Any]] = []
    for idx, d in enumerate(DOMAINS, start=1):
        key = d["key"]
        label = d["label"]
        score = domain_scores[key]
        rating, description = interpret_score(score)
        findings.append(
            {
                "id": f"SCHA-{idx:03d}",
                "title": f"{label}: {score}/100 — {rating}",
                "severity": _severity_for(rating, score),
                "category": _DOMAIN_CATEGORY[key],
                "domain": key,
                "detail": f"{label} scored {score}/100. {description}.",
            }
        )

    created_at = _utc_now_iso()
    stamp = created_at.replace("-", "").replace(":", "")
    assessment_id = f"{_slugify(org_name)}-{stamp}"

    return {
        "assessment_id": assessment_id,
        "created_at": created_at,
        "overall_score": overall,
        "domain_scores": domain_scores,
        "narrative": narrative,
        "action_pack": action_pack,
        "benchmarks_used": [d["label"] for d in DOMAINS],
        "findings": findings,
    }


def _tool_get_assessment_history(args: Dict[str, Any]) -> Dict[str, Any]:
    """Bridge get_assessment_history -> (no persistence layer yet).

    Validated for input shape, but always returns an empty page for now.
    Server-side persistence of assessment runs will be added in a future PR;
    until then this tool is a well-formed no-op.
    """
    _opt_str(args, "org_name")
    _opt_str(args, "cursor")
    _opt_int(args, "limit", minimum=1, maximum=200)

    return {
        "assessments": [],
        "page_info": {"has_more": False},
    }


def _tool_get_benchmarks(args: Dict[str, Any]) -> Dict[str, Any]:
    """Bridge get_benchmarks -> 2026 KPI benchmark table + VERTICAL_PRESETS."""
    domain = _opt_str(args, "domain")
    if domain is not None and domain not in _DOMAIN_BENCHMARKS:
        raise ToolError("'domain' must be one of: " + ", ".join(_DOMAIN_BENCHMARKS))

    vertical = _opt_str(args, "vertical")
    if vertical is not None and vertical not in VERTICAL_PRESETS:
        raise ToolError(
            "'vertical' must be one of: " + ", ".join(sorted(VERTICAL_PRESETS))
        )

    _opt_str(args, "cursor")  # accepted; offset paging not implemented
    limit = _opt_int(args, "limit", minimum=1, maximum=200) or 25

    labels = {d["key"]: d["label"] for d in DOMAINS}
    vertical_note = VERTICAL_PRESETS.get(vertical, "") if vertical else ""

    benchmarks: List[Dict[str, Any]] = []
    domain_keys = [domain] if domain else [d["key"] for d in DOMAINS]
    for dkey in domain_keys:
        label = labels.get(dkey, dkey)
        for spec in _DOMAIN_BENCHMARKS.get(dkey, []):
            description = f"{label} — 2026 world-class KPI benchmark."
            record: Dict[str, Any] = {
                "id": f"{dkey}:{_slugify(spec['metric'])}",
                "domain": dkey,
                "metric": spec["metric"],
                "unit": spec["unit"],
                "world_class": spec["world_class"],
            }
            if spec.get("industry_average") and spec["industry_average"] != "n/a":
                record["industry_average"] = spec["industry_average"]
            if vertical:
                record["vertical"] = vertical
                if vertical_note:
                    description += f" Vertical context ({vertical}): {vertical_note}"
            record["description"] = description
            benchmarks.append(record)

    page = benchmarks[:limit]
    return {
        "benchmarks": page,
        "page_info": {"has_more": len(benchmarks) > limit},
    }


# Dispatch table: tool name -> handler. Lookups are gated by TOOLS_BY_NAME so an
# unknown or non-free tool name can never reach a handler.
_HANDLERS = {
    "run_assessment": _tool_run_assessment,
    "get_assessment_history": _tool_get_assessment_history,
    "get_benchmarks": _tool_get_benchmarks,
}


# ===========================================================================
# Small formatting helpers
# ===========================================================================

def _utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(name: str) -> str:
    """Lowercase, collapse non-alphanumerics to single underscores."""
    slug = "".join(c if c.isalnum() else "_" for c in name.strip().lower())
    slug = "_".join(filter(None, slug.split("_")))
    return slug or "org"


def _extract_action_pack(narrative: str) -> str:
    """Slice out the PRIORITY RECOMMENDATIONS section, or fall back to the whole text."""
    if not narrative:
        return ""
    idx = narrative.upper().find("PRIORITY RECOMMENDATIONS")
    if idx != -1:
        return narrative[idx:].strip()
    return narrative


def _severity_for(rating: str, score: int) -> str:
    """Map an interpret_score() rating onto the schema's severity vocabulary."""
    if rating == "Excellent":
        return "info"
    if rating == "Good":
        return "low"
    if rating == "Fair":
        return "medium"
    # "At Risk"
    return "critical" if score < 20 else "high"


# ===========================================================================
# MCP server wiring
# ===========================================================================

server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """Advertise the three free-tier tools, built straight from schemas.py."""
    tools: List[Tool] = []
    for spec in FREE_TOOLS:
        tools.append(
            Tool(
                name=spec["name"],
                title=spec.get("title"),
                description=spec["description"],
                inputSchema=spec["inputSchema"],
                outputSchema=spec.get("outputSchema"),
            )
        )
    return tools


@server.call_tool()
async def call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> Dict[str, Any] | CallToolResult:
    """Dispatch a tool call through TOOLS_BY_NAME and return its result.

    On success the handler returns a plain dict conforming to the tool's
    outputSchema; the low-level Server emits it as structuredContent (plus a
    JSON text block) and validates it against the schema. On failure we return
    an explicit CallToolResult with isError=True — a well-formed error result,
    never a raw traceback.
    """
    # Gate: must be a known tool AND served by the free tier.
    if name not in TOOLS_BY_NAME or name not in _FREE_TOOL_NAMES:
        return _error_result(f"Unknown or unavailable tool: {name!r}")

    handler = _HANDLERS.get(name)
    if handler is None:  # defensive: schema present but no bridge wired
        return _error_result(f"Tool {name!r} is not implemented on this server.")

    try:
        args = _require_dict(arguments)
        # Run the (synchronous, possibly long/blocking) engine bridge off the
        # event loop so the stdio transport stays responsive.
        return await asyncio.to_thread(handler, args)
    except ToolError as exc:
        return _error_result(str(exc))
    except Exception as exc:  # last-resort guard — never leak a raw traceback
        return _error_result(f"Internal error in {name!r}: {exc}")


def _error_result(message: str) -> CallToolResult:
    """Build a well-formed MCP error result with a machine-readable payload."""
    return CallToolResult(
        isError=True,
        content=[
            TextContent(
                type="text",
                text=json.dumps({"error": message}, ensure_ascii=False),
            )
        ],
    )


# ===========================================================================
# Entry point
# ===========================================================================

async def _serve() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Serve the free tier over stdio until the client disconnects."""
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
