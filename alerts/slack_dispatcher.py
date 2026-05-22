"""
alerts/slack_dispatcher.py

Slack webhook dispatcher for Supply Chain Health Agent Phase 2.
Sends assessment summaries, risk alerts, and KPI trend notifications
to configured Slack channels via incoming webhooks.

Phase 2 Feature — requires Pro tier or above.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")


def _score_emoji(score: int) -> str:
    if score >= 80: return ":large_green_circle:"
    if score >= 60: return ":large_blue_circle:"
    if score >= 40: return ":large_yellow_circle:"
    return ":red_circle:"


def _delta_emoji(delta: int) -> str:
    if delta > 0:  return f":chart_with_upwards_trend: +{delta}"
    if delta < 0:  return f":chart_with_downwards_trend: {delta}"
    return ":left_right_arrow: 0"


def send_slack_message(webhook_url: str, payload: dict) -> bool:
    """
    Send a raw payload to a Slack webhook URL.
    Returns True on success, False on failure.
    """
    if not webhook_url or not webhook_url.startswith("https://hooks.slack.com/"):
        print(f"[Slack] Invalid webhook URL")
        return False
    try:
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"[Slack] HTTP error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"[Slack] Error: {e}")
        return False


def send_assessment_summary(
    webhook_url: str,
    org_name: str,
    vertical: str,
    overall_score: int,
    domain_scores: dict,
    narrative_snippet: str = "",
    deltas: dict = None,
) -> bool:
    """
    Send a full assessment summary to Slack.
    Includes overall score, domain scores, and optional trend deltas.
    """
    score_emoji = _score_emoji(overall_score)

    # Build domain score rows
    domain_rows = []
    for domain, score in domain_scores.items():
        emoji = _score_emoji(score)
        delta_str = ""
        if deltas and domain in deltas:
            delta_str = f"  {_delta_emoji(deltas[domain])}"
        domain_rows.append(
            f"{emoji} *{domain.replace('_',' ').title()}*: {score}/100{delta_str}"
        )

    # Trim narrative to 300 chars
    snippet = ""
    if narrative_snippet:
        snippet = narrative_snippet[:300].strip()
        if len(narrative_snippet) > 300:
            snippet += "..."

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 Supply Chain Health Assessment — {org_name}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Vertical:*\n{vertical.replace('_',' ').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Score:*\n{score_emoji} *{overall_score}/100*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:*\n{_now()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Assessment:*\nCompleted"
                    },
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Domain Health Scores:*\n" + "\n".join(domain_rows)
                }
            },
        ]
    }

    if snippet:
        payload["blocks"].append({"type": "divider"})
        payload["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Executive Summary:*\n_{snippet}_"
            }
        })

    payload["blocks"].append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": "Supply Chain Health Agent · Powered by Anthropic Claude · "
                    "All assessments are illustrative and directional only."
        }]
    })

    return send_slack_message(webhook_url, payload)


def send_risk_alert(
    webhook_url: str,
    org_name: str,
    vertical: str,
    alerts: list,
) -> bool:
    """
    Send proactive risk alerts to Slack.
    alerts: list of dicts with keys: severity, headline, detail
    """
    if not alerts:
        return True

    severity_emoji = {
        "High":   ":rotating_light:",
        "Medium": ":warning:",
        "Low":    ":information_source:",
    }

    alert_rows = []
    for alert in alerts[:5]:  # Cap at 5 alerts per message
        emoji = severity_emoji.get(alert.get("severity", "Medium"), ":warning:")
        headline = alert.get("headline", "")
        detail   = alert.get("detail", "")
        alert_rows.append(
            f"{emoji} *{alert.get('severity', 'Medium')} — {headline}*"
            + (f"\n>{detail}" if detail else "")
        )

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⚠️ Supply Chain Risk Alert — {org_name}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Vertical:*\n{vertical.replace('_',' ').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Alerts:*\n{len(alerts)} identified"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:*\n{_now()}"
                    },
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Active Risk Signals:*\n\n" + "\n\n".join(alert_rows)
                }
            },
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": "Supply Chain Health Agent · Risk signals sourced via live web search · "
                            "Verify before acting."
                }]
            }
        ]
    }

    return send_slack_message(webhook_url, payload)


def send_kpi_trend_alert(
    webhook_url: str,
    org_name: str,
    improving: list,
    declining: list,
    overall_delta: int,
) -> bool:
    """
    Send a KPI trend notification when scores change significantly.
    """
    if not improving and not declining:
        return True

    delta_emoji = _delta_emoji(overall_delta)

    lines = [f"*Overall Score Change:* {delta_emoji}\n"]

    if improving:
        lines.append(
            ":chart_with_upwards_trend: *Improving:* "
            + ", ".join(d.replace('_', ' ').title() for d in improving)
        )
    if declining:
        lines.append(
            ":chart_with_downwards_trend: *Declining:* "
            + ", ".join(d.replace('_', ' ').title() for d in declining)
        )

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 KPI Trend Update — {org_name}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(lines)
                }
            },
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"Supply Chain Health Agent · {_now()}"
                }]
            }
        ]
    }

    return send_slack_message(webhook_url, payload)
