"""
memory/memory_store.py

SQLite-based persistent memory store for Supply Chain Health Agent.
Tracks assessment history, org profiles, and KPI trends across sessions.

Phase 2 Feature — requires Pro tier or above.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Optional

# ── Database location ─────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sc_memory.db")


def _get_conn() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
    return conn


def init_db():
    """
    Initialize all database tables.
    Safe to call multiple times — uses CREATE IF NOT EXISTS.
    """
    conn = _get_conn()
    try:
        conn.executescript("""
            -- Organisation profiles
            CREATE TABLE IF NOT EXISTS organisations (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                org_key         TEXT    UNIQUE NOT NULL,
                org_name        TEXT,
                vertical        TEXT    DEFAULT 'general',
                persona         TEXT    DEFAULT 'analyst',
                created_at      TEXT    NOT NULL,
                updated_at      TEXT    NOT NULL,
                metadata        TEXT    DEFAULT '{}'
            );

            -- Assessment history
            CREATE TABLE IF NOT EXISTS assessments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                org_key         TEXT    NOT NULL,
                vertical        TEXT    NOT NULL,
                persona         TEXT    NOT NULL,
                overall_score   INTEGER,
                scores_json     TEXT,
                narrative       TEXT,
                raw_response    TEXT,
                mode            TEXT    DEFAULT 'general',
                created_at      TEXT    NOT NULL,
                FOREIGN KEY (org_key) REFERENCES organisations(org_key)
            );

            -- Domain score trends (denormalised for fast queries)
            CREATE TABLE IF NOT EXISTS score_trends (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                org_key         TEXT    NOT NULL,
                assessment_id   INTEGER NOT NULL,
                domain          TEXT    NOT NULL,
                score           INTEGER NOT NULL,
                recorded_at     TEXT    NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id)
            );

            -- Risk alerts log
            CREATE TABLE IF NOT EXISTS risk_alerts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                org_key         TEXT,
                vertical        TEXT,
                alert_type      TEXT    NOT NULL,
                severity        TEXT    NOT NULL,
                headline        TEXT    NOT NULL,
                detail          TEXT,
                delivered_slack INTEGER DEFAULT 0,
                delivered_email INTEGER DEFAULT 0,
                created_at      TEXT    NOT NULL
            );

            -- Session memory (within-session context)
            CREATE TABLE IF NOT EXISTS session_memory (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT    NOT NULL,
                org_key         TEXT,
                key             TEXT    NOT NULL,
                value           TEXT    NOT NULL,
                created_at      TEXT    NOT NULL,
                expires_at      TEXT
            );

            -- Waitlist (for upgrade prompts)
            CREATE TABLE IF NOT EXISTS waitlist (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                email           TEXT    UNIQUE NOT NULL,
                tier_interest   TEXT,
                org_name        TEXT,
                notes           TEXT,
                created_at      TEXT    NOT NULL
            );

            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_assessments_org
                ON assessments(org_key);
            CREATE INDEX IF NOT EXISTS idx_assessments_created
                ON assessments(created_at);
            CREATE INDEX IF NOT EXISTS idx_score_trends_org
                ON score_trends(org_key);
            CREATE INDEX IF NOT EXISTS idx_score_trends_domain
                ON score_trends(domain, org_key);
            CREATE INDEX IF NOT EXISTS idx_alerts_org
                ON risk_alerts(org_key, created_at);
        """)
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


# ── Organisation functions ────────────────────────────────────────────────────

def upsert_org(
    org_key: str,
    org_name: str = None,
    vertical: str = "general",
    persona: str = "analyst",
    metadata: dict = None,
) -> dict:
    """
    Create or update an organisation profile.
    org_key is the stable identifier (e.g. slugified company name or user ID).
    """
    init_db()
    conn = _get_conn()
    now = _now()
    try:
        existing = conn.execute(
            "SELECT * FROM organisations WHERE org_key = ?", (org_key,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE organisations
                SET org_name = COALESCE(?, org_name),
                    vertical = ?,
                    persona  = ?,
                    metadata = ?,
                    updated_at = ?
                WHERE org_key = ?
            """, (
                org_name,
                vertical,
                persona,
                json.dumps(metadata or {}),
                now,
                org_key,
            ))
        else:
            conn.execute("""
                INSERT INTO organisations
                    (org_key, org_name, vertical, persona, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                org_key,
                org_name or org_key,
                vertical,
                persona,
                now,
                now,
                json.dumps(metadata or {}),
            ))

        conn.commit()
        return get_org(org_key)
    finally:
        conn.close()


def get_org(org_key: str) -> Optional[dict]:
    """Retrieve an organisation profile by key."""
    init_db()
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM organisations WHERE org_key = ?", (org_key,)
        ).fetchone()
        if row:
            d = dict(row)
            d["metadata"] = json.loads(d.get("metadata") or "{}")
            return d
        return None
    finally:
        conn.close()


# ── Assessment functions ──────────────────────────────────────────────────────

def save_assessment(
    org_key: str,
    result: dict,
    vertical: str = "general",
    persona: str = "analyst",
    mode: str = "general",
) -> int:
    """
    Save a completed assessment to history.
    Returns the assessment ID.
    """
    init_db()
    conn = _get_conn()
    now = _now()

    scores_data   = result.get("scores") or {}
    domain_scores = scores_data.get("scores", {})
    overall       = scores_data.get("overall")

    try:
        cursor = conn.execute("""
            INSERT INTO assessments
                (org_key, vertical, persona, overall_score, scores_json,
                 narrative, raw_response, mode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            org_key,
            vertical,
            persona,
            overall,
            json.dumps(domain_scores),
            result.get("narrative", ""),
            result.get("raw", ""),
            mode,
            now,
        ))
        assessment_id = cursor.lastrowid

        # Denormalise domain scores for trend queries
        for domain, score in domain_scores.items():
            conn.execute("""
                INSERT INTO score_trends
                    (org_key, assessment_id, domain, score, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (org_key, assessment_id, domain, score, now))

        conn.commit()
        return assessment_id
    finally:
        conn.close()


def get_assessment_history(
    org_key: str,
    limit: int = 10,
) -> list:
    """
    Retrieve assessment history for an org, most recent first.
    """
    init_db()
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT id, vertical, persona, overall_score,
                   scores_json, mode, created_at
            FROM assessments
            WHERE org_key = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (org_key, limit)).fetchall()

        results = []
        for row in rows:
            d = dict(row)
            d["scores"] = json.loads(d.get("scores_json") or "{}")
            del d["scores_json"]
            results.append(d)
        return results
    finally:
        conn.close()


def get_score_trends(
    org_key: str,
    domain: str = None,
    limit: int = 20,
) -> list:
    """
    Retrieve score trends for an org, optionally filtered by domain.
    Returns list of {domain, score, recorded_at} dicts ordered by date.
    """
    init_db()
    conn = _get_conn()
    try:
        if domain:
            rows = conn.execute("""
                SELECT domain, score, recorded_at
                FROM score_trends
                WHERE org_key = ? AND domain = ?
                ORDER BY recorded_at ASC
                LIMIT ?
            """, (org_key, domain, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT domain, score, recorded_at
                FROM score_trends
                WHERE org_key = ?
                ORDER BY recorded_at ASC
                LIMIT ?
            """, (org_key, limit)).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_latest_assessment(org_key: str) -> Optional[dict]:
    """Retrieve the most recent assessment for an org."""
    history = get_assessment_history(org_key, limit=1)
    return history[0] if history else None


def get_score_delta(org_key: str) -> dict:
    """
    Compare latest assessment scores to the previous one.
    Returns dict of domain -> delta (positive = improvement).
    """
    history = get_assessment_history(org_key, limit=2)
    if len(history) < 2:
        return {}

    latest   = history[0]["scores"]
    previous = history[1]["scores"]

    deltas = {}
    for domain in latest:
        if domain in previous:
            deltas[domain] = latest[domain] - previous[domain]
    return deltas


# ── Session memory functions ──────────────────────────────────────────────────

def set_session_value(
    session_id: str,
    key: str,
    value,
    org_key: str = None,
) -> None:
    """Store a key-value pair for the current session."""
    init_db()
    conn = _get_conn()
    now = _now()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO session_memory
                (session_id, org_key, key, value, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, org_key, key, json.dumps(value), now))
        conn.commit()
    finally:
        conn.close()


def get_session_value(session_id: str, key: str):
    """Retrieve a session value by key."""
    init_db()
    conn = _get_conn()
    try:
        row = conn.execute("""
            SELECT value FROM session_memory
            WHERE session_id = ? AND key = ?
        """, (session_id, key)).fetchone()
        if row:
            return json.loads(row["value"])
        return None
    finally:
        conn.close()


# ── Waitlist functions ────────────────────────────────────────────────────────

def add_to_waitlist(
    email: str,
    tier_interest: str = None,
    org_name: str = None,
    notes: str = None,
) -> bool:
    """
    Add an email to the upgrade waitlist.
    Returns True if added, False if already exists.
    """
    init_db()
    conn = _get_conn()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO waitlist
                (email, tier_interest, org_name, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (email, tier_interest, org_name, notes, _now()))
        conn.commit()
        return conn.execute(
            "SELECT changes()"
        ).fetchone()[0] > 0
    finally:
        conn.close()


# ── Summary for Q&A context ───────────────────────────────────────────────────

def get_memory_summary(org_key: str) -> str:
    """
    Generate a plain-text memory summary for injection into Q&A prompts.
    This gives Claude context about the org's history and trends.
    """
    init_db()
    history = get_assessment_history(org_key, limit=5)
    if not history:
        return ""

    latest  = history[0]
    deltas  = get_score_delta(org_key)
    org     = get_org(org_key)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "ORGANISATION MEMORY — CROSS-SESSION CONTEXT",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if org:
        lines.append(
            f"Organisation: {org.get('org_name', org_key)} "
            f"| Vertical: {org.get('vertical', 'general')}"
        )

    lines.append(
        f"Total assessments on record: {len(history)}"
    )
    lines.append(
        f"Latest overall score: {latest.get('overall_score', 'N/A')}/100 "
        f"({latest.get('created_at', '')[:10]})"
    )

    if latest.get("scores"):
        lines.append("Latest domain scores:")
        for domain, score in latest["scores"].items():
            delta_str = ""
            if domain in deltas:
                d = deltas[domain]
                delta_str = f" (▲{d})" if d > 0 else f" (▼{abs(d)})" if d < 0 else " (→0)"
            lines.append(f"  {domain.capitalize()}: {score}/100{delta_str}")

    if deltas:
        improving = [d for d, v in deltas.items() if v > 0]
        declining = [d for d, v in deltas.items() if v < 0]
        if improving:
            lines.append(f"Improving since last assessment: {', '.join(improving)}")
        if declining:
            lines.append(f"Declining since last assessment: {', '.join(declining)}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)
