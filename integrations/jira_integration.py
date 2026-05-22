"""
integrations/jira_integration.py

Jira integration for Supply Chain Health Agent Phase 2.
Automatically creates Jira tickets from the 90-day action plan,
turning AI recommendations directly into tracked work items.

Phase 2 Feature — requires Team tier or above.

Setup:
  1. Go to id.atlassian.com/manage-profile/security/api-tokens
  2. Create an API token
  3. Add to your .env file:
       JIRA_BASE_URL   = https://yourcompany.atlassian.net
       JIRA_EMAIL      = your-email@company.com
       JIRA_API_TOKEN  = your-api-token
       JIRA_PROJECT    = SC (your project key)

Usage:
  from integrations.jira_integration import create_tickets_from_action_plan
  tickets = create_tickets_from_action_plan(action_plan_text, project_key="SC")
"""

import os
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone


def _jira_config() -> dict:
    return {
        "base_url":  os.environ.get("JIRA_BASE_URL", "").rstrip("/"),
        "email":     os.environ.get("JIRA_EMAIL", ""),
        "api_token": os.environ.get("JIRA_API_TOKEN", ""),
        "project":   os.environ.get("JIRA_PROJECT", "SC"),
    }


def _auth_header() -> str:
    cfg = _jira_config()
    token = base64.b64encode(
        f"{cfg['email']}:{cfg['api_token']}".encode()
    ).decode()
    return f"Basic {token}"


def _jira_request(
    method: str,
    path: str,
    body: dict = None,
) -> dict:
    """Make a Jira REST API request."""
    cfg = _jira_config()
    if not cfg["base_url"] or not cfg["email"] or not cfg["api_token"]:
        raise ValueError(
            "Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, "
            "and JIRA_API_TOKEN in your .env file."
        )

    url  = f"{cfg['base_url']}/rest/api/3{path}"
    data = json.dumps(body).encode("utf-8") if body else None

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization":  _auth_header(),
            "Content-Type":   "application/json",
            "Accept":         "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"Jira API error {e.code}: {body}")


def _priority_to_jira(priority: str) -> str:
    """Map our priority labels to Jira priority names."""
    mapping = {
        "immediate": "Highest",
        "high":      "High",
        "medium":    "Medium",
        "low":       "Low",
        "strategic": "Low",
    }
    return mapping.get(priority.lower(), "Medium")


def _parse_action_items(action_plan_text: str) -> list:
    """
    Parse action plan text into structured action items.
    Returns list of dicts with: title, description, priority, week.
    """
    items  = []
    lines  = action_plan_text.split("\n")
    current = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Detect priority sections
        priority = "medium"
        if any(k in stripped.upper() for k in ["IMMEDIATE", "0-90", "WEEK 1"]):
            priority = "immediate"
        elif any(k in stripped.upper() for k in ["SHORT", "6-18", "WEEK 5"]):
            priority = "high"
        elif any(k in stripped.upper() for k in ["STRATEGIC", "18+", "LONG"]):
            priority = "strategic"

        # Detect week timing
        week = "Week 1-4"
        if "WEEK 5" in stripped.upper() or "WEEK 6" in stripped.upper():
            week = "Week 5-8"
        elif "WEEK 9" in stripped.upper() or "WEEK 10" in stripped.upper():
            week = "Week 9-12"

        # Detect numbered action items
        import re
        match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if match:
            if current:
                items.append(current)
            title = match.group(2).strip()
            # Clean up bold markers
            title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
            current = {
                "title":       title[:255],
                "description": "",
                "priority":    priority,
                "week":        week,
            }
        elif current and stripped and not stripped.startswith("#"):
            # Append to current item description
            current["description"] += stripped + "\n"

    if current:
        items.append(current)

    return items[:10]  # Cap at 10 tickets per assessment


def create_jira_ticket(
    summary: str,
    description: str,
    project_key: str = None,
    issue_type: str = "Task",
    priority: str = "Medium",
    labels: list = None,
    due_date: str = None,
) -> dict:
    """
    Create a single Jira ticket.
    Returns the created issue dict with id, key, and URL.
    """
    cfg = _jira_config()
    project = project_key or cfg["project"]

    body = {
        "fields": {
            "project":     {"key": project},
            "summary":     summary,
            "description": {
                "type":    "doc",
                "version": 1,
                "content": [{
                    "type":    "paragraph",
                    "content": [{
                        "type": "text",
                        "text": description or summary,
                    }]
                }]
            },
            "issuetype": {"name": issue_type},
            "priority":  {"name": priority},
            "labels":    labels or ["supply-chain-health-agent"],
        }
    }

    if due_date:
        body["fields"]["duedate"] = due_date

    result = _jira_request("POST", "/issue", body)
    cfg = _jira_config()
    result["url"] = f"{cfg['base_url']}/browse/{result.get('key', '')}"
    return result


def create_tickets_from_action_plan(
    action_plan_text: str,
    org_name: str = "Supply Chain",
    project_key: str = None,
    vertical: str = "general",
) -> list:
    """
    Parse the 90-day action plan and create Jira tickets.
    Returns list of created ticket dicts with key and URL.

    Each ticket includes:
    - Summary: the action item title
    - Description: detail + context
    - Priority: mapped from timing (Immediate/Short/Strategic)
    - Labels: supply-chain-health-agent, vertical name
    - Week target in description
    """
    items   = _parse_action_items(action_plan_text)
    created = []
    failed  = []

    print(f"[Jira] Creating {len(items)} tickets for {org_name}...")

    for item in items:
        try:
            description = (
                f"Supply Chain Health Agent — {org_name}\n"
                f"Vertical: {vertical.replace('_', ' ').title()}\n"
                f"Target: {item['week']}\n\n"
                f"{item['description'].strip()}\n\n"
                f"Generated by Supply Chain Health Agent. "
                f"Validate with your supply chain team before acting."
            )

            ticket = create_jira_ticket(
                summary=f"[SC Health] {item['title']}",
                description=description,
                project_key=project_key,
                priority=_priority_to_jira(item["priority"]),
                labels=[
                    "supply-chain-health-agent",
                    vertical.replace(" ", "-").lower(),
                    item["week"].replace(" ", "-").lower(),
                ],
            )
            created.append({
                "key":     ticket.get("key"),
                "url":     ticket.get("url"),
                "title":   item["title"],
                "priority": item["priority"],
            })
            print(f"  ✅ Created: {ticket.get('key')} — {item['title'][:60]}")

        except Exception as e:
            failed.append({"title": item["title"], "error": str(e)})
            print(f"  ❌ Failed: {item['title'][:60]} — {e}")

    print(
        f"[Jira] Done — {len(created)} created, {len(failed)} failed"
    )
    return created


def get_project_info(project_key: str = None) -> dict:
    """Verify Jira connection and return project details."""
    cfg = _jira_config()
    key = project_key or cfg["project"]
    return _jira_request("GET", f"/project/{key}")


def test_connection() -> bool:
    """Test Jira API connectivity. Returns True if connected."""
    try:
        result = _jira_request("GET", "/myself")
        print(f"[Jira] Connected as: {result.get('displayName', 'unknown')}")
        return True
    except ValueError as e:
        print(f"[Jira] Not configured: {e}")
        return False
    except RuntimeError as e:
        print(f"[Jira] Connection failed: {e}")
        return False
