import json
import re

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import ResumeConstraintsDto, UpdateResumeConstraintsInput
from app.services.utils import utc_now_iso


def ensure_constraints_schema() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_constraints (
              resume_id TEXT PRIMARY KEY,
              rules_json TEXT NOT NULL DEFAULT '[]',
              updated_at TEXT NOT NULL,
              FOREIGN KEY(resume_id) REFERENCES resumes(id)
            )
            """
        )
        connection.commit()


def get_resume_constraints_for_user(user_id: str, resume_id: str) -> ResumeConstraintsDto:
    ensure_constraints_schema()
    _ensure_resume_for_user(user_id, resume_id)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT rules_json, updated_at
            FROM resume_constraints
            WHERE resume_id = ?
            """,
            (resume_id,),
        ).fetchone()

        if row is None:
            timestamp = utc_now_iso()
            connection.execute(
                """
                INSERT INTO resume_constraints (resume_id, rules_json, updated_at)
                VALUES (?, '[]', ?)
                """,
                (resume_id, timestamp),
            )
            connection.commit()
            return ResumeConstraintsDto(resumeId=resume_id, rules=[], updatedAt=timestamp)

    rules = [rule for rule in json.loads(row["rules_json"]) if isinstance(rule, str)]
    return ResumeConstraintsDto(resumeId=resume_id, rules=rules, updatedAt=row["updated_at"])


def update_resume_constraints_for_user(
    user_id: str,
    resume_id: str,
    input_data: UpdateResumeConstraintsInput,
) -> ResumeConstraintsDto:
    ensure_constraints_schema()
    _ensure_resume_for_user(user_id, resume_id)

    normalized_rules = _normalize_rules(input_data.rules)
    timestamp = utc_now_iso()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO resume_constraints (resume_id, rules_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(resume_id) DO UPDATE SET rules_json = excluded.rules_json, updated_at = excluded.updated_at
            """,
            (resume_id, json.dumps(normalized_rules), timestamp),
        )
        connection.commit()

    return ResumeConstraintsDto(resumeId=resume_id, rules=normalized_rules, updatedAt=timestamp)


def get_constraint_rules_for_user(user_id: str, resume_id: str) -> list[str]:
    return get_resume_constraints_for_user(user_id, resume_id).rules


def has_one_line_bullet_rule(rules: list[str]) -> bool:
    return any("one line" in rule.casefold() and "bullet" in rule.casefold() for rule in rules)


def evaluate_constraint_violations(before_text: str, after_text: str, block_kind: str, rules: list[str]) -> list[str]:
    violations: list[str] = []
    normalized_after = " ".join(after_text.split())
    normalized_before = " ".join(before_text.split())

    lowered_rules = [rule.casefold() for rule in rules]

    if block_kind == "bullet" and any("one line" in rule and "bullet" in rule for rule in lowered_rules):
        if len(normalized_after) > 95:
            violations.append("Likely exceeds a one-line bullet.")

    if any("first-person" in rule or "first person" in rule for rule in lowered_rules):
        if re.search(r"\b(i|me|my|mine|we|our|ours|us)\b", after_text, flags=re.IGNORECASE):
            violations.append("Uses first-person language.")

    if any("concise" in rule for rule in lowered_rules):
        if len(normalized_after.split()) > len(normalized_before.split()) + 4:
            violations.append("Less concise than the original.")

    if any("one sentence" in rule for rule in lowered_rules):
        sentence_count = len([part for part in re.split(r"[.!?]+", normalized_after) if part.strip()])
        if sentence_count > 1:
            violations.append("Contains more than one sentence.")

    return violations


def _normalize_rules(rules: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for raw_rule in rules:
        rule = raw_rule.strip()
        if not rule:
            continue
        if len(rule) > 160:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Constraint rules must be 160 characters or fewer.")
        lowered = rule.casefold()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(rule)

    if len(normalized) > 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At most 12 constraint rules are allowed per resume.")

    return normalized


def _ensure_resume_for_user(user_id: str, resume_id: str) -> None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT r.id
            FROM resumes r
            WHERE r.id = ? AND r.user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
