"""
alerts/email_dispatcher.py

Email dispatcher for Supply Chain Health Agent Phase 2.
Sends assessment summaries and risk alerts via SMTP.
Supports Gmail, SendGrid, and any standard SMTP provider.

Phase 2 Feature — requires Pro tier or above.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone


# ── Config from environment variables ────────────────────────────────────────
# Set these in your .env file — never hardcode credentials.
#
# SMTP_HOST     e.g. smtp.gmail.com or smtp.sendgrid.net
# SMTP_PORT     e.g. 587
# SMTP_USER     your email address or SendGrid API user
# SMTP_PASS     your password or SendGrid API key
# SMTP_FROM     the From address (defaults to SMTP_USER)

def _smtp_config() -> dict:
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASS", ""),
        "from_addr": os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "")),
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")


def _score_color(score: int) -> str:
    if score >= 80: return "#1D9E75"
    if score >= 60: return "#3B8BD4"
    if score >= 40: return "#BA7517"
    return "#E24B4A"


def _score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "At Risk"


def _bar(score: int) -> str:
    filled = round(score / 5)
    return "|" + ("=" * filled) + ("-" * (20 - filled)) + "|"


def _send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Send an email via SMTP.
    Returns True on success, False on failure.
    """
    cfg = _smtp_config()
    if not cfg["user"] or not cfg["password"]:
        print("[Email] SMTP credentials not configured — set SMTP_USER and SMTP_PASS in .env")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg["from_addr"]
        msg["To"]      = to_email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from_addr"], to_email, msg.as_string())

        print(f"[Email] Sent to {to_email}: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[Email] Authentication failed — check SMTP_USER and SMTP_PASS")
        return False
    except smtplib.SMTPException as e:
        print(f"[Email] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[Email] Unexpected error: {e}")
        return False


def send_assessment_email(
    to_email: str,
    org_name: str,
    vertical: str,
    overall_score: int,
    domain_scores: dict,
    narrative_snippet: str = "",
    deltas: dict = None,
) -> bool:
    """
    Send a full assessment summary email.
    """
    subject = f"Supply Chain Health Assessment — {org_name} — {overall_score}/100"
    color   = _score_color(overall_score)
    label   = _score_label(overall_score)

    # Build domain rows for HTML
    domain_rows_html = ""
    domain_rows_text = ""
    for domain, score in domain_scores.items():
        sc     = _score_color(score)
        sl     = _score_label(score)
        bar    = _bar(score)
        delta_html = delta_text = ""
        if deltas and domain in deltas:
            d = deltas[domain]
            arrow = "▲" if d > 0 else "▼" if d < 0 else "→"
            delta_html = f' <span style="color:{"#1D9E75" if d>0 else "#E24B4A"}">({arrow}{abs(d)})</span>'
            delta_text = f" ({arrow}{abs(d)})"

        domain_rows_html += f"""
        <tr>
          <td style="padding:8px 12px;font-weight:600;color:#1A1A2E;">
            {domain.replace('_',' ').title()}
          </td>
          <td style="padding:8px 12px;font-weight:700;color:{sc};">
            {score}/100{delta_html}
          </td>
          <td style="padding:8px 12px;color:{sc};">{sl}</td>
          <td style="padding:8px 12px;font-family:monospace;font-size:11px;color:{sc};">
            {bar}
          </td>
        </tr>"""

        domain_rows_text += f"  {domain.replace('_',' ').title():<25} {score}/100  {sl}{delta_text}\n"

    snippet_html = snippet_text = ""
    if narrative_snippet:
        snip = narrative_snippet[:400].strip()
        if len(narrative_snippet) > 400:
            snip += "..."
        snippet_html = f"""
        <div style="background:#F7F6F3;border-left:4px solid #534AB7;
        padding:16px;margin:24px 0;border-radius:0 8px 8px 0;">
          <p style="font-weight:600;color:#1A1A2E;margin:0 0 8px;">
            Executive Summary
          </p>
          <p style="color:#374151;font-size:14px;line-height:1.6;margin:0;">
            {snip}
          </p>
        </div>"""
        snippet_text = f"\nEXECUTIVE SUMMARY\n{snip}\n"

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#F7F6F3;
             margin:0;padding:0;">
  <div style="max-width:640px;margin:32px auto;background:#FFFFFF;
              border-radius:12px;overflow:hidden;
              box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#1E1A4E;padding:28px 32px;">
      <h1 style="color:#FFFFFF;font-size:20px;margin:0 0 4px;">
        🤖 Supply Chain Health Assessment
      </h1>
      <p style="color:#AFA9EC;font-size:13px;margin:0;">
        {org_name} · {vertical.replace('_',' ').title()} · {_now()}
      </p>
    </div>

    <!-- Overall score -->
    <div style="background:#1E1A4E;padding:0 32px 28px;">
      <div style="background:#2D2878;border-radius:10px;
                  padding:20px;text-align:center;">
        <div style="font-size:48px;font-weight:700;color:#FFFFFF;
                    line-height:1;">{overall_score}</div>
        <div style="font-size:13px;color:#AFA9EC;margin-top:4px;">
          out of 100
        </div>
        <div style="font-size:15px;font-weight:600;color:{color};
                    margin-top:8px;">{label}</div>
      </div>
    </div>

    <div style="padding:28px 32px;">

      <!-- Domain scores -->
      <h2 style="font-size:15px;font-weight:700;color:#1A1A2E;
                 border-left:4px solid #534AB7;padding-left:12px;
                 margin:0 0 16px;">Domain Health Scores</h2>
      <table style="width:100%;border-collapse:collapse;
                    font-size:13px;">
        <thead>
          <tr style="background:#534AB7;">
            <th style="padding:8px 12px;text-align:left;color:#FFFFFF;">
              Domain
            </th>
            <th style="padding:8px 12px;text-align:left;color:#FFFFFF;">
              Score
            </th>
            <th style="padding:8px 12px;text-align:left;color:#FFFFFF;">
              Rating
            </th>
            <th style="padding:8px 12px;text-align:left;color:#FFFFFF;">
              Health Bar
            </th>
          </tr>
        </thead>
        <tbody>
          {domain_rows_html}
        </tbody>
      </table>

      {snippet_html}

      <!-- Disclaimer -->
      <div style="background:#FFFBEB;border:1px solid #FCD34D;
                  border-radius:8px;padding:12px 16px;margin-top:24px;">
        <p style="font-size:11px;color:#78350F;margin:0;line-height:1.5;">
          ⚠️ <strong>Illustrative &amp; Directional Use Only.</strong>
          All assessments, scores, and estimates are for informational
          purposes only. Not professional financial or consulting advice.
        </p>
      </div>
    </div>

    <!-- Footer -->
    <div style="background:#F7F6F3;padding:16px 32px;text-align:center;
                border-top:1px solid #E5E7EB;">
      <p style="font-size:11px;color:#6B7280;margin:0;">
        Supply Chain Health Agent · Powered by Anthropic Claude ·
        <a href="https://supply-chain-health-agent.streamlit.app"
           style="color:#534AB7;">supply-chain-health-agent.streamlit.app</a>
      </p>
    </div>

  </div>
</body>
</html>"""

    text_body = f"""SUPPLY CHAIN HEALTH ASSESSMENT
{org_name} | {vertical.replace('_',' ').title()} | {_now()}

OVERALL SCORE: {overall_score}/100 — {label}

DOMAIN SCORES:
{domain_rows_text}
{snippet_text}
---
Supply Chain Health Agent | Powered by Anthropic Claude
All assessments are illustrative and directional only.
"""

    return _send_email(to_email, subject, html_body, text_body)


def send_risk_alert_email(
    to_email: str,
    org_name: str,
    vertical: str,
    alerts: list,
) -> bool:
    """
    Send a proactive risk alert email.
    alerts: list of dicts with keys: severity, headline, detail
    """
    if not alerts:
        return True

    subject = f"⚠️ Supply Chain Risk Alert — {org_name} — {len(alerts)} signals detected"

    severity_colors = {
        "High":   "#E24B4A",
        "Medium": "#E8A020",
        "Low":    "#3B8BD4",
    }

    rows_html = rows_text = ""
    for alert in alerts[:5]:
        sev   = alert.get("severity", "Medium")
        color = severity_colors.get(sev, "#E8A020")
        head  = alert.get("headline", "")
        detail = alert.get("detail", "")
        rows_html += f"""
        <div style="border-left:4px solid {color};padding:12px 16px;
                    margin:12px 0;background:#FAFAFA;border-radius:0 8px 8px 0;">
          <div style="font-weight:700;color:{color};font-size:13px;">
            {sev} — {head}
          </div>
          {"<div style='font-size:12px;color:#374151;margin-top:4px;line-height:1.5;'>" + detail + "</div>" if detail else ""}
        </div>"""
        rows_text += f"[{sev}] {head}\n{detail}\n\n"

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#F7F6F3;
             margin:0;padding:0;">
  <div style="max-width:640px;margin:32px auto;background:#FFFFFF;
              border-radius:12px;overflow:hidden;
              box-shadow:0 4px 24px rgba(0,0,0,0.08);">
    <div style="background:#1E1A4E;padding:28px 32px;">
      <h1 style="color:#FFFFFF;font-size:20px;margin:0 0 4px;">
        ⚠️ Supply Chain Risk Alert
      </h1>
      <p style="color:#AFA9EC;font-size:13px;margin:0;">
        {org_name} · {vertical.replace('_',' ').title()} · {_now()}
      </p>
    </div>
    <div style="padding:28px 32px;">
      <p style="color:#374151;font-size:14px;">
        Claude has identified <strong>{len(alerts)} supply chain risk signal(s)</strong>
        relevant to your organisation.
      </p>
      {rows_html}
      <div style="background:#FFFBEB;border:1px solid #FCD34D;
                  border-radius:8px;padding:12px 16px;margin-top:24px;">
        <p style="font-size:11px;color:#78350F;margin:0;">
          ⚠️ Risk signals are sourced via live web search and are
          informational only. Verify before acting.
        </p>
      </div>
    </div>
    <div style="background:#F7F6F3;padding:16px 32px;text-align:center;
                border-top:1px solid #E5E7EB;">
      <p style="font-size:11px;color:#6B7280;margin:0;">
        Supply Chain Health Agent · Powered by Anthropic Claude
      </p>
    </div>
  </div>
</body>
</html>"""

    text_body = f"""SUPPLY CHAIN RISK ALERT
{org_name} | {vertical.replace('_',' ').title()} | {_now()}

{len(alerts)} risk signal(s) detected:

{rows_text}
---
Supply Chain Health Agent | Risk signals are informational only.
"""

    return _send_email(to_email, subject, html_body, text_body)
