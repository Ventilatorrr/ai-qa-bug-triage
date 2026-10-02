import os

from app.ai_context import AiTriageContext, build_triage_context, load_eligible_assignees
from app.ai_generation import build_generation_input
from app.ai_openai import request_openai_suggestions
from app.ai_response import process_provider_response
from app.ai_suggestions import MalformedSuggestionResponse, SuggestionResult
from app.schemas import AiAssistRequest


class AiTriageUnavailable(Exception):
    pass


class AiTriageFailed(Exception):
    """Safe application-level failure; never contains raw SDK error details."""


def create_openai_client(api_key: str):
    # Keep the SDK optional when AI is not configured. The caller closes it.
    from openai import OpenAI

    return OpenAI(api_key=api_key, timeout=60.0, max_retries=0)


def request_triage(project_id: int, bug_id: int | None, form: AiAssistRequest) -> SuggestionResult:
    """Build permitted context only after request authorization has succeeded."""
    context = build_triage_context(project_id, bug_id, form)
    return request_suggestions(context, project_id=project_id)


def request_suggestions(context: AiTriageContext, *, project_id: int) -> SuggestionResult:
    """Generate and validate suggestions without persisting application data."""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise AiTriageUnavailable("AI assistance is not configured yet.")
    generation_input = build_generation_input(context)
    try:
        with create_openai_client(api_key) as client:
            raw_response = request_openai_suggestions(generation_input, client=client)
    except Exception:
        # SDK/client errors may contain credentials or request content. Do not
        # propagate/log them; keep this catch limited to the provider boundary.
        raise AiTriageFailed("AI assistance could not generate suggestions. Please try again.") from None
    # Membership can change while generation runs. Keep the provider's snapshot,
    # but validate its output against current eligibility from the same project.
    validation_context = context.model_copy(
        update={"eligible_assignees": load_eligible_assignees(project_id)}
    )
    try:
        return process_provider_response(validation_context, raw_response)
    except MalformedSuggestionResponse:
        raise AiTriageFailed("AI assistance returned an invalid suggestion response. Please try again.") from None
