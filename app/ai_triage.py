import logging
import os

from app.ai_context import AiTriageContext, build_triage_context, load_eligible_assignees
from app.ai_generation import build_generation_input
from app.ai_openai import request_openai_suggestions
from app.ai_response import process_provider_response
from app.ai_suggestions import MalformedSuggestionResponse, SuggestionResult
from app.ai_usage import AiUsageLimitReached, AiUsageMisconfigured, reserve_ai_request
from app.schemas import AiAssistRequest


logger = logging.getLogger(__name__)


class AiTriageUnavailable(Exception):
    pass


class AiTriageFailed(Exception):
    """Safe application-level failure; never contains raw SDK error details."""


def create_openai_client(api_key: str):
    # Keep the SDK optional when AI is not configured. The caller closes it.
    from openai import OpenAI

    return OpenAI(api_key=api_key, timeout=60.0, max_retries=0)


def request_triage(project_id: int, bug_id: int | None, form: AiAssistRequest, *, user_id: int, conn=None) -> SuggestionResult:
    """Build permitted context only after request authorization has succeeded.

    `conn` is the authorizing read transaction; it is closed once the context is read,
    so no database transaction stays open during the provider call.
    """
    try:
        context = build_triage_context(project_id, bug_id, form, conn)
    finally:
        if conn is not None:
            conn.close()
    return request_suggestions(context, project_id=project_id, user_id=user_id)


def request_suggestions(context: AiTriageContext, *, project_id: int, user_id: int) -> SuggestionResult:
    """Generate and validate suggestions without persisting application data."""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise AiTriageUnavailable("AI assistance is not configured yet.")
    generation_input = build_generation_input(context)
    try:
        with create_openai_client(api_key) as client:
            # Counted once, after local preparation and just before the provider call,
            # whether the provider then succeeds or fails.
            reserve_ai_request(user_id)
            raw_response = request_openai_suggestions(generation_input, client=client)
    except (AiUsageLimitReached, AiUsageMisconfigured):
        raise  # Returned unchanged as 429/503 by the endpoint.
    except Exception as error:
        # SDK/client errors may contain credentials or request content. Log only
        # the error type and HTTP status, never the message, so failures can still
        # be diagnosed; keep this catch limited to the provider boundary.
        logger.warning(
            "AI provider request failed: %s (HTTP status %s).",
            type(error).__name__, getattr(error, "status_code", None),
        )
        raise AiTriageFailed("AI assistance could not generate suggestions. Please try again.") from None
    # Membership can change while generation runs. Keep the provider's snapshot,
    # but validate its output against members who are still eligible now. Only members
    # of the authorized snapshot count, so a project that reuses the ID adds none.
    validation_context = context.model_copy(update={"eligible_assignees": [
        member for member in load_eligible_assignees(project_id)
        if member.user_id in context.eligible_assignee_ids
    ]})
    try:
        return process_provider_response(validation_context, raw_response)
    except MalformedSuggestionResponse:
        logger.warning("AI provider returned a malformed suggestion response.")
        raise AiTriageFailed("AI assistance returned an invalid suggestion response. Please try again.") from None
