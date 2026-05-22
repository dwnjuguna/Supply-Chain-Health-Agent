"""
integrations/slack_integration.py

Slack workflow integration for Supply Chain Health Agent Phase 2.
Pushes assessment summaries, 90-day action plans, and risk watch lists
directly into Slack channels — turning insights into team action.

Phase 2 Feature — requires Pro tier or above.

Setup:
  1. Go to api.slack.com/apps and create a new app
  2. Enable Incoming Webhooks
  3. Add a webhook for your target channel
  4. Add SLACK_WEBHOOK_URL to your .env file

Usage:
  from integrations.slack_integration import push_assessment_to_slack
  push_assessment_to_slack(result, org_name="Acme", vertical="automotive")
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from alerts.slack_dispatcher import (
    send_slack_message,
    send_assessment_summary,
    send_risk_alert,
    _now,
    _score_emoji,
)


def _get_webhook_url() -> str:
    """Get Slack webhook URL from environment."""
    url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not url:
        print(
            "[Slack Integration] SLACK_WEBHOOK_URL not set.\n"
            "Add it to your .env file:\n"
            "  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..."
        )
    return url


def push_assessment_to_slack(
    result: dict,
    org_name: str = "Your Organisation",
    vertical: str = "general",
    webhook_url: str = None,
    include_action_plan: bool = True,
    include_risks: bool = True,
) -> dict:
    """
    Push a complete assessment to Slack.
    Sends up to 3 messages: summary, action plan, risk watch list.

    Returns dict with keys: summary, action_plan, risks (bool success each).
    """
    url = webhook_url or _get_webhook_url()
    if not url:
        return {"summary": False, "action_plan": False, "risks": False}

    scores_data   = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall       = scores_data.get("overall", 0)
    narrative     = result.get("narrative", "")
    action_pack   = result.get("action_pack", {})

    outcomes = {"summary": False, "action_plan": False, "risks": False}

    # ── Message 1: Assessment summary ────────────────────────────────────────
    outcomes["summary"] = send_assessment_summary(
        webhook_url=url,
        org_name=org_name,
        vertical=vertical,
        overall_score=int(overall) if overall else 0,
        domain_scores=domain_scores,
        narrative_snippet=narrative[:300] if narrative else "",
    )

    # ── Message 2: 90-day action plan ────────────────────────────────────────
    if include_action_plan and action_pack.get("action_plan"):
        plan_text = action_pack["action_plan"][:1500]
        outcomes["action_plan"] = send_slack_message(url, {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🗓️ 90-Day Action Plan — {org_name}",
                        "emoji": True,
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": plan_text
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
        })

    # ── Message 3: Risk watch list ────────────────────────────────────────────
    if include_risks and action_pack.get("risk_watchlist"):
        risk_text = action_pack["risk_watchlist"][:1500]
        outcomes["risks"] = send_slack_message(url, {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Risk Watch List — {org_name}",
                        "emoji": True,
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": risk_text
                    }
                },
                {
                    "type": "context",
                    "elements": [{
                        "type": "mrkdwn",
                        "text": f"Supply Chain Health Agent · {_now()} · "
                                f"Risk signals are informational only."
                    }]
                }
            ]
        })

    total = sum(1 for v in outcomes.values() if v)
    print(
        f"[Slack Integration] Pushed {total}/3 messages to Slack "
        f"for {org_name} ({vertical})"
    )
    return outcomes


def push_board_summary_to_slack(
    board_summary: str,
    org_name: str = "Your Organisation",
    webhook_url: str = None,
) -> bool:
    """
    Push just the board summary to Slack — useful for exec channels.
    """
    url = webhook_url or _get_webhook_url()
    if not url:
        return False

    return send_slack_message(url, {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📌 Board Summary — {org_name}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": board_summary[:1500]
                }
            },
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"Supply Chain Health Agent · {_now()} · "
                            f"For informational purposes only."
                }]
            }
        ]
    })
