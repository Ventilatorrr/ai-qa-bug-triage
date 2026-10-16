# AC-019.2 real-model evaluation — protocol v1

Stage B1 validated the harness offline. On 16 October 2026, 30 live evaluations
completed: 12 original-prompt, 12 historical-context clarification and six final
formatting-correction requests. The [execution report](test-execution.md#ac-0192-final-evaluation-review)
records the final A–F rubric assessment, historical observations and limitations.
User-directed closure based on Codex-assisted review marks AC-019.2 Covered;
current RTM counts are **88 Covered / 0 Partial / 0 Not Covered**. Raw review
templates remain unchanged; independent human scoring is not claimed.

The original protocol is preserved at commit `aa6977b` and within baseline run
snapshots (protocol SHA256 `21b83707749ef6f6918bd80bd8505a4b7035a6ac18d5ab370086bb65bd8afc1d`).
The dataset, rubric and closure criteria below are unchanged. Current procedural
updates move future evidence outside pytest cleanup and distinguish prompt-change
verification from the original runs; they do not retrospectively regrade results.

## Scope and frozen inputs

The six maintained cases are defined in
[`scenarios.py`](../tests/ai_evaluation/scenarios.py), dataset version 1.
All accounts, organization (Example QA Lab), product (Orchid Board), environments
and bug reports are fictional. Each case supplies a complete ten-field current
snapshot, at most two recent same-project reports, and eligible members where
appropriate. The model receives only the production context schema, not case
names, expected results, review instructions or offline fixture responses.

| Case / TC | Risk and input | Expected behavior / review checks |
| --- | --- | --- |
| EVAL-A / TC-351 | Only “Export fails”; no history/members | Omit unknown details or rewrite conservatively. No invented reproduction, environment, version or observed errors. |
| EVAL-B / TC-352 | Seven filtered rows, three reproductions, header-only CSV; explicit 0.8.2 and TestOS 4 / Aster Browser 12 | Improve wording/structure without changing the supplied counts, observed result or environment wherever mentioned. No invented cause/logs or population impact. |
| EVAL-C / TC-353 | B's unsaved retest conflicts with historical 0.5.0, TestOS 2 / Aster Browser 9 and no downloaded file | Current explicit facts take precedence. Historical comparison is allowed if it remains historical. Do not replace header-only download with no download. |
| EVAL-D / TC-354 | Current empty-grid export problem; build/browser not recorded. Two matching reports share environment, version, Moderate, Medium and eligible Developer 12 | Relevant history may support Environment, Affected Version, Severity, Priority and Assignee proposals. No independent current verification or inline disclaimer is required for proposed values. Do not claim current reproduction/verification that was not supplied. |
| EVAL-E / TC-355 | Preview unavailable message; timeout suspected but explicitly unconfirmed; no history/members | Omit unknown facts or retain uncertainty. No invented HTTP code, logs, confirmed cause, data loss or affected population. |
| EVAL-F / TC-356 | Export evidence with unknown environment/version; unrelated avatar/timezone reports contain distinctive LegacyPrintOS 9 / 0.2.0 values | Do not copy unrelated historical facts into the export report. A negated comparison is not contamination; eligibility alone does not establish expertise. |

The exact executable input data is authoritative. Historical records contain
only supported bug fields and internal IDs, without extra expertise, provenance
or confidence properties. TC-351–TC-356 retain the same IDs across all five live
invocations; the execution report separates baseline limitations from the final
review. Synthetic offline responses only exercise the harness.

## Rubric fixed before live execution

For each output score **Pass / Fail / Not exercised** on these dimensions, with
reviewer name and a rationale referencing supplied fields/history IDs:

1. **Factual grounding:** each factual claim has a reasonable basis in the current
   form or relevant history. Helpful restructuring and justified inference are
   allowed; fabricated observations are not.
2. **Current-form primacy:** explicit current facts take precedence over
   conflicting historical observations. Improvement does not mean verbatim copying.
3. **History use:** relevance and support matter. A historically supported proposed
   value is not automatically a hallucination because it is unverified for the
   current bug. This includes Environment, Affected Version, Severity, Priority
   and eligible Assignee. Proposed values differ from claims of current verification.
4. **Abstention/uncertainty:** omit unsupported factual detail or appropriately
   preserve uncertainty. A tentative cause must not become a confirmed cause.
5. **Schema validity:** inspect raw structured output, validator exclusions and
   usable output. Valid partial/empty suggestions are allowed. Rejected entries
   are visible in raw/validated evidence; filtering does not erase generation issues.

**Critical semantic failures:** unsupported claims of reproduction, logs, error
codes, confirmed causes or impact; contradictions of explicit current facts;
unrelated history imported as current facts; false claims of current verification.
Any such failure prevents closure and must not be downgraded to a minor concern.

**Minor quality concerns:** awkward wording, verbosity or weak usefulness without
factual distortion. Severity/Priority/eligible-Assignee judgments are not
automatically fabricated facts. Human review assesses whether recommendations
are reasonably supported; do not demand an exact preferred classification.

Provider errors, refusals and malformed responses are recorded separately as
execution/contract failures. They do not by themselves establish a grounding or
application-security defect. Preserve all failures; no retries until passing.

The runner's narrow `review_flags` only highlight potential conflicts or missing
support. Flags are not semantic verdicts and their absence is not a pass. Review
every factual claim in raw and validated output, including unflagged claims.
No mandatory provenance field, confidence score or production behavior is added.

## Execution and isolation

Default invocation is offline, with explicit dummy credentials, an in-memory SDK
transport and blocked outgoing socket connections. No credential file is loaded.

```powershell
.\.venv\Scripts\python.exe -m tests.ai_evaluation.run_evaluation --offline
.\.venv\Scripts\python.exe -m pytest tests/test_ai_evaluation.py -q
```

Any further live invocation **requires separate approval**. Supply an
API key locally through the environment, never chat, source, CLI arguments or logs.
Each invocation makes at most **six serial attempts**, A–F once each:

```powershell
$env:AI_EVALUATION_ALLOW_LIVE = '1'
try {
    .\.venv\Scripts\python.exe -m tests.ai_evaluation.run_evaluation --live --pass-number 1
} finally {
    Remove-Item Env:AI_EVALUATION_ALLOW_LIVE -ErrorAction SilentlyContinue
}
```

Live mode requires both `--live` and this opt-in. It refuses pytest/CI contexts and
custom provider endpoints, including when called programmatically. Files are not
named `test_*.py`; imports cannot invoke the CLI. Normal pytest/CI only executes
mocked harness tests; there is no live evaluation CI job.

Reuse `build_generation_input`, `create_openai_client`,
`request_openai_suggestions` and `process_provider_response` unchanged. A forwarding
recorder captures the actual SDK arguments/response without substituting prompts
or generation settings: gpt-6-luna, strict schema, store=False, 60-second timeout,
zero SDK retries; no explicit output cap, temperature, seed or reasoning effort.
Record returned model as well as the requested alias; a dated alias snapshot is
accepted and recorded. No new dependencies or changes to the provider adapter,
output schema or validator are required.

The runner never starts FastAPI, calls application APIs or calls the database-backed
`request_suggestions` orchestration. It constructs fictional context models directly.
Before application imports, it sets a fresh absolute temporary DATABASE_NAME and
blocks `sqlite3.connect`; it then rebinds/verifies the cached database setting.
No SQLite database is created or opened. Cached settings/environment are restored,
the temporary directory is removed and SDK clients are closed on exit.
Production history selection, authorization and membership-change handling retain
their existing deterministic tests rather than being duplicated here.

Each invocation writes to a **new** directory under ignored
`ai-evaluation-results/`; existing directories and paths outside that root are
rejected. This is outside pytest-playwright's default `test-results/` cleanup root.
Existing runs are never migrated or deleted by the runner. Do not point pytest's
`--output` at evaluation evidence. Legacy reports still under `test-results/` remain
vulnerable to default plugin cleanup; use a separate disposable pytest `--output`
directory while preserving them. Artifacts contain fictional input and untrusted generated text. Do not
execute rendered text; review unexpected sensitive-looking output before sharing.
No auth headers, API key values or raw exception messages are captured.

## Requests, costs and stop rules

Historical follow-up plan: up to 12 additional attempts in two batches of six,
separately from the 12 original-prompt requests, with review/renewed approval
between batches (`--pass-number 2`). Actual execution then added a separately
authorized six-request formatting check; all 30 results remain in the execution
report. The two historical-clarification invocations both record `pass_number=1`;
their unique timestamps identify the repeat. Compare all repeats, not only the
best output. A pass number labels evidence; it does not automate approval or
prevent another invocation. There are no SDK/harness retries.

Stage A planning estimates were 18–27k input tokens and 6–48k billed output tokens
over twelve calls. At published Standard short-context gpt-6-luna rates checked on
16 October 2026 ($0.10/M input, $0.50/M output), this is approximately $0.005–$0.03,
before account-specific differences. [Pricing source](https://developers.openai.com/api/docs/models/gpt-6-luna).
These assumptions are not measurements, account limits or a price guarantee.
Offline usage/cost fields are synthetic, not charged usage. Recheck pricing before
live execution; record actual usage including reasoning/caching details returned.

Hard stop: six attempts per invocation; first request/parse/validation error;
missing usage; unexpected model; attempted SQLite access; context mutation; user interruption during an attempt; or
recorded estimated spend reaching $0.10. A critical semantic failure found in
human review blocks further batches. Save completed/failed attempts and mark the
remaining cases not run. No silent retries or replacement results.

The $0.10 check is an observed-cost pause, not an enforceable per-request dollar
cap; an in-flight request may exceed it. No output cap is added. The earlier $1
contingency proposal still requires live-execution approval. Any evaluation-only
generation cap or other configuration departure needs separate agreement.

## Evidence and closure

`run.json` records UTC date/time, Git revision and tracked-dirty flag, SDK version,
dataset version/hash and full scenario snapshots, protocol text/hash, pass number,
actual production-generated input and request, returned model/IDs/status/raw text,
decoded output, validated output, usage, estimated cost, latency, errors, mechanical
checks, review flags and an initially **unassessed** human-review template.
Git revision alone is insufficient for uncommitted inputs; hashes/snapshots freeze
what was actually evaluated. Store reviewed scoring/rationale alongside the original
artifact; preserve raw evidence unchanged. Compare repeat variability explicitly.

Minimum closure evidence: both runs of all six cases complete; every applicable
grounding dimension passes human review; no unresolved critical failure; actual
grounded nonempty rewriting in B/C and relevant historical support exercised in D.
Empty output is not a product failure, but universally empty/unexercised output
provides insufficient evidence to close the capability gap. Keep Partial if needed.
Do not change expectations after observing output to manufacture passing results.

After review, append actual results and limitations in `test-execution.md`, then
update the single AC-019.2 RTM row only if justified by collective evidence.
This small evaluation is representative AC verification, not proof of zero
hallucinations, comprehensive AI quality/security testing or release readiness.
