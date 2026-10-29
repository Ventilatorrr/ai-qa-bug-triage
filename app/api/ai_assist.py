from fastapi import APIRouter, Header, HTTPException

from app import ai_triage, ai_usage
from app.ai_context import FORM_TEXT_LIMIT
from app.api.auth import get_current_user_id
from app.database import get_connection
from app.schemas import AiAssistRequest


router = APIRouter(tags=["AI Assist"])

FORM_TEXT_LABELS = {
    "title": "Title",
    "affected_version": "Affected Version",
    "environment": "Environment",
    "description": "Description",
    "steps_to_reproduce": "Steps to Reproduce",
    "expected_result": "Expected Result",
    "actual_result": "Actual Result",
}


def authorize_ai_assist(project_id, bug_number, authorization):
    """Return the user, bug and the open read transaction that authorized them.

    The context is read in the same transaction, so a project deleted and recreated
    with the same ID cannot supply another user's reports or members.
    """
    user_id = get_current_user_id(authorization)
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        member = conn.execute(
            "SELECT role FROM project_members WHERE project_id = ? AND user_id = ?",
            (project_id, user_id),
        ).fetchone()
        if member is None:
            raise HTTPException(status_code=404, detail="Project not found.")
        if member[0] not in ("Project Owner", "QA Analyst"):
            raise HTTPException(status_code=403, detail="You are not authorized to request AI assistance.")
        bug_id = None
        if bug_number is not None:
            bug = conn.execute(
                "SELECT id, status FROM bugs WHERE project_id = ? AND bug_number = ?",
                (project_id, bug_number),
            ).fetchone()
            if bug is None:
                raise HTTPException(status_code=404, detail="Bug not found.")
            if bug[1] != "Triage":
                raise HTTPException(status_code=409, detail="AI assistance requires a bug in Triage.")
            bug_id = bug[0]
        return user_id, bug_id, conn
    except BaseException:
        conn.close()
        raise


def reject_oversized_form(form):
    # Reject rather than truncate: the user's current bug information stays intact.
    for field, label in FORM_TEXT_LABELS.items():
        if len(getattr(form, field)) > FORM_TEXT_LIMIT:
            raise HTTPException(
                status_code=422,
                detail=f"{label} is too long for AI Assist (maximum {FORM_TEXT_LIMIT:,} characters).",
            )


def request_authorized_triage(project_id, bug_number, form, authorization):
    user_id, bug_id, conn = authorize_ai_assist(project_id, bug_number, authorization)
    try:
        reject_oversized_form(form)
        # request_triage closes the connection after reading the context, before the provider call.
        result = ai_triage.request_triage(project_id, bug_id, form, user_id=user_id, conn=conn)
        return {"outcome": result.outcome, "suggestions": result.suggestions}
    except ai_usage.AiUsageLimitReached as error:
        raise HTTPException(status_code=429, detail=str(error)) from None
    except (ai_triage.AiTriageUnavailable, ai_usage.AiUsageMisconfigured) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ai_triage.AiTriageFailed as error:
        raise HTTPException(status_code=502, detail=str(error)) from None
    finally:
        conn.close()  # Already closed unless an earlier step failed; closing twice is harmless.


@router.post("/projects/{project_id}/ai-assist")
def request_new_bug_triage(
    project_id: int,
    form: AiAssistRequest,
    authorization: str | None = Header(default=None),
):
    return request_authorized_triage(project_id, None, form, authorization)


@router.post("/projects/{project_id}/bugs/{bug_number}/ai-assist")
def request_edit_bug_triage(
    project_id: int,
    bug_number: int,
    form: AiAssistRequest,
    authorization: str | None = Header(default=None),
):
    return request_authorized_triage(project_id, bug_number, form, authorization)
