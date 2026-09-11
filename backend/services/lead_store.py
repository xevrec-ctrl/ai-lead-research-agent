"""Small SQLite persistence layer for leads, reports, and approval-gated tasks."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LeadStore:
    def __init__(self, database_path: str | Path = "data/leads.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    company TEXT NOT NULL,
                    company_url TEXT,
                    industry TEXT,
                    hq_location TEXT,
                    client_need TEXT,
                    our_capabilities TEXT,
                    status TEXT NOT NULL DEFAULT 'researching',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL REFERENCES leads(id),
                    report TEXT NOT NULL,
                    assessment_json TEXT,
                    review_json TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL REFERENCES leads(id),
                    title TEXT NOT NULL,
                    details TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending_approval',
                    external_task_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_reports_lead_id ON reports(lead_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_lead_id ON task_drafts(lead_id);
                """
            )

    def create_lead(self, lead_id: str, data: dict[str, Any]) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO leads
                (id, company, company_url, industry, hq_location, client_need,
                 our_capabilities, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'researching', ?, ?)
                """,
                (
                    lead_id,
                    data["company"],
                    data.get("company_url"),
                    data.get("industry"),
                    data.get("hq_location"),
                    data.get("client_need"),
                    data.get("our_capabilities"),
                    now,
                    now,
                ),
            )

    def update_lead_status(self, lead_id: str, status: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE leads SET status = ?, updated_at = ? WHERE id = ?",
                (status, utc_now(), lead_id),
            )

    def save_report(
        self,
        lead_id: str,
        report: str,
        assessment: dict[str, Any] | None,
        review: dict[str, Any] | None,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reports (lead_id, report, assessment_json, review_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    lead_id,
                    report,
                    json.dumps(assessment or {}, ensure_ascii=False),
                    json.dumps(review or {}, ensure_ascii=False),
                    utc_now(),
                ),
            )
            connection.execute(
                "UPDATE leads SET status = 'review_required', updated_at = ? WHERE id = ?",
                (utc_now(), lead_id),
            )
            return int(cursor.lastrowid)

    def create_task_draft(
        self, lead_id: str, title: str, details: dict[str, Any]
    ) -> int:
        now = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO task_drafts (lead_id, title, details, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (lead_id, title, json.dumps(details, ensure_ascii=False), now, now),
            )
            return int(cursor.lastrowid)

    def approve_task_draft(self, task_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM task_drafts WHERE id = ?", (task_id,)
            ).fetchone()
            if row is None:
                return None
            if row["status"] != "pending_approval":
                return dict(row)
            connection.execute(
                "UPDATE task_drafts SET status = 'approved', updated_at = ? WHERE id = ?",
                (utc_now(), task_id),
            )
            updated = connection.execute(
                "SELECT * FROM task_drafts WHERE id = ?", (task_id,)
            ).fetchone()
            return dict(updated) if updated else None

    def get_lead(self, lead_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            lead = connection.execute(
                "SELECT * FROM leads WHERE id = ?", (lead_id,)
            ).fetchone()
            if lead is None:
                return None
            reports = connection.execute(
                "SELECT * FROM reports WHERE lead_id = ? ORDER BY id DESC", (lead_id,)
            ).fetchall()
            tasks = connection.execute(
                "SELECT * FROM task_drafts WHERE lead_id = ? ORDER BY id DESC",
                (lead_id,),
            ).fetchall()
            result = dict(lead)
            result["reports"] = [
                self._decode_json_columns(dict(row)) for row in reports
            ]
            result["tasks"] = [self._decode_json_columns(dict(row)) for row in tasks]
            return result

    def list_leads(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM leads ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def _decode_json_columns(row: dict[str, Any]) -> dict[str, Any]:
        for key in ("assessment_json", "review_json", "details"):
            if row.get(key):
                try:
                    row[key.removesuffix("_json")] = json.loads(row[key])
                except json.JSONDecodeError:
                    row[key.removesuffix("_json")] = row[key]
        return row
