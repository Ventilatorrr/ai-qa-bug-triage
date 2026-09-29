from app.ai_context import AiTriageContext, build_triage_context
from app.schemas import AiAssistRequest


class AiTriageUnavailable(Exception):
    pass


def request_triage(project_id: int, bug_id: int | None, form: AiAssistRequest):
    """Build permitted context only after request authorization has succeeded."""
    context = build_triage_context(project_id, bug_id, form)
    return request_suggestions(context)


def request_suggestions(context: AiTriageContext):
    """Unconfigured provider boundary; no suggestions or persistence yet."""
    raise AiTriageUnavailable("AI assistance is not configured yet.")
