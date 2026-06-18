"""
tests/test_prompt_assembly.py

Unit tests for prompt-assembly logic in domains.build_system_prompt()
and score parsing in scoring.parse_scores().

Pure unit tests — no Anthropic API calls, no Streamlit. Run with:
    pip install -r dev-requirements.txt
    pytest -q
"""

import os
import sys
import re
import warnings

# Flat repo layout — add the project root (parent of tests/) to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip the live model probe so importing `agent` makes no real API call.
os.environ.setdefault("SCHA_SKIP_MODEL_RESOLUTION", "1")

from domains import build_system_prompt, DOMAINS
from scoring import parse_scores
import agent as agent_mod


# Markers for each conditionally-injected block
NORTH_STAR_MARKER  = "USER NORTH STAR VISION"
SOURCING_MARKER    = "GEOPOLITICAL & SOURCING FOOTPRINT (USER-PROVIDED)"
CBA_MARKER         = "COST-BENEFIT ANALYSIS (CBA)"
EXEC_MARKER        = "EXECUTIVE TRACK"
CYBER_BENCH_MARKER = "Cyber Resilience (sub-dimension)"
CYBER_INSTR_MARKER = "CYBER RESILIENCE (REQUIRED SUB-DIMENSION OF RISK & RESILIENCE)"

EXPECTED_DOMAINS = [
    "demand", "procurement", "manufacturing", "inventory",
    "logistics", "warehousing", "risk", "sustainability",
]


# ── (1) Block inclusion / exclusion ────────────────────────────────────────────

def test_cba_block_excluded_by_default():
    assert CBA_MARKER not in build_system_prompt("general")

def test_cba_block_included_when_opted_in():
    assert CBA_MARKER in build_system_prompt("general", include_cba=True)

def test_executive_sections_excluded_for_analyst():
    p = build_system_prompt("general", persona="analyst")
    assert EXEC_MARKER not in p
    assert "STRATEGIC SCENARIO COMPARISON" not in p
    assert "SUPPLY CHAIN MATURITY ROADMAP" not in p

def test_executive_sections_included_for_executive():
    p = build_system_prompt("general", persona="executive")
    assert EXEC_MARKER in p
    assert "STRATEGIC SCENARIO COMPARISON" in p
    assert "SUPPLY CHAIN MATURITY ROADMAP" in p

def test_north_star_excluded_when_blank():
    assert NORTH_STAR_MARKER not in build_system_prompt("general")
    assert NORTH_STAR_MARKER not in build_system_prompt("general", north_star="   ")

def test_north_star_included_when_provided():
    p = build_system_prompt("general", north_star="98% OTIF in two years")
    assert NORTH_STAR_MARKER in p
    assert "98% OTIF in two years" in p

def test_sourcing_excluded_when_blank():
    assert SOURCING_MARKER not in build_system_prompt("general")
    assert SOURCING_MARKER not in build_system_prompt(
        "general", sourcing_exposure="  ", sourcing_footprint="")

def test_sourcing_included_with_either_field():
    p1 = build_system_prompt("general", sourcing_exposure="40% China-origin")
    assert SOURCING_MARKER in p1 and "40% China-origin" in p1
    p2 = build_system_prompt("general", sourcing_footprint="reshoring in progress")
    assert SOURCING_MARKER in p2 and "reshoring in progress" in p2

def test_cyber_always_present():
    # Cyber resilience is part of the base prompt — unconditional, not input-gated.
    p = build_system_prompt("general")
    assert CYBER_BENCH_MARKER in p
    assert CYBER_INSTR_MARKER in p


# ── (2) JSON scores contract guard ──────────────────────────────────────────────

def test_scores_json_contract_is_exactly_eight_domains():
    p = build_system_prompt("general")
    m = re.search(r'"scores"\s*:\s*\{([^}]*)\}', p)
    assert m, "scores JSON template not found in prompt"
    keys = re.findall(r'"(\w+)"\s*:\s*0-100', m.group(1))
    assert keys == EXPECTED_DOMAINS, keys

def test_no_cyber_or_ai_key_leaked_into_scores_json():
    p = build_system_prompt("general")
    m = re.search(r'"scores"\s*:\s*\{([^}]*)\}', p)
    keys = re.findall(r'"(\w+)"\s*:\s*0-100', m.group(1))
    assert "cyber" not in keys
    assert "ai" not in keys

def test_domains_module_matches_contract():
    # The DOMAINS list and the JSON template must agree on the same 8 keys.
    assert [d["key"] for d in DOMAINS] == EXPECTED_DOMAINS


# ── (3) parse_scores() clamping + graceful None ─────────────────────────────────

def test_parse_scores_clamps_to_0_100():
    text = (
        'Here is the result:\n'
        '{"scores":{"demand":-10,"procurement":120,"manufacturing":50,'
        '"inventory":50,"logistics":50,"warehousing":50,"risk":50,'
        '"sustainability":50},"overall":150}\n'
        'EXECUTIVE SUMMARY ...'
    )
    data = parse_scores(text)
    assert data is not None
    assert data["scores"]["demand"] == 0          # -10 clamped up
    assert data["scores"]["procurement"] == 100   # 120 clamped down
    assert data["scores"]["manufacturing"] == 50
    assert data["overall"] == 100                 # 150 clamped down

def test_parse_scores_returns_none_when_no_json():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert parse_scores("No JSON anywhere in this narrative.") is None

def test_parse_scores_returns_none_on_malformed_json():
    # Regex matches (contains "overall":NN) but the JSON is invalid (trailing comma).
    text = '{"scores":{"demand":10,},"overall":50}'
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert parse_scores(text) is None


# ── (4) Default analyst regression guard ────────────────────────────────────────

def test_default_analyst_prompt_has_no_user_injected_blocks():
    p = build_system_prompt()  # defaults: general vertical, analyst, no CBA, no inputs
    for marker in (NORTH_STAR_MARKER, SOURCING_MARKER, CBA_MARKER, EXEC_MARKER):
        assert marker not in p, f"unexpected block leaked into default prompt: {marker}"

def test_default_analyst_prompt_has_base_content():
    p = build_system_prompt()
    assert "2026 WORLD-CLASS KPI BENCHMARKS BY DOMAIN" in p
    assert "BENCHMARK TRANSPARENCY (REQUIRED)" in p
    assert CYBER_INSTR_MARKER in p  # cyber is base content — always present


# ── (5) Model configuration ─────────────────────────────────────────────────────

def test_model_preference_is_nonempty_list_of_strings():
    assert isinstance(agent_mod.MODEL_PREFERENCE, list)
    assert len(agent_mod.MODEL_PREFERENCE) >= 1
    assert all(isinstance(m, str) and m for m in agent_mod.MODEL_PREFERENCE)

def test_resolved_model_is_a_string():
    # With SCHA_SKIP_MODEL_RESOLUTION set, MODEL = MODEL_PREFERENCE[0] (no API call).
    assert isinstance(agent_mod.MODEL, str) and agent_mod.MODEL
