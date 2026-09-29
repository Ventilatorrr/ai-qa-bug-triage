"""Permitted supporting context for an already-authorized AI Assist request."""

from typing import Literal

from pydantic import BaseModel

from app.database import get_connection
from app.schemas import AiAssistRequest


RECENT_BUG_LIMIT = 5


class HistoricalBugContext(BaseModel):
    id: int
    title: str
    affected_version: str | None
    environment: str | None
    description: str | None
    steps_to_reproduce: str | None
    expected_result: str | None
    actual_result: str | None
    severity: str | None
    priority: str | None
    assignee_id: int | None


class AssignableMemberContext(BaseModel):
    user_id: int
    email: str
    role: Literal["QA Analyst", "Developer"]


class AiTriageContext(BaseModel):
    current_form: AiAssistRequest
    recent_bugs: list[HistoricalBugContext]
    eligible_assignees: list[AssignableMemberContext]

    @property
    def eligible_assignee_ids(self) -> set[int]:
        return {member.user_id for member in self.eligible_assignees}


def build_triage_context(project_id: int, bug_id: int | None, form: AiAssistRequest) -> AiTriageContext:
    """Call after authorization. History supports, never fills, the submitted form.

    Retrieve at most five recent same-project bugs, excluding the edited bug.
    Only suggestion-supported fields and a source bug ID are included in history.
    History is not verified fact for the current bug, and historical assignee IDs
    do not confer eligibility: use the current eligible_assignee_ids for validation.
    """
    fields = tuple(HistoricalBugContext.model_fields)
    conn = get_connection()
    try:
        bug_rows = conn.execute(
            f"""
            SELECT {', '.join(fields)} FROM bugs
            WHERE project_id = ? AND (? IS NULL OR id != ?)
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            (project_id, bug_id, bug_id, RECENT_BUG_LIMIT),
        ).fetchall()
        member_rows = conn.execute(
            """
            SELECT pm.user_id, u.email, pm.role
            FROM project_members pm
            JOIN users u ON u.id = pm.user_id
            WHERE pm.project_id = ? AND pm.role IN ('QA Analyst', 'Developer')
            ORDER BY pm.user_id
            """,
            (project_id,),
        ).fetchall()
    finally:
        conn.close()
    return AiTriageContext(
        current_form=form.model_copy(deep=True),
        recent_bugs=[HistoricalBugContext(**dict(zip(fields, row))) for row in bug_rows],
        eligible_assignees=[
            AssignableMemberContext(user_id=user_id, email=email, role=role)
            for user_id, email, role in member_rows
        ],
    )
