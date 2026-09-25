from app.schemas import AiAssistRequest


class AiTriageUnavailable(Exception):
    pass


def request_triage(project_id: int, bug_id: int | None, form: AiAssistRequest):
    """Provider boundary. Call only after request authorization has succeeded."""
    raise AiTriageUnavailable("AI assistance is not configured yet.")
