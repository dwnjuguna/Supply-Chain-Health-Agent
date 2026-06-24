"""
alerts/risk_monitor.py

Proactive risk monitor for Supply Chain Health Agent Phase 2.
Uses Claude + live web search to autonomously scan for supply chain
risks relevant to a given vertical and deliver alerts via Slack/email.

Phase 2 Feature — requires Pro tier or above.

How it works:
  1. Claude searches the web for live supply chain risk signals
  2. Signals are scored by severity and relevance
  3. High/Medium signals trigger Slack and/or email alerts
  4. All alerts are logged to the SQLite database
  5. Can be run on-demand or scheduled via scheduler.py
"""

import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from datetime import datetime, timezone

from agent import MODEL  # single source of truth for the Claude model id


# ── Web search tool ───────────────────────────────────────────────────────────
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
}


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    try:
        import streamlit as st
        api_key = st.secrets.get("ANTHROPIC_API_KEY", api_key)
    except Exception:
        pass
    return anthropic.Anthropic(api_key=api_key)


def _extract_text(response) -> str:
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text" and block.text:
            parts.append(block.text)
    return "\n".join(parts).strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Core risk scanning ────────────────────────────────────────────────────────

def scan_for_risks(
    vertical: str = "general",
    org_context: str = "",
    max_signals: int = 5,
) -> list:
    """
    Use Claude + web search to autonomously scan for supply chain risks.

    Returns list of dicts:
    {
        "severity":  "High" | "Medium" | "Low",
        "headline":  str,
        "detail":    str,
        "risk_type": str,
        "vertical":  str,
    }
    """
    client = _get_client()

    org_context_block = ""
    if org_context:
        org_context_block = f"\n\nORGANISATION CONTEXT:\n{org_context}\n"

    prompt = (
        f"You are a supply chain risk intelligence analyst. "
        f"Search for the {max_signals} most important supply chain risk signals "
        f"RIGHT NOW that would affect a {vertical} organisation.{org_context_block}\n\n"
        f"Cover: geopolitical disruptions, freight/shipping conditions, "
        f"regulatory changes, commodity price movements, extreme weather events, "
        f"supplier failures, and technology risks.\n\n"
        f"For each signal respond ONLY with a JSON array. "
        f"No markdown fences, no preamble. Example format:\n"
        f'[{{"severity":"High","headline":"...","detail":"...","risk_type":"geopolitical"}}]\n\n'
        f"severity must be exactly: High, Medium, or Low\n"
        f"risk_type must be one of: geopolitical, freight, regulatory, commodity, "
        f"weather, supplier, technology, other\n\n"
        f"Be specific — include figures, dates, and sources where available. "
        f"Only include signals from the last 30 days."
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=(
                "You are a supply chain risk intelligence analyst with access to "
                "real-time web search. Always search before responding. "
                "Return ONLY a valid JSON array — no markdown, no explanation. "
                "Prioritise recency — last 30 days only."
            ),
            messages=[{"role": "user", "content": prompt}],
            tools=[WEB_SEARCH_TOOL],
        )

        raw = _extract_text(response)

        # Strip any accidental markdown fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        # Find the JSON array
        start = raw.find("[")
        end   = raw.rfind("]") + 1
        if start == -1 or end == 0:
            print(f"[RiskMonitor] No JSON array found in response")
            return []

        signals = json.loads(raw[start:end])

        # Validate and clean
        valid = []
        for s in signals:
            if not isinstance(s, dict):
                continue
            valid.append({
                "severity":  s.get("severity", "Medium"),
                "headline":  s.get("headline", "")[:200],
                "detail":    s.get("detail", "")[:500],
                "risk_type": s.get("risk_type", "other"),
                "vertical":  vertical,
                "scanned_at": _now_iso(),
            })

        return valid[:max_signals]

    except json.JSONDecodeError as e:
        print(f"[RiskMonitor] JSON parse error: {e}\nRaw: {raw[:200]}")
        return []
    except Exception as e:
        print(f"[RiskMonitor] Scan failed: {e}")
        return []


def filter_significant_signals(
    signals: list,
    min_severity: str = "Medium",
) -> list:
    """
    Filter signals by minimum severity level.
    min_severity: "High" (only high), "Medium" (high + medium), "Low" (all)
    """
    order = {"High": 3, "Medium": 2, "Low": 1}
    threshold = order.get(min_severity, 2)
    return [s for s in signals if order.get(s.get("severity", "Low"), 1) >= threshold]


def log_alerts_to_db(
    signals: list,
    org_key: str = None,
    vertical: str = "general",
) -> int:
    """
    Log risk alerts to the SQLite database.
    Returns number of alerts logged.
    """
    try:
        from memory.memory_store import init_db, _get_conn, _now
        init_db()
        conn = _get_conn()
        count = 0
        try:
            for signal in signals:
                conn.execute("""
                    INSERT INTO risk_alerts
                        (org_key, vertical, alert_type, severity,
                         headline, detail, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    org_key,
                    vertical,
                    signal.get("risk_type", "other"),
                    signal.get("severity", "Medium"),
                    signal.get("headline", ""),
                    signal.get("detail", ""),
                    _now(),
                ))
                count += 1
            conn.commit()
        finally:
            conn.close()
        return count
    except Exception as e:
        print(f"[RiskMonitor] DB logging failed: {e}")
        return 0


def run_risk_monitor(
    vertical: str = "general",
    org_name: str = "Your Organisation",
    org_key: str = None,
    org_context: str = "",
    slack_webhook: str = None,
    email_to: str = None,
    min_severity: str = "Medium",
    max_signals: int = 5,
) -> dict:
    """
    Full risk monitoring run:
    1. Scan for live risk signals using Claude + web search
    2. Filter by severity
    3. Log to database
    4. Deliver via Slack and/or email

    Returns summary dict with scan results and delivery status.
    """
    print(f"[RiskMonitor] Starting scan for {org_name} ({vertical})...")

    # Step 1: Scan
    all_signals = scan_for_risks(
        vertical=vertical,
        org_context=org_context,
        max_signals=max_signals,
    )
    print(f"[RiskMonitor] Found {len(all_signals)} signals")

    # Step 2: Filter
    significant = filter_significant_signals(all_signals, min_severity)
    print(f"[RiskMonitor] {len(significant)} meet severity threshold ({min_severity}+)")

    # Step 3: Log to DB
    logged = log_alerts_to_db(
        significant,
        org_key=org_key,
        vertical=vertical,
    )
    print(f"[RiskMonitor] Logged {logged} alerts to database")

    # Step 4: Deliver
    slack_ok = email_ok = False

    if significant:
        if slack_webhook:
            from alerts.slack_dispatcher import send_risk_alert
            slack_ok = send_risk_alert(
                webhook_url=slack_webhook,
                org_name=org_name,
                vertical=vertical,
                alerts=significant,
            )
            print(f"[RiskMonitor] Slack delivery: {'✅' if slack_ok else '❌'}")

        if email_to:
            from alerts.email_dispatcher import send_risk_alert_email
            email_ok = send_risk_alert_email(
                to_email=email_to,
                org_name=org_name,
                vertical=vertical,
                alerts=significant,
            )
            print(f"[RiskMonitor] Email delivery: {'✅' if email_ok else '❌'}")
    else:
        print(f"[RiskMonitor] No significant signals — no alerts sent")

    return {
        "total_signals":    len(all_signals),
        "significant":      len(significant),
        "logged":           logged,
        "slack_delivered":  slack_ok,
        "email_delivered":  email_ok,
        "signals":          significant,
        "scanned_at":       _now_iso(),
        "vertical":         vertical,
        "org_name":         org_name,
    }


def get_recent_alerts(
    org_key: str = None,
    vertical: str = None,
    limit: int = 10,
) -> list:
    """
    Retrieve recent alerts from the database.
    """
    try:
        from memory.memory_store import init_db, _get_conn
        init_db()
        conn = _get_conn()
        try:
            if org_key and vertical:
                rows = conn.execute("""
                    SELECT * FROM risk_alerts
                    WHERE org_key = ? AND vertical = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (org_key, vertical, limit)).fetchall()
            elif org_key:
                rows = conn.execute("""
                    SELECT * FROM risk_alerts
                    WHERE org_key = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (org_key, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM risk_alerts
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    except Exception as e:
        print(f"[RiskMonitor] DB query failed: {e}")
        return []
