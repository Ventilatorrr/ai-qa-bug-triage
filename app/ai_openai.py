"""OpenAI transport adapter, deliberately separate from the live AI Assist service."""

from copy import deepcopy
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI


class OpenAiSuggestionResponseError(ValueError):
    """The provider did not complete a usable structured-output response."""


def request_openai_suggestions(generation_input: dict, *, client: "OpenAI") -> object:
    """Return untrusted decoded JSON for process_provider_response to validate.

    The caller supplies a configured client. No credentials are read here, and
    no authorization, database access, persistence, or domain validation occurs.
    SDK request errors propagate; unsuccessful output never becomes suggestions.
    """
    contract = generation_input["output_contract"]
    response = client.responses.create(
        model="gpt-6-luna",
        instructions=(
            generation_input["instructions"]
            + "\noutput_contract.field_rules:\n"
            + json.dumps(contract["field_rules"], ensure_ascii=False)
        ),
        input=[{
            "role": "user",
            "content": json.dumps(generation_input["context"], ensure_ascii=False),
        }],
        text={"format": {
            "type": "json_schema",
            "name": "bug_suggestions",
            "strict": True,
            "schema": deepcopy(contract["schema"]),
        }},
        store=False,
    )
    if response.status != "completed":
        raise OpenAiSuggestionResponseError("OpenAI did not complete the suggestion response.")
    for item in response.output:
        if item.type == "message" and any(content.type == "refusal" for content in item.content):
            raise OpenAiSuggestionResponseError("OpenAI refused the suggestion request.")
    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        raise OpenAiSuggestionResponseError("OpenAI did not return structured suggestion JSON.") from exc
