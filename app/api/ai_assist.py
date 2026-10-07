from fastapi import APIRouter, Header, HTTPException

from app import ai_triage
from app.api.auth import get_current_user_id
from app.database import get_connection
from app.schemas import AiAssistRequest


router = APIRouter(tags=["AI Assist"])


def authorize_ai_assist(project_id, bug_number, authorization):
    user_id = get_current_user_id(authorization)
    conn = get_connection()
    try:
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
        return bug_id
    finally:
        conn.close()


def request_authorized_triage(project_id, bug_number, form, authorization):
    bug_id = authorize_ai_assist(project_id, bug_number, authorization)
    try:
        result = ai_triage.request_triage(project_id, bug_id, form)
        return {"outcome": result.outcome, "suggestions": result.suggestions}
    except ai_triage.AiTriageUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ai_triage.AiTriageFailed as error:
        raise HTTPException(status_code=502, detail=str(error)) from None


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
