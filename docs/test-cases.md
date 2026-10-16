# Test case catalogue

The catalogue owns stable TC IDs and implementation/parameter mappings. The
[RTM](traceability-matrix.md) owns overall AC coverage; [execution records](test-execution.md)
own results. Test bodies and parameter data remain the executable specification.

## Conventions

- Global sequence: TC-001 onward. Never renumber or reuse an assigned ID; next available: **TC-348**.
- One row per conceptual case. Equivalent values/roles/states share an ID; approved distinct outcomes have explicit selectors.
- `All variants` includes every declared parameter combination and internal loop for that named test.
- References identify Python functions or exact Node registered names; generated Node names may share one source registration site.
- `—` means no business AC mapping, not an omitted test. Source comments point back here.
- Source/framework helpers and server launchers support cases; they are not standalone test cases.
- Manual aliases M01–M05 remain stable. Historical exploratory sessions and nonexecutable BDD do not inflate executed TC counts.

## Inventory

| Group | Maintained definitions/groups | TC IDs | Runner cases / variants |
| --- | ---: | ---: | --- |
| Backend pytest (20 modules) | 217 | 228 | 575 cases; 90 parameterized functions |
| Frontend Node (8 files) | 96 registered tests | 96 | Internal loops are variants |
| Playwright (6 modules) | 14 functions | 15 | 15 Chromium scenarios |
| Standalone browser fixtures (2 HTML files) | 3 routines | 3 | 9 divider + 4 destructive-state + 12 native-input variants |
| Structured manual | 5 groups | 5 | M01–M05 |
| Total | 335 | **347** | Definition, conceptual-case and execution counts differ |

The approved splits retain all existing functions: Passed Fix Version supplied/omitted/cleared;
normal/deleted readback; AI eligibility/Developer/outsider; prohibited/invalid AI context;
public identity/AI history; three legacy safeguards; two storage constraints; two deletion
denials; and browser AI failure/empty output. The AI pre-pipeline guard and lifecycle
unassignment state/role matrix each retain one ID.


## tests/test_ai_assist.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-001"></a>TC-001 | AC-018.1, AC-022.1 | Allow eligible project roles to reach AI Assist | API / AI (mocked or unavailable provider) | [`test_ai_assist_requires_authorized_project_role`](../tests/test_ai_assist.py#L60); role in {Project Owner, QA Analyst}; edit in {False, True} |
| <a id="tc-002"></a>TC-002 | AC-018.1, AC-022.1 | Reject Developer AI Assist before service invocation | API / AI (mocked or unavailable provider) | [`test_ai_assist_requires_authorized_project_role`](../tests/test_ai_assist.py#L60); role=Developer; edit in {False, True} |
| <a id="tc-003"></a>TC-003 | AC-018.1, AC-022.1 | Reject outsider AI Assist before service invocation | API / AI (mocked or unavailable provider) | [`test_ai_assist_requires_authorized_project_role`](../tests/test_ai_assist.py#L60); role=non-member; edit in {False, True} |
| <a id="tc-004"></a>TC-004 | AC-018.1, AC-022.1 | AI assist requires authentication | API / AI (mocked or unavailable provider) | [`test_ai_assist_requires_authentication`](../tests/test_ai_assist.py#L87); All variants |
| <a id="tc-005"></a>TC-005 | AC-018.1, AC-022.1 | AI assist checks current bug status | API / AI (mocked or unavailable provider) | [`test_ai_assist_checks_current_bug_status`](../tests/test_ai_assist.py#L98); All variants |
| <a id="tc-006"></a>TC-006 | AC-018.1, AC-022.1 | AI assist rechecks membership | API / AI (mocked or unavailable provider) | [`test_ai_assist_rechecks_membership`](../tests/test_ai_assist.py#L123); All variants |
| <a id="tc-007"></a>TC-007 | AC-018.1, AC-022.1 | AI assist rejects bug outside project | API / AI (mocked or unavailable provider) | [`test_ai_assist_rejects_bug_outside_project`](../tests/test_ai_assist.py#L138); All variants |
| <a id="tc-008"></a>TC-008 | AC-018.3, AC-023.1 | AI assist preserves current form without saving | API / AI (mocked or unavailable provider) | [`test_ai_assist_preserves_current_form_without_saving`](../tests/test_ai_assist.py#L152); All variants |
| <a id="tc-009"></a>TC-009 | AC-018.3 | Reject prohibited fields in AI request context | API / AI (mocked or unavailable provider) | [`test_ai_assist_rejects_invalid_context`](../tests/test_ai_assist.py#L174); field in {fix_version, status, resolution, created_at, updated_at} |
| <a id="tc-010"></a>TC-010 | AC-018.3 | Reject invalid supported AI context values | API / AI (mocked or unavailable provider) | [`test_ai_assist_rejects_invalid_context`](../tests/test_ai_assist.py#L174); field in {title, assignee_id, severity, priority} |
| <a id="tc-011"></a>TC-011 | AC-018.3 | AI assist requires complete snapshot | API / AI (mocked or unavailable provider) | [`test_ai_assist_requires_complete_snapshot`](../tests/test_ai_assist.py#L181); All variants |

## tests/test_ai_context.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-012"></a>TC-012 | AC-019.2, AC-022.2 | AI context preserves submitted form and persisted bugs | API / AI (mocked or unavailable provider) | [`test_ai_context_preserves_submitted_form_and_persisted_bugs`](../tests/test_ai_context.py#L72); All variants |
| <a id="tc-013"></a>TC-013 | AC-019.2, AC-022.2 | AI context retrieves bounded deterministic same project history | API / AI (mocked or unavailable provider) | [`test_ai_context_retrieves_bounded_deterministic_same_project_history`](../tests/test_ai_context.py#L119); All variants |
| <a id="tc-014"></a>TC-014 | AC-019.2, AC-022.2 | AI context includes only current assignable project members | API / AI (mocked or unavailable provider) | [`test_ai_context_includes_only_current_assignable_project_members`](../tests/test_ai_context.py#L153); All variants |
| <a id="tc-015"></a>TC-015 | AC-019.2 | AI context supports empty project history and assignees | API / AI (mocked or unavailable provider) | [`test_ai_context_supports_empty_project_history_and_assignees`](../tests/test_ai_context.py#L183); All variants |
| <a id="tc-016"></a>TC-016 | AC-019.2 | AI context is not constructed for rejected requests | API / AI (mocked or unavailable provider) | [`test_ai_context_is_not_constructed_for_rejected_requests`](../tests/test_ai_context.py#L203); All variants |

## tests/test_ai_generation.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-017"></a>TC-017 | AC-019.2, AC-022.2 | AI generation preserves separate context without mutation | Python unit / AI (offline) | [`test_ai_generation_preserves_separate_context_without_mutation`](../tests/test_ai_generation.py#L37); All variants |
| <a id="tc-018"></a>TC-018 | AC-019.1 | AI generation defines only supported output fields | Python unit / AI (offline) | [`test_ai_generation_defines_only_supported_output_fields`](../tests/test_ai_generation.py#L59); All variants |
| <a id="tc-019"></a>TC-019 | AC-019.3 | AI generation classification rules match application | Python unit / AI (offline) | [`test_ai_generation_classification_rules_match_application`](../tests/test_ai_generation.py#L78); All variants |
| <a id="tc-020"></a>TC-020 | AC-019.3 | AI generation limits assignees to supplied eligible context | Python unit / AI (offline) | [`test_ai_generation_limits_assignees_to_supplied_eligible_context`](../tests/test_ai_generation.py#L91); All variants |
| <a id="tc-021"></a>TC-021 | AC-019.2, AC-022.3 | AI generation instructions define context and safety boundaries | Python unit / AI (offline) | [`test_ai_generation_instructions_define_context_and_safety_boundaries`](../tests/test_ai_generation.py#L103); All variants |
| <a id="tc-022"></a>TC-022 | AC-019.4 | AI generation reuses suggestion envelope and allows zero suggestions | Python unit / AI (offline) | [`test_ai_generation_reuses_suggestion_envelope_and_allows_zero_suggestions`](../tests/test_ai_generation.py#L124); All variants |
| <a id="tc-023"></a>TC-023 | AC-022.2 | AI generation does not introduce account information or secrets | Python unit / AI (offline) | [`test_ai_generation_does_not_introduce_account_information_or_secrets`](../tests/test_ai_generation.py#L144); All variants |

## tests/test_ai_openai.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-024"></a>TC-024 | AC-019.2, AC-022.2 | AI openai sends existing contract with SDK without network or database | Python unit / AI (offline) | [`test_ai_openai_sends_existing_contract_with_sdk_without_network_or_database`](../tests/test_ai_openai.py#L48); All variants |
| <a id="tc-025"></a>TC-025 | AC-019.4 | AI openai returns raw data without domain validation | Python unit / AI (offline) | [`test_ai_openai_returns_raw_data_without_domain_validation`](../tests/test_ai_openai.py#L116); All variants |
| <a id="tc-026"></a>TC-026 | — | AI openai does not expose mutable input to client | Python unit / AI (offline) | [`test_ai_openai_does_not_expose_mutable_input_to_client`](../tests/test_ai_openai.py#L123); All variants |
| <a id="tc-027"></a>TC-027 | AC-019.4, AC-023.1 | AI openai rejects uncompleted output | Python unit / AI (offline) | [`test_ai_openai_rejects_uncompleted_output`](../tests/test_ai_openai.py#L138); All variants |
| <a id="tc-028"></a>TC-028 | AC-019.4, AC-023.1 | AI openai rejects refusal instead of returning suggestions | Python unit / AI (offline) | [`test_ai_openai_rejects_refusal_instead_of_returning_suggestions`](../tests/test_ai_openai.py#L145); All variants |
| <a id="tc-029"></a>TC-029 | AC-019.4, AC-023.1 | AI openai rejects missing or unparseable JSON | Python unit / AI (offline) | [`test_ai_openai_rejects_missing_or_unparseable_json`](../tests/test_ai_openai.py#L154); All variants |
| <a id="tc-030"></a>TC-030 | AC-019.3 | AI openai rejects duplicate JSON properties at any depth | Python unit / AI (offline) | [`test_ai_openai_rejects_duplicate_json_properties_at_any_depth`](../tests/test_ai_openai.py#L171); All variants |
| <a id="tc-031"></a>TC-031 | AC-023.1 | AI openai propagates request failure without fake suggestions | Python unit / AI (offline) | [`test_ai_openai_propagates_request_failure_without_fake_suggestions`](../tests/test_ai_openai.py#L179); All variants |

## tests/test_ai_response.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-032"></a>TC-032 | AC-019.3, AC-022.3 | AI response delegates to validator and returns its result | Python unit / AI (offline) | [`test_ai_response_delegates_to_validator_and_returns_its_result`](../tests/test_ai_response.py#L38); All variants |
| <a id="tc-033"></a>TC-033 | AC-019.4 | AI response retains partial valid suggestions | Python unit / AI (offline) | [`test_ai_response_retains_partial_valid_suggestions`](../tests/test_ai_response.py#L55); All variants |
| <a id="tc-034"></a>TC-034 | AC-019.3 | AI response uses only context assignee eligibility | Python unit / AI (offline) | [`test_ai_response_uses_only_context_assignee_eligibility`](../tests/test_ai_response.py#L70); All variants |
| <a id="tc-035"></a>TC-035 | AC-019.4 | AI response preserves no usable suggestions outcome | Python unit / AI (offline) | [`test_ai_response_preserves_no_usable_suggestions_outcome`](../tests/test_ai_response.py#L88); All variants |
| <a id="tc-036"></a>TC-036 | AC-019.4, AC-022.3, AC-023.1 | AI response propagates malformed response | Python unit / AI (offline) | [`test_ai_response_propagates_malformed_response`](../tests/test_ai_response.py#L98); All variants |
| <a id="tc-037"></a>TC-037 | AC-019.3 | AI response preserves conflicting duplicate behavior | Python unit / AI (offline) | [`test_ai_response_preserves_conflicting_duplicate_behavior`](../tests/test_ai_response.py#L104); All variants |
| <a id="tc-038"></a>TC-038 | AC-022.3 | AI response has no mutation database or provider side effects | Python unit / AI (offline) | [`test_ai_response_has_no_mutation_database_or_provider_side_effects`](../tests/test_ai_response.py#L114); All variants |

## tests/test_ai_suggestions.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-039"></a>TC-039 | AC-019.4 | AI suggestions accept partial set without mutating input | Python unit / AI (offline) | [`test_ai_suggestions_accept_partial_set_without_mutating_input`](../tests/test_ai_suggestions.py#L20); All variants |
| <a id="tc-040"></a>TC-040 | AC-019.1 | AI suggestions accept all supported fields | Python unit / AI (offline) | [`test_ai_suggestions_accept_all_supported_fields`](../tests/test_ai_suggestions.py#L30); All variants |
| <a id="tc-041"></a>TC-041 | AC-019.1, AC-022.3 | AI suggestions exclude unsupported or unmapped fields | Python unit / AI (offline) | [`test_ai_suggestions_exclude_unsupported_or_unmapped_fields`](../tests/test_ai_suggestions.py#L39); All variants |
| <a id="tc-042"></a>TC-042 | AC-019.3, AC-022.3 | AI suggestions exclude non string text without losing valid field | Python unit / AI (offline) | [`test_ai_suggestions_exclude_non_string_text_without_losing_valid_field`](../tests/test_ai_suggestions.py#L47); All variants |
| <a id="tc-043"></a>TC-043 | AC-019.4 | AI suggestions omit blank values without clearing fields | Python unit / AI (offline) | [`test_ai_suggestions_omit_blank_values_without_clearing_fields`](../tests/test_ai_suggestions.py#L55); All variants |
| <a id="tc-044"></a>TC-044 | AC-019.3, AC-022.3 | AI suggestions exclude invalid classification without losing valid field | Python unit / AI (offline) | [`test_ai_suggestions_exclude_invalid_classification_without_losing_valid_field`](../tests/test_ai_suggestions.py#L65); All variants |
| <a id="tc-045"></a>TC-045 | AC-019.3 | AI suggestions accept classification matching bug validation | Python unit / AI (offline) | [`test_ai_suggestions_accept_classification_matching_bug_validation`](../tests/test_ai_suggestions.py#L75); All variants |
| <a id="tc-046"></a>TC-046 | AC-019.3, AC-022.3 | AI suggestions exclude ineligible or non integer assignee | Python unit / AI (offline) | [`test_ai_suggestions_exclude_ineligible_or_non_integer_assignee`](../tests/test_ai_suggestions.py#L83); All variants |
| <a id="tc-047"></a>TC-047 | AC-019.3 | AI suggestions exclude conflicting duplicate field | Python unit / AI (offline) | [`test_ai_suggestions_exclude_conflicting_duplicate_field`](../tests/test_ai_suggestions.py#L90); All variants |
| <a id="tc-048"></a>TC-048 | AC-019.3 | AI suggestions collapse identical duplicates and ignore blank entries | Python unit / AI (offline) | [`test_ai_suggestions_collapse_identical_duplicates_and_ignore_blank_entries`](../tests/test_ai_suggestions.py#L98); All variants |
| <a id="tc-049"></a>TC-049 | AC-019.4, AC-022.3 | AI suggestions report malformed structure as error | Python unit / AI (offline) | [`test_ai_suggestions_report_malformed_structure_as_error`](../tests/test_ai_suggestions.py#L110); All variants |
| <a id="tc-050"></a>TC-050 | AC-019.4 | AI suggestions report no usable suggestions for valid structure | Python unit / AI (offline) | [`test_ai_suggestions_report_no_usable_suggestions_for_valid_structure`](../tests/test_ai_suggestions.py#L122); All variants |
| <a id="tc-051"></a>TC-051 | AC-019.3 | AI suggestions use current assignable project member context | Python unit / AI (offline) | [`test_ai_suggestions_use_current_assignable_project_member_context`](../tests/test_ai_suggestions.py#L129); All variants |

## tests/test_ai_triage.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-052"></a>TC-052 | AC-023.1 | AI triage duplicate JSON is safe failure before validation | API / AI (mocked or unavailable provider) | [`test_ai_triage_duplicate_json_is_safe_failure_before_validation`](../tests/test_ai_triage.py#L63); All variants |
| <a id="tc-053"></a>TC-053 | AC-018.4, AC-019.1, AC-019.2, AC-019.3, AC-019.4, AC-022.2, AC-022.3 | AI triage configured pipeline preserves form and returns validated suggestions | API / AI (mocked or unavailable provider) | [`test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions`](../tests/test_ai_triage.py#L89); All variants |
| <a id="tc-054"></a>TC-054 | AC-022.3 | AI valid suggestion cannot modify bug without user save | API / AI (mocked or unavailable provider) | [`test_ai_valid_suggestion_cannot_modify_bug_without_user_save`](../tests/test_ai_triage.py#L148); All variants |
| <a id="tc-055"></a>TC-055 | AC-023.1 | AI triage unconfigured requests keep 503 without provider work | API / AI (mocked or unavailable provider) | [`test_ai_triage_unconfigured_requests_keep_503_without_provider_work`](../tests/test_ai_triage.py#L192); All variants |
| <a id="tc-056"></a>TC-056 | AC-018.4, AC-019.4, AC-023.2 | AI triage returns distinct no usable suggestions | API / AI (mocked or unavailable provider) | [`test_ai_triage_returns_distinct_no_usable_suggestions`](../tests/test_ai_triage.py#L217); All variants |
| <a id="tc-057"></a>TC-057 | AC-019.3, AC-022.2 | AI triage revalidates current member eligibility | API / AI (mocked or unavailable provider) | [`test_ai_triage_revalidates_current_member_eligibility`](../tests/test_ai_triage.py#L227); All variants |
| <a id="tc-058"></a>TC-058 | AC-019.3 | AI triage excludes assignee removed during generation | API / AI (mocked or unavailable provider) | [`test_ai_triage_excludes_assignee_removed_during_generation`](../tests/test_ai_triage.py#L250); All variants |
| <a id="tc-059"></a>TC-059 | AC-022.1 | AI triage configured requests authorize before any pipeline work | API / AI (mocked or unavailable provider) | [`test_ai_triage_configured_requests_authorize_before_any_pipeline_work`](../tests/test_ai_triage.py#L287); All variants |
| <a id="tc-060"></a>TC-060 | AC-022.1 | AI triage rechecks changed role before provider invocation | API / AI (mocked or unavailable provider) | [`test_ai_triage_rechecks_changed_role_before_provider_invocation`](../tests/test_ai_triage.py#L315); All variants |
| <a id="tc-061"></a>TC-061 | AC-022.3 | AI triage instruction like content and output cannot perform actions | API / AI (mocked or unavailable provider) | [`test_ai_triage_instruction_like_content_and_output_cannot_perform_actions`](../tests/test_ai_triage.py#L352); All variants |
| <a id="tc-062"></a>TC-062 | AC-018.4, AC-019.4, AC-023.1 | AI triage failures are safe errors without persistence | API / AI (mocked or unavailable provider) | [`test_ai_triage_failures_are_safe_errors_without_persistence`](../tests/test_ai_triage.py#L390); All variants |
| <a id="tc-063"></a>TC-063 | AC-023.1 | AI triage timeout is safe without retries or persistence | API / AI (mocked or unavailable provider) | [`test_ai_triage_timeout_is_safe_without_retries_or_persistence`](../tests/test_ai_triage.py#L419); All variants |
| <a id="tc-064"></a>TC-064 | — | AI triage configuration is checked on each request | API / AI (mocked or unavailable provider) | [`test_ai_triage_configuration_is_checked_on_each_request`](../tests/test_ai_triage.py#L436); All variants |
| <a id="tc-065"></a>TC-065 | — | AI triage client factory disables retries without reading credentials | API / AI (mocked or unavailable provider) | [`test_ai_triage_client_factory_disables_retries_without_reading_credentials`](../tests/test_ai_triage.py#L452); All variants |

## tests/test_bug.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-066"></a>TC-066 | AC-011.1 | Project member can create bug | API / integration | [`test_project_member_can_create_bug`](../tests/test_bug.py#L5); All variants |
| <a id="tc-067"></a>TC-067 | AC-011.2 | Bug creation rejected without title | API / integration | [`test_bug_creation_rejected_without_title`](../tests/test_bug.py#L64); All variants |
| <a id="tc-068"></a>TC-068 | AC-011.3 | Non member cannot create bug | API / integration | [`test_non_member_cannot_create_bug`](../tests/test_bug.py#L95); All variants |
| <a id="tc-069"></a>TC-069 | AC-011.4 | Bug can be created with optional information | API / integration | [`test_bug_can_be_created_with_optional_information`](../tests/test_bug.py#L133); All variants |
| <a id="tc-070"></a>TC-070 | AC-012.1 | Project member can view bug list | API / integration | [`test_project_member_can_view_bug_list`](../tests/test_bug.py#L208); All variants |
| <a id="tc-071"></a>TC-071 | AC-012.2 | Project member can open bug report | API / integration | [`test_project_member_can_open_bug_report`](../tests/test_bug.py#L261); All variants |
| <a id="tc-072"></a>TC-072 | AC-012.3 | Non member cannot open bug report | API / integration | [`test_non_member_cannot_open_bug_report`](../tests/test_bug.py#L367); All variants |
| <a id="tc-073"></a>TC-073 | AC-012.3 | Non member cannot retrieve another projects bug collection | API / integration | [`test_non_member_cannot_retrieve_another_projects_bug_collection`](../tests/test_bug.py#L416); All variants |
| <a id="tc-074"></a>TC-074 | AC-012.4 | Bug list defaults to most recently updated first | API / integration | [`test_bug_list_defaults_to_most_recently_updated_first`](../tests/test_bug.py#L455); All variants |
| <a id="tc-075"></a>TC-075 | AC-013.1 | Project member can edit bug report | API / integration | [`test_project_member_can_edit_bug_report`](../tests/test_bug.py#L544); All variants |
| <a id="tc-076"></a>TC-076 | — | Bug update rejected with null title | API / integration | [`test_bug_update_rejected_with_null_title`](../tests/test_bug.py#L600); All variants |
| <a id="tc-077"></a>TC-077 | AC-013.2 | Project member can update optional bug information | API / integration | [`test_project_member_can_update_optional_bug_information`](../tests/test_bug.py#L661); All variants |
| <a id="tc-078"></a>TC-078 | AC-013.3 | Non member cannot edit bug report | API / integration | [`test_non_member_cannot_edit_bug_report`](../tests/test_bug.py#L743); All variants |
| <a id="tc-079"></a>TC-079 | AC-014.1 | Authorized member can delete bug | API / integration | [`test_authorized_member_can_delete_bug`](../tests/test_bug.py#L803); All variants |
| <a id="tc-080"></a>TC-080 | AC-014.2 | Reject Developer bug deletion and preserve the report | API / integration | [`test_unauthorized_member_cannot_delete_bug`](../tests/test_bug.py#L876); role=Developer |
| <a id="tc-081"></a>TC-081 | AC-014.2 | Reject outsider bug deletion and preserve the report | API / integration | [`test_unauthorized_member_cannot_delete_bug`](../tests/test_bug.py#L876); role=non-member |
| <a id="tc-082"></a>TC-082 | AC-015.1 | Authorized member can assign bug | API / integration | [`test_authorized_member_can_assign_bug`](../tests/test_bug.py#L959); All variants |
| <a id="tc-083"></a>TC-083 | AC-015.1 | Authorized member can unassign bug | API / integration | [`test_authorized_member_can_unassign_bug`](../tests/test_bug.py#L1061); All variants |
| <a id="tc-084"></a>TC-084 | AC-015.1 | Bug unassignment is rejected outside triage | API / integration | [`test_bug_unassignment_is_rejected_outside_triage`](../tests/test_bug.py#L1173); All variants |
| <a id="tc-085"></a>TC-085 | AC-015.2 | Bug cannot be assigned to invalid member | API / integration | [`test_bug_cannot_be_assigned_to_invalid_member`](../tests/test_bug.py#L1219); All variants |
| <a id="tc-086"></a>TC-086 | AC-015.1, AC-015.3 | Non member cannot assign bug | API / integration | [`test_non_member_cannot_assign_bug`](../tests/test_bug.py#L1284); All variants |
| <a id="tc-087"></a>TC-087 | AC-015.4 | Authorized member can reassign bug | API / integration | [`test_authorized_member_can_reassign_bug`](../tests/test_bug.py#L1360); All variants |
| <a id="tc-088"></a>TC-088 | AC-016.1 | Project member can set bug severity | API / integration | [`test_project_member_can_set_bug_severity`](../tests/test_bug.py#L1445); All variants |
| <a id="tc-089"></a>TC-089 | AC-016.2 | Project member can set bug priority | API / integration | [`test_project_member_can_set_bug_priority`](../tests/test_bug.py#L1537); All variants |
| <a id="tc-090"></a>TC-090 | AC-016.3 | Project member can update bug classification | API / integration | [`test_project_member_can_update_bug_classification`](../tests/test_bug.py#L1625); All variants |
| <a id="tc-091"></a>TC-091 | AC-016.4 | Non member cannot update bug classification | API / integration | [`test_non_member_cannot_update_bug_classification`](../tests/test_bug.py#L1714); All variants |
| <a id="tc-092"></a>TC-092 | — | Bug rejects invalid severity | API / integration | [`test_bug_rejects_invalid_severity`](../tests/test_bug.py#L1774); All variants |
| <a id="tc-093"></a>TC-093 | — | Bug rejects invalid priority | API / integration | [`test_bug_rejects_invalid_priority`](../tests/test_bug.py#L1846); All variants |
| <a id="tc-094"></a>TC-094 | AC-017.1 | New bug starts in triage | API / integration | [`test_new_bug_starts_in_triage`](../tests/test_bug.py#L1897); All variants |
| <a id="tc-095"></a>TC-095 | AC-017.2 | Project owner or QA can move bug from triage to open | API / integration | [`test_project_owner_or_qa_can_move_bug_from_triage_to_open`](../tests/test_bug.py#L1935); All variants |
| <a id="tc-096"></a>TC-096 | AC-017.2 | Triage to open can assign eligible project member | API / integration | [`test_triage_to_open_can_assign_eligible_project_member`](../tests/test_bug.py#L2017); All variants |
| <a id="tc-097"></a>TC-097 | AC-017.2 | Triage to open rejects ineligible assignee | API / integration | [`test_triage_to_open_rejects_ineligible_assignee`](../tests/test_bug.py#L2067); All variants |
| <a id="tc-098"></a>TC-098 | AC-017.2 | Developer cannot move bug from triage to open | API / integration | [`test_developer_cannot_move_bug_from_triage_to_open`](../tests/test_bug.py#L2115); All variants |
| <a id="tc-099"></a>TC-099 | AC-017.2 | Bug without assignee cannot move from triage to open | API / integration | [`test_bug_without_assignee_cannot_move_from_triage_to_open`](../tests/test_bug.py#L2179); All variants |
| <a id="tc-100"></a>TC-100 | AC-017.3 | QA analyst cannot move bug from open to development | API / integration | [`test_qa_analyst_cannot_move_bug_from_open_to_development`](../tests/test_bug.py#L2227); All variants |
| <a id="tc-101"></a>TC-101 | AC-017.3 | Project owner can move bug from open to development | API / integration | [`test_project_owner_can_move_bug_from_open_to_development`](../tests/test_bug.py#L2313); All variants |
| <a id="tc-102"></a>TC-102 | AC-017.3 | Open to development requires valid developer assignee | API / integration | [`test_open_to_development_requires_valid_developer_assignee`](../tests/test_bug.py#L2402); All variants |
| <a id="tc-103"></a>TC-103 | AC-017.3 | Non assigned developer cannot move bug from open to development | API / integration | [`test_non_assigned_developer_cannot_move_bug_from_open_to_development`](../tests/test_bug.py#L2467); All variants |
| <a id="tc-104"></a>TC-104 | AC-017.4 | Assigned developer can move bug from development to testing | API / integration | [`test_assigned_developer_can_move_bug_from_development_to_testing`](../tests/test_bug.py#L2553); All variants |
| <a id="tc-105"></a>TC-105 | AC-017.4 | Project owner can move bug from development to testing | API / integration | [`test_project_owner_can_move_bug_from_development_to_testing`](../tests/test_bug.py#L2657); All variants |
| <a id="tc-106"></a>TC-106 | AC-017.4 | Non assigned developer cannot move bug from development to testing | API / integration | [`test_non_assigned_developer_cannot_move_bug_from_development_to_testing`](../tests/test_bug.py#L2752); All variants |
| <a id="tc-107"></a>TC-107 | AC-017.4 | Bug cannot move to testing with developer assignee | API / integration | [`test_bug_cannot_move_to_testing_with_developer_assignee`](../tests/test_bug.py#L2863); All variants |
| <a id="tc-108"></a>TC-108 | AC-017.5 | Assigned QA can pass bug and close it | API / integration | [`test_assigned_qa_can_pass_bug_and_close_it`](../tests/test_bug.py#L2962); All variants |
| <a id="tc-109"></a>TC-109 | AC-017.5 | Project owner can pass bug and close it | API / integration | [`test_project_owner_can_pass_bug_and_close_it`](../tests/test_bug.py#L3102); All variants |
| <a id="tc-110"></a>TC-110 | AC-017.5 | Assigned QA can fail bug and return it to development | API / integration | [`test_assigned_qa_can_fail_bug_and_return_it_to_development`](../tests/test_bug.py#L3203); All variants |
| <a id="tc-111"></a>TC-111 | AC-017.5 | Project owner can fail bug and return it to development | API / integration | [`test_project_owner_can_fail_bug_and_return_it_to_development`](../tests/test_bug.py#L3316); All variants |
| <a id="tc-112"></a>TC-112 | AC-017.5 | Failed testing requires valid developer assignee | API / integration | [`test_failed_testing_requires_valid_developer_assignee`](../tests/test_bug.py#L3436); All variants |
| <a id="tc-113"></a>TC-113 | AC-017.5 | Non assigned QA cannot record testing outcome | API / integration | [`test_non_assigned_qa_cannot_record_testing_outcome`](../tests/test_bug.py#L3533); All variants |
| <a id="tc-114"></a>TC-114 | AC-017.5 | Testing outcome is required | API / integration | [`test_testing_outcome_is_required`](../tests/test_bug.py#L3656); All variants |
| <a id="tc-115"></a>TC-115 | AC-017.5 | Invalid testing outcome is rejected | API / integration | [`test_invalid_testing_outcome_is_rejected`](../tests/test_bug.py#L3774); All variants |
| <a id="tc-116"></a>TC-116 | AC-017.6 | Assigned developer can close bug without fixing | API / integration | [`test_assigned_developer_can_close_bug_without_fixing`](../tests/test_bug.py#L3891); All variants |
| <a id="tc-117"></a>TC-117 | AC-017.6 | Project owner can close bug without fixing | API / integration | [`test_project_owner_can_close_bug_without_fixing`](../tests/test_bug.py#L3988); All variants |
| <a id="tc-118"></a>TC-118 | AC-017.6 | Non assigned developer cannot close bug without fixing | API / integration | [`test_non_assigned_developer_cannot_close_bug_without_fixing`](../tests/test_bug.py#L4081); All variants |
| <a id="tc-119"></a>TC-119 | AC-017.6 | Bug cannot be closed without resolution | API / integration | [`test_bug_cannot_be_closed_without_resolution`](../tests/test_bug.py#L4168); All variants |
| <a id="tc-120"></a>TC-120 | AC-017.6 | Fixed resolution cannot be manually selected when closing bug | API / integration | [`test_fixed_resolution_cannot_be_manually_selected_when_closing_bug`](../tests/test_bug.py#L4254); All variants |
| <a id="tc-121"></a>TC-121 | AC-017.7 | Project owner can move closed bug to triage | API / integration | [`test_project_owner_can_move_closed_bug_to_triage`](../tests/test_bug.py#L4503); All variants |
| <a id="tc-122"></a>TC-122 | AC-017.7 | Project owner can move unassigned closed bug to triage | API / integration | [`test_project_owner_can_move_unassigned_closed_bug_to_triage`](../tests/test_bug.py#L4539); All variants |
| <a id="tc-123"></a>TC-123 | AC-017.7 | Unauthorized user cannot move closed bug to triage | API / integration | [`test_unauthorized_user_cannot_move_closed_bug_to_triage`](../tests/test_bug.py#L4592); All variants |
| <a id="tc-124"></a>TC-124 | AC-017.7 | Closed bug rejects invalid direct transition | API / integration | [`test_closed_bug_rejects_invalid_direct_transition`](../tests/test_bug.py#L4636); All variants |
| <a id="tc-125"></a>TC-125 | AC-017.7 | Closed to triage rejects extra transition data | API / integration | [`test_closed_to_triage_rejects_extra_transition_data`](../tests/test_bug.py#L4672); All variants |
| <a id="tc-126"></a>TC-126 | AC-017.8 | Bug cannot skip from triage to development | API / integration | [`test_bug_cannot_skip_from_triage_to_development`](../tests/test_bug.py#L4714); All variants |
| <a id="tc-127"></a>TC-127 | AC-017.8 | Bug cannot skip from open to testing | API / integration | [`test_bug_cannot_skip_from_open_to_testing`](../tests/test_bug.py#L4776); All variants |
| <a id="tc-128"></a>TC-128 | AC-017.8 | Bug cannot move from development back to open | API / integration | [`test_bug_cannot_move_from_development_back_to_open`](../tests/test_bug.py#L4863); All variants |
| <a id="tc-129"></a>TC-129 | AC-017.8 | Bug cannot move from testing back to open | API / integration | [`test_bug_cannot_move_from_testing_back_to_open`](../tests/test_bug.py#L4949); All variants |
| <a id="tc-130"></a>TC-130 | AC-017.8 | Bug cannot move from testing back to triage | API / integration | [`test_bug_cannot_move_from_testing_back_to_triage`](../tests/test_bug.py#L5060); All variants |
| <a id="tc-131"></a>TC-131 | AC-017.9 | Changing bug status updates last updated timestamp | API / integration | [`test_changing_bug_status_updates_last_updated_timestamp`](../tests/test_bug.py#L5171); All variants |

## tests/test_bug_numbers.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-132"></a>TC-132 | AC-011.1 | Bug numbers are independent and routes use local numbers | API / integration | [`test_bug_numbers_are_independent_and_routes_use_local_numbers`](../tests/test_bug_numbers.py#L27); All variants |
| <a id="tc-133"></a>TC-133 | AC-011.1 | Deleted bug numbers are not reused | API / integration | [`test_deleted_bug_numbers_are_not_reused`](../tests/test_bug_numbers.py#L58); All variants |
| <a id="tc-134"></a>TC-134 | AC-013.1 | Bug number is preserved on edit | API / integration | [`test_bug_number_is_preserved_on_edit`](../tests/test_bug_numbers.py#L69); All variants |
| <a id="tc-135"></a>TC-135 | AC-012.2 | Resolve public bug routes by project and local number | API / integration | [`test_public_bug_routes_use_local_number_and_isolate_projects`](../tests/test_bug_numbers.py#L82); operation in {details, edit, status, delete, ai-assist} |
| <a id="tc-136"></a>TC-136 | AC-019.2, AC-022.2 | Keep AI history exclusion tied to internal identity after public resolution | API / integration | [`test_public_bug_routes_use_local_number_and_isolate_projects`](../tests/test_bug_numbers.py#L82); operation=ai-assist |
| <a id="tc-137"></a>TC-137 | — | Failed creation rolls back bug and counter | API / integration | [`test_failed_creation_rolls_back_bug_and_counter`](../tests/test_bug_numbers.py#L141); All variants |
| <a id="tc-138"></a>TC-138 | AC-011.1 | Concurrent creation allocates unique bug numbers | API / integration | [`test_concurrent_creation_allocates_unique_bug_numbers`](../tests/test_bug_numbers.py#L184); All variants |

## tests/test_bug_update_readback.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-139"></a>TC-139 | — | Return committed edit/status data through durable readback | API / integration | [`test_bug_update_response_readback_after_commit`](../tests/test_bug_update_readback.py#L10); delete_before_readback=False; operation in {edit, status} |
| <a id="tc-140"></a>TC-140 | — | Return consistent not-found feedback if deleted before readback | API / integration | [`test_bug_update_response_readback_after_commit`](../tests/test_bug_update_readback.py#L10); delete_before_readback=True; operation in {edit, status} |

## tests/test_database_isolation.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-141"></a>TC-141 | — | Client rebinds cached database before startup | Database / infrastructure | [`test_client_rebinds_cached_database_before_startup`](../tests/test_database_isolation.py#L9); All variants |
| <a id="tc-142"></a>TC-142 | — | Client starts with fresh database | Database / infrastructure | [`test_client_starts_with_fresh_database`](../tests/test_database_isolation.py#L44); All variants |

## tests/test_database_lifecycle.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-143"></a>TC-143 | — | Importing application does not create database | Database / infrastructure | [`test_importing_application_does_not_create_database`](../tests/test_database_lifecycle.py#L28); All variants |
| <a id="tc-144"></a>TC-144 | — | Application lifespan initializes schema before requests | Database / infrastructure | [`test_application_lifespan_initializes_schema_before_requests`](../tests/test_database_lifecycle.py#L38); All variants |

## tests/test_database_migrations.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-145"></a>TC-145 | — | Fresh database creates numbering schema | Database / infrastructure | [`test_fresh_database_creates_numbering_schema`](../tests/test_database_migrations.py#L68); All variants |
| <a id="tc-146"></a>TC-146 | — | Legacy backfill preserves every field and is idempotent | Database / infrastructure | [`test_legacy_backfill_preserves_every_field_and_is_idempotent`](../tests/test_database_migrations.py#L80); All variants |
| <a id="tc-147"></a>TC-147 | — | Migration failure rolls back schema data and version | Database / infrastructure | [`test_migration_failure_rolls_back_schema_data_and_version`](../tests/test_database_migrations.py#L109); All variants |
| <a id="tc-148"></a>TC-148 | — | Refuse unexpected or partially migrated legacy schema | Database / infrastructure | [`test_migration_rejects_unexpected_partial_or_inconsistent_legacy_schema`](../tests/test_database_migrations.py#L171); mutation starts with ALTER or CREATE (7 variants) |
| <a id="tc-149"></a>TC-149 | — | Refuse unsupported database schema versions | Database / infrastructure | [`test_migration_rejects_unexpected_partial_or_inconsistent_legacy_schema`](../tests/test_database_migrations.py#L171); mutation=PRAGMA user_version=2 |
| <a id="tc-150"></a>TC-150 | — | Refuse legacy data with broken relationships | Database / infrastructure | [`test_migration_rejects_unexpected_partial_or_inconsistent_legacy_schema`](../tests/test_database_migrations.py#L171); mutation=DELETE FROM users WHERE id=2 |
| <a id="tc-151"></a>TC-151 | — | Enforce positive integer report numbers in storage | Database / infrastructure | [`test_numbering_constraints_reject_invalid_storage`](../tests/test_database_migrations.py#L187); field=bug_number; all associated values |
| <a id="tc-152"></a>TC-152 | — | Enforce positive integer allocation counters in storage | Database / infrastructure | [`test_numbering_constraints_reject_invalid_storage`](../tests/test_database_migrations.py#L187); field=next_bug_number; all associated values |
| <a id="tc-153"></a>TC-153 | — | Numbering uniqueness is scoped to project | Database / infrastructure | [`test_numbering_uniqueness_is_scoped_to_project`](../tests/test_database_migrations.py#L199); All variants |
| <a id="tc-154"></a>TC-154 | — | Current schema rejects invalid counter without repair | Database / infrastructure | [`test_current_schema_rejects_invalid_counter_without_repair`](../tests/test_database_migrations.py#L209); All variants |

## tests/test_fix_version_on_pass.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-155"></a>TC-155 | AC-017.5 | Persist a supplied Fix Version during Passed | API / integration | [`test_passed_transition_persists_optional_fix_version`](../tests/test_fix_version_on_pass.py#L68); param IDs: qa-supplied, owner-supplied, unchanged, replace-existing, no-trimming, whitespace-unchanged |
| <a id="tc-156"></a>TC-156 | AC-017.5 | Preserve the existing Fix Version when Passed omits it | API / integration | [`test_passed_transition_persists_optional_fix_version`](../tests/test_fix_version_on_pass.py#L68); param IDs: omitted-preserves, omitted-blank |
| <a id="tc-157"></a>TC-157 | AC-017.5 | Clear Fix Version with explicit null or empty Passed input | API / integration | [`test_passed_transition_persists_optional_fix_version`](../tests/test_fix_version_on_pass.py#L68); param IDs: blank, clear-existing, api-empty-string |
| <a id="tc-158"></a>TC-158 | AC-017.5 | Failed transition clears legacy fix version | API / integration | [`test_failed_transition_clears_legacy_fix_version`](../tests/test_fix_version_on_pass.py#L93); All variants |
| <a id="tc-159"></a>TC-159 | AC-017.5 | Fix version is rejected outside passed transition | API / integration | [`test_fix_version_is_rejected_outside_passed_transition`](../tests/test_fix_version_on_pass.py#L124); All variants |
| <a id="tc-160"></a>TC-160 | AC-011.4 | Bug creation allows empty fix version | API / integration | [`test_bug_creation_allows_empty_fix_version`](../tests/test_fix_version_on_pass.py#L144); All variants |
| <a id="tc-161"></a>TC-161 | AC-011.4 | Bug creation rejects nonempty fix version | API / integration | [`test_bug_creation_rejects_nonempty_fix_version`](../tests/test_fix_version_on_pass.py#L158); All variants |
| <a id="tc-162"></a>TC-162 | AC-013.2 | Unresolved bug edit rejects nonempty fix version | API / integration | [`test_unresolved_bug_edit_rejects_nonempty_fix_version`](../tests/test_fix_version_on_pass.py#L176); All variants |
| <a id="tc-163"></a>TC-163 | AC-013.2 | Unresolved bug edit clears legacy fix version | API / integration | [`test_unresolved_bug_edit_clears_legacy_fix_version`](../tests/test_fix_version_on_pass.py#L188); All variants |
| <a id="tc-164"></a>TC-164 | AC-013.2 | Closed fixed bug fix version can be edited and cleared | API / integration | [`test_closed_fixed_bug_fix_version_can_be_edited_and_cleared`](../tests/test_fix_version_on_pass.py#L202); All variants |
| <a id="tc-165"></a>TC-165 | AC-017.7 | Reopening clears resolution and fix version | API / integration | [`test_reopening_clears_resolution_and_fix_version`](../tests/test_fix_version_on_pass.py#L220); All variants |
| <a id="tc-166"></a>TC-166 | AC-017.6 | Nonfixed closure clears fix version and rejects assignment | API / integration | [`test_nonfixed_closure_clears_fix_version_and_rejects_assignment`](../tests/test_fix_version_on_pass.py#L237); All variants |
| <a id="tc-167"></a>TC-167 | AC-013.2 | Nonfixed bug edit clears legacy fix version | API / integration | [`test_nonfixed_bug_edit_clears_legacy_fix_version`](../tests/test_fix_version_on_pass.py#L254); All variants |
| <a id="tc-168"></a>TC-168 | AC-017.5 | Passed fix version preserves authorization | API / integration | [`test_passed_fix_version_preserves_authorization`](../tests/test_fix_version_on_pass.py#L276); All variants |

## tests/test_jwt_secret.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-169"></a>TC-169 | AC-002.1 | Login and access with configured secret | API / integration | [`test_login_and_access_with_configured_secret`](../tests/test_jwt_secret.py#L22); All variants |
| <a id="tc-170"></a>TC-170 | — | Token signed with configured secret | API / integration | [`test_token_signed_with_configured_secret`](../tests/test_jwt_secret.py#L43); All variants |
| <a id="tc-171"></a>TC-171 | AC-003.3 | Forged token with old secret is rejected | API / integration | [`test_forged_token_with_old_secret_is_rejected`](../tests/test_jwt_secret.py#L65); All variants |
| <a id="tc-172"></a>TC-172 | AC-003.3 | Correctly signed expired token is rejected | API / integration | [`test_correctly_signed_expired_token_is_rejected`](../tests/test_jwt_secret.py#L91); All variants |
| <a id="tc-173"></a>TC-173 | — | Missing or blank JWT secret key rejects authentication | API / integration | [`test_missing_or_blank_jwt_secret_key_rejects_authentication`](../tests/test_jwt_secret.py#L130); All variants |
| <a id="tc-174"></a>TC-174 | — | Secret not in login response | API / integration | [`test_secret_not_in_login_response`](../tests/test_jwt_secret.py#L186); All variants |
| <a id="tc-175"></a>TC-175 | — | Secret not in protected response | API / integration | [`test_secret_not_in_protected_response`](../tests/test_jwt_secret.py#L208); All variants |
| <a id="tc-176"></a>TC-176 | — | Secret not in error response | API / integration | [`test_secret_not_in_error_response`](../tests/test_jwt_secret.py#L227); All variants |

## tests/test_login.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-177"></a>TC-177 | AC-002.1 | Successful login | API / integration | [`test_successful_login`](../tests/test_login.py#L2); All variants |
| <a id="tc-178"></a>TC-178 | AC-002.2 | Login with incorrect password | API / integration | [`test_login_with_incorrect_password`](../tests/test_login.py#L22); All variants |
| <a id="tc-179"></a>TC-179 | AC-002.2 | Login with unknown email | API / integration | [`test_login_with_unknown_email`](../tests/test_login.py#L45); All variants |
| <a id="tc-180"></a>TC-180 | AC-003.1 | Authenticated user can access protected endpoint | API / integration | [`test_authenticated_user_can_access_protected_endpoint`](../tests/test_login.py#L63); All variants |
| <a id="tc-181"></a>TC-181 | AC-003.2 | Unauthenticated user cannot access protected endpoint | API / integration | [`test_unauthenticated_user_cannot_access_protected_endpoint`](../tests/test_login.py#L84); All variants |
| <a id="tc-182"></a>TC-182 | AC-003.3 | Invalid token cannot access protected endpoint | API / integration | [`test_invalid_token_cannot_access_protected_endpoint`](../tests/test_login.py#L91); All variants |

## tests/test_privacy.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-183"></a>TC-183 | — | Privacy policy is public without authentication | API / integration | [`test_privacy_policy_is_public_without_authentication`](../tests/test_privacy.py#L2); All variants |

## tests/test_projects.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-184"></a>TC-184 | AC-005.1 | Create project | API / integration | [`test_create_project`](../tests/test_projects.py#L5); All variants |
| <a id="tc-185"></a>TC-185 | AC-005.2 | Create project with empty name | API / integration | [`test_create_project_with_empty_name`](../tests/test_projects.py#L20); All variants |
| <a id="tc-186"></a>TC-186 | AC-005.2 | Project creation rejects whitespace only name | API / integration | [`test_project_creation_rejects_whitespace_only_name`](../tests/test_projects.py#L43); All variants |
| <a id="tc-187"></a>TC-187 | AC-005.2 | Project creation rejects non string name | API / integration | [`test_project_creation_rejects_non_string_name`](../tests/test_projects.py#L68); All variants |
| <a id="tc-188"></a>TC-188 | AC-005.1 | Project creation preserves padded name | API / integration | [`test_project_creation_preserves_padded_name`](../tests/test_projects.py#L84); All variants |
| <a id="tc-189"></a>TC-189 | AC-005.3 | Unauthenticated user cannot create project | API / integration | [`test_unauthenticated_user_cannot_create_project`](../tests/test_projects.py#L99); All variants |
| <a id="tc-190"></a>TC-190 | AC-006.1 | Get projects | API / integration | [`test_get_projects`](../tests/test_projects.py#L114); All variants |
| <a id="tc-191"></a>TC-191 | AC-006.2 | User only sees own projects | API / integration | [`test_user_only_sees_own_projects`](../tests/test_projects.py#L141); All variants |
| <a id="tc-192"></a>TC-192 | AC-006.3 | Get project | API / integration | [`test_get_project`](../tests/test_projects.py#L180); All variants |
| <a id="tc-193"></a>TC-193 | AC-006.4 | User cannot access another users project | API / integration | [`test_user_cannot_access_another_users_project`](../tests/test_projects.py#L209); All variants |
| <a id="tc-194"></a>TC-194 | AC-007.1 | Edit project name | API / integration | [`test_edit_project_name`](../tests/test_projects.py#L239); All variants |
| <a id="tc-195"></a>TC-195 | AC-007.3 | Project edit rejects empty or whitespace only name | API / integration | [`test_project_edit_rejects_empty_or_whitespace_only_name`](../tests/test_projects.py#L270); All variants |
| <a id="tc-196"></a>TC-196 | AC-007.3 | Project edit rejects non string name | API / integration | [`test_project_edit_rejects_non_string_name`](../tests/test_projects.py#L290); All variants |
| <a id="tc-197"></a>TC-197 | AC-007.1 | Project edit preserves padded name | API / integration | [`test_project_edit_preserves_padded_name`](../tests/test_projects.py#L309); All variants |
| <a id="tc-198"></a>TC-198 | AC-007.2 | User cannot edit another users project name | API / integration | [`test_user_cannot_edit_another_users_project_name`](../tests/test_projects.py#L329); All variants |
| <a id="tc-199"></a>TC-199 | AC-008.1 | Delete project | API / integration | [`test_delete_project`](../tests/test_projects.py#L372); All variants |
| <a id="tc-200"></a>TC-200 | AC-008.1 | New project owner cannot access bugs from deleted project | API / integration | [`test_new_project_owner_cannot_access_bugs_from_deleted_project`](../tests/test_projects.py#L407); All variants |
| <a id="tc-201"></a>TC-201 | AC-008.2 | User cannot delete another users project | API / integration | [`test_user_cannot_delete_another_users_project`](../tests/test_projects.py#L466); All variants |
| <a id="tc-202"></a>TC-202 | AC-009.1 | Owner can add project member | API / integration | [`test_owner_can_add_project_member`](../tests/test_projects.py#L506); All variants |
| <a id="tc-203"></a>TC-203 | AC-009.1 | Added member can access project | API / integration | [`test_added_member_can_access_project`](../tests/test_projects.py#L540); All variants |
| <a id="tc-204"></a>TC-204 | AC-009.2 | Owner can remove project member | API / integration | [`test_owner_can_remove_project_member`](../tests/test_projects.py#L580); All variants |
| <a id="tc-205"></a>TC-205 | AC-009.2, AC-015.1 | Removing member unassigns only their bugs in that project | API / integration | [`test_removing_member_unassigns_only_their_bugs_in_that_project`](../tests/test_projects.py#L619); All variants |
| <a id="tc-206"></a>TC-206 | AC-009.2 | Removed member can no longer access project | API / integration | [`test_removed_member_can_no_longer_access_project`](../tests/test_projects.py#L722); All variants |
| <a id="tc-207"></a>TC-207 | AC-009.3 | Project owner cannot add user who does not have an account | API / integration | [`test_project_owner_cannot_add_user_who_does_not_have_an_account`](../tests/test_projects.py#L769); All variants |
| <a id="tc-208"></a>TC-208 | AC-009.4 | Project owner cannot add same user more than once | API / integration | [`test_project_owner_cannot_add_same_user_more_than_once`](../tests/test_projects.py#L800); All variants |
| <a id="tc-209"></a>TC-209 | AC-009.5 | Project member can view project members | API / integration | [`test_project_member_can_view_project_members`](../tests/test_projects.py#L844); All variants |
| <a id="tc-210"></a>TC-210 | — | Project owner cannot remove themselves | API / integration | [`test_project_owner_cannot_remove_themselves`](../tests/test_projects.py#L928); All variants |
| <a id="tc-211"></a>TC-211 | AC-010.1 | Project creator is project owner | API / integration | [`test_project_creator_is_project_owner`](../tests/test_projects.py#L993); All variants |
| <a id="tc-212"></a>TC-212 | AC-010.2 | QA analyst can access project | API / integration | [`test_qa_analyst_can_access_project`](../tests/test_projects.py#L1029); All variants |
| <a id="tc-213"></a>TC-213 | AC-010.3 | Developer can access project | API / integration | [`test_developer_can_access_project`](../tests/test_projects.py#L1074); All variants |
| <a id="tc-214"></a>TC-214 | AC-010.4 | Non owner cannot manage project members | API / integration | [`test_non_owner_cannot_manage_project_members`](../tests/test_projects.py#L1120); All variants |
| <a id="tc-215"></a>TC-215 | AC-010.5 | Non owner cannot edit project | API / integration | [`test_non_owner_cannot_edit_project`](../tests/test_projects.py#L1202); All variants |
| <a id="tc-216"></a>TC-216 | AC-010.5 | Non owner cannot delete project | API / integration | [`test_non_owner_cannot_delete_project`](../tests/test_projects.py#L1255); All variants |

## tests/test_registration.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-217"></a>TC-217 | AC-001.1 | Successful registration | API / integration | [`test_successful_registration`](../tests/test_registration.py#L8); All variants |
| <a id="tc-218"></a>TC-218 | AC-001.2 | Registration with duplicate email | API / integration | [`test_registration_with_duplicate_email`](../tests/test_registration.py#L26); All variants |
| <a id="tc-219"></a>TC-219 | AC-001.3 | Registration with invalid email | API / integration | [`test_registration_with_invalid_email`](../tests/test_registration.py#L45); All variants |
| <a id="tc-220"></a>TC-220 | AC-001.4 | Registration with short password | API / integration | [`test_registration_with_short_password`](../tests/test_registration.py#L64); All variants |
| <a id="tc-221"></a>TC-221 | AC-001.4 | Registration without uppercase password | API / integration | [`test_registration_without_uppercase_password`](../tests/test_registration.py#L81); All variants |
| <a id="tc-222"></a>TC-222 | AC-001.4 | Registration without lowercase password | API / integration | [`test_registration_without_lowercase_password`](../tests/test_registration.py#L98); All variants |
| <a id="tc-223"></a>TC-223 | AC-001.4 | Registration without number password | API / integration | [`test_registration_without_number_password`](../tests/test_registration.py#L115); All variants |
| <a id="tc-224"></a>TC-224 | — | Registration rejects invalid password for existing email | API / integration | [`test_registration_rejects_invalid_password_for_existing_email`](../tests/test_registration.py#L133); All variants |
| <a id="tc-225"></a>TC-225 | AC-001.5 | Password is not stored as plain text | Database / security | [`test_password_is_not_stored_as_plain_text`](../tests/test_registration.py#L155); All variants |
| <a id="tc-226"></a>TC-226 | — | Registration rejects password over bcrypt limit | API / integration | [`test_registration_rejects_password_over_bcrypt_limit`](../tests/test_registration.py#L178); All variants |

## tests/test_version.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-227"></a>TC-227 | — | Application version is shared by openapi and endpoint | API / integration | [`test_application_version_is_shared_by_openapi_and_endpoint`](../tests/test_version.py#L5); All variants |
| <a id="tc-228"></a>TC-228 | — | About page includes application version loader | API / integration | [`test_about_page_includes_application_version_loader`](../tests/test_version.py#L18); All variants |

## tests/frontend/ai-assist.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-229"></a>TC-229 | AC-020.2, AC-020.4 | AI native text input mismatches are excluded before use or use all | Frontend JS / DOM substitutes | [`test_ai_native_text_input_mismatches_are_excluded_before_use_or_use_all`](../tests/frontend/ai-assist.test.cjs#L39); All variants |
| <a id="tc-230"></a>TC-230 | AC-019.4, AC-023.2 | AI all native input mismatches allow manual work and retry | Frontend JS / DOM substitutes | [`test_ai_all_native_input_mismatches_allow_manual_work_and_retry`](../tests/frontend/ai-assist.test.cjs#L67); All variants |
| <a id="tc-231"></a>TC-231 | AC-018.3 | Collect AI context preserves blank and unsaved values | Frontend JS / DOM substitutes | [`test_collect_ai_context_preserves_blank_and_unsaved_values`](../tests/frontend/ai-assist.test.cjs#L82); All variants |
| <a id="tc-232"></a>TC-232 | AC-018.2, AC-023.1 | Submit AI context limits requests and reports unavailable | Frontend JS / DOM substitutes | [`test_submit_ai_context_limits_requests_and_reports_unavailable`](../tests/frontend/ai-assist.test.cjs#L114); All variants |
| <a id="tc-233"></a>TC-233 | AC-023.1 | Submit AI context recovers from network failure | Frontend JS / DOM substitutes | [`test_submit_ai_context_recovers_from_network_failure`](../tests/frontend/ai-assist.test.cjs#L143); All variants |
| <a id="tc-234"></a>TC-234 | — | AI classification suggestions keep semantic value classes | Frontend JS / DOM substitutes | [`test_ai_classification_suggestions_keep_semantic_value_classes`](../tests/frontend/ai-assist.test.cjs#L153); All variants |
| <a id="tc-235"></a>TC-235 | AC-020.1, AC-021.1, AC-022.3 | AI suggestions review separates values and follows form order | Frontend JS / DOM substitutes | [`test_ai_suggestions_review_separates_values_and_follows_form_order`](../tests/frontend/ai-assist.test.cjs#L175); All variants |
| <a id="tc-236"></a>TC-236 | AC-021.1 | AI pending guidance uses bottom status and clears after review | Frontend JS / DOM substitutes | [`test_ai_pending_guidance_uses_bottom_status_and_clears_after_review`](../tests/frontend/ai-assist.test.cjs#L227); All variants |
| <a id="tc-237"></a>TC-237 | AC-020.1 | AI review tracks current values after manual edits | Frontend JS / DOM substitutes | [`test_ai_review_tracks_current_values_after_manual_edits`](../tests/frontend/ai-assist.test.cjs#L266); All variants |
| <a id="tc-238"></a>TC-238 | AC-020.2, AC-021.1 | AI use replaces value removes pending and remains editable | Frontend JS / DOM substitutes | [`test_ai_use_replaces_value_removes_pending_and_remains_editable`](../tests/frontend/ai-assist.test.cjs#L284); All variants |
| <a id="tc-239"></a>TC-239 | AC-020.3 | AI dismiss preserves form and excludes field from use all | Frontend JS / DOM substitutes | [`test_ai_dismiss_preserves_form_and_excludes_field_from_use_all`](../tests/frontend/ai-assist.test.cjs#L311); All variants |
| <a id="tc-240"></a>TC-240 | AC-020.4, AC-021.1 | AI use all applies only pending values without reapplying used fields | Frontend JS / DOM substitutes | [`test_ai_use_all_applies_only_pending_values_without_reapplying_used_fields`](../tests/frontend/ai-assist.test.cjs#L328); All variants |
| <a id="tc-241"></a>TC-241 | AC-020.5 | AI dismiss all preserves used and other form values | Frontend JS / DOM substitutes | [`test_ai_dismiss_all_preserves_used_and_other_form_values`](../tests/frontend/ai-assist.test.cjs#L352); All variants |
| <a id="tc-242"></a>TC-242 | AC-020.6 | AI repeat request waits for resolution and uses latest form | Frontend JS / DOM substitutes | [`test_ai_repeat_request_waits_for_resolution_and_uses_latest_form`](../tests/frontend/ai-assist.test.cjs#L368); All variants |
| <a id="tc-243"></a>TC-243 | AC-023.2 | AI no usable suggestions is success and allows manual work and retry | Frontend JS / DOM substitutes | [`test_ai_no_usable_suggestions_is_success_and_allows_manual_work_and_retry`](../tests/frontend/ai-assist.test.cjs#L387); All variants |
| <a id="tc-244"></a>TC-244 | AC-023.1, AC-023.2 | AI failed or malformed responses preserve form and allow retry | Frontend JS / DOM substitutes | [`test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry`](../tests/frontend/ai-assist.test.cjs#L407); All variants |
| <a id="tc-245"></a>TC-245 | AC-020.8 | AI cancel discards pending and detached actions cannot apply | Frontend JS / DOM substitutes | [`test_ai_cancel_discards_pending_and_detached_actions_cannot_apply`](../tests/frontend/ai-assist.test.cjs#L452); All variants |
| <a id="tc-246"></a>TC-246 | AC-020.8, AC-023.1 | AI late success or error cannot populate reopened session | Frontend JS / DOM substitutes | [`test_ai_late_success_or_error_cannot_populate_reopened_session`](../tests/frontend/ai-assist.test.cjs#L475); All variants |
| <a id="tc-247"></a>TC-247 | AC-020.8, AC-023.1 | AI late JSON cannot replace later results | Frontend JS / DOM substitutes | [`test_ai_late_json_cannot_replace_later_results`](../tests/frontend/ai-assist.test.cjs#L498); All variants |
| <a id="tc-248"></a>TC-248 | AC-020.8 | AI results do not populate hidden or disconnected forms | Frontend JS / DOM substitutes | [`test_ai_results_do_not_populate_hidden_or_disconnected_forms`](../tests/frontend/ai-assist.test.cjs#L521); All variants |
| <a id="tc-249"></a>TC-249 | AC-020.8 | AI sessions are isolated between new and edit forms | Frontend JS / DOM substitutes | [`test_ai_sessions_are_isolated_between_new_and_edit_forms`](../tests/frontend/ai-assist.test.cjs#L535); All variants |
| <a id="tc-250"></a>TC-250 | AC-020.7, AC-021.1, AC-022.3 | AI use all maps every supported field without persistence | Frontend JS / DOM substitutes | [`test_ai_use_all_maps_every_supported_field_without_persistence`](../tests/frontend/ai-assist.test.cjs#L548); All variants |
| <a id="tc-251"></a>TC-251 | AC-020.2 | AI validated assignee missing from dropdown is reviewable and usable | Frontend JS / DOM substitutes | [`test_ai_validated_assignee_missing_from_dropdown_is_reviewable_and_usable`](../tests/frontend/ai-assist.test.cjs#L571); All variants |

## tests/frontend/ai-disclosure.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-252"></a>TC-252 | AC-022.2 | New bug AI disclosure is near and describes AI assist | Frontend JS / DOM substitutes | [`test_new_bug_ai_disclosure_is_near_and_describes_ai_assist`](../tests/frontend/ai-disclosure.test.cjs#L44); All variants |
| <a id="tc-253"></a>TC-253 | AC-022.2 | Edit bug AI disclosure is near and describes AI assist | Frontend JS / DOM substitutes | [`test_edit_bug_ai_disclosure_is_near_and_describes_ai_assist`](../tests/frontend/ai-disclosure.test.cjs#L44); All variants |
| <a id="tc-254"></a>TC-254 | AC-022.2 | AI notice availability and dismissal update accessible description | Frontend JS / DOM substitutes | [`test_ai_notice_availability_and_dismissal_update_accessible_description`](../tests/frontend/ai-disclosure.test.cjs#L66); All variants |
| <a id="tc-255"></a>TC-255 | AC-022.2 | AI notice dismissal persists across new edit and reload | Frontend JS / DOM substitutes | [`test_ai_notice_dismissal_persists_across_new_edit_and_reload`](../tests/frontend/ai-disclosure.test.cjs#L87); All variants |
| <a id="tc-256"></a>TC-256 | AC-022.2 | AI notice dismissal preserves focus during AI loading or review | Frontend JS / DOM substitutes | [`test_ai_notice_dismissal_preserves_focus_during_ai_loading_or_review`](../tests/frontend/ai-disclosure.test.cjs#L104); All variants |
| <a id="tc-257"></a>TC-257 | AC-022.2 | AI notice restores preference on cached navigation and storage events | Frontend JS / DOM substitutes | [`test_ai_notice_restores_preference_on_cached_navigation_and_storage_events`](../tests/frontend/ai-disclosure.test.cjs#L118); All variants |
| <a id="tc-258"></a>TC-258 | AC-022.2 | AI notice storage failure still allows in page dismissal | Frontend JS / DOM substitutes | [`test_ai_notice_storage_failure_still_allows_in_page_dismissal`](../tests/frontend/ai-disclosure.test.cjs#L135); All variants |
| <a id="tc-259"></a>TC-259 | — | Privacy policy links cover all page footers | Frontend JS / DOM substitutes | [`test_privacy_policy_links_cover_all_page_footers`](../tests/frontend/ai-disclosure.test.cjs#L148); All variants |
| <a id="tc-260"></a>TC-260 | — | Registration subtitle links only privacy without extra paragraphs | Frontend JS / DOM substitutes | [`test_registration_subtitle_links_only_privacy_without_extra_paragraphs`](../tests/frontend/ai-disclosure.test.cjs#L164); All variants |
| <a id="tc-261"></a>TC-261 | — | About navigation preserves guest and authenticated controls | Frontend JS / DOM substitutes | [`test_about_navigation_preserves_guest_and_authenticated_controls`](../tests/frontend/ai-disclosure.test.cjs#L174); All variants |

## tests/frontend/bug-number-display.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-262"></a>TC-262 | AC-012.2 | Bug details and deletion use local resource number | Frontend JS / DOM substitutes | [`test_bug_details_and_deletion_use_local_resource_number`](../tests/frontend/bug-number-display.test.cjs#L28); All variants |
| <a id="tc-263"></a>TC-263 | AC-014.1 | Bug deletion requires confirmation and preserves cancelled report | Frontend JS / DOM substitutes | [`test_bug_deletion_requires_confirmation_and_preserves_cancelled_report`](../tests/frontend/bug-number-display.test.cjs#L41); All variants |
| <a id="tc-264"></a>TC-264 | AC-012.2 | Bug response validates project and local resource number | Frontend JS / DOM substitutes | [`test_bug_response_validates_project_and_local_resource_number`](../tests/frontend/bug-number-display.test.cjs#L64); All variants |
| <a id="tc-265"></a>TC-265 | — | Project navigation preserves full name as text and focus tooltip | Frontend JS / DOM substitutes | [`test_project_navigation_preserves_full_name_as_text_and_focus_tooltip`](../tests/frontend/bug-number-display.test.cjs#L79); All variants |
| <a id="tc-266"></a>TC-266 | AC-012.2 | Bug detail get and AI assist use local resource number | Frontend JS / DOM substitutes | [`test_bug_detail_get_and_ai_assist_use_local_resource_number`](../tests/frontend/bug-number-display.test.cjs#L93); All variants |
| <a id="tc-267"></a>TC-267 | AC-012.2 | Bug number query rejects invalid missing and legacy identity | Frontend JS / DOM substitutes | [`test_bug_number_query_rejects_invalid_missing_and_legacy_identity`](../tests/frontend/bug-number-display.test.cjs#L110); All variants |

## tests/frontend/bug-sort-persistence.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-268"></a>TC-268 | AC-012.6 | Page size invalid or unavailable reads fall back to ten | Frontend JS / DOM substitutes | [`test_page_size_invalid_or_unavailable_reads_fall_back_to_ten`](../tests/frontend/bug-sort-persistence.test.cjs#L101); All variants |
| <a id="tc-269"></a>TC-269 | AC-012.6 | Page size blocked writes preserve current pagination and sort | Frontend JS / DOM substitutes | [`test_page_size_blocked_writes_preserve_current_pagination_and_sort`](../tests/frontend/bug-sort-persistence.test.cjs#L122); All variants |
| <a id="tc-270"></a>TC-270 | AC-012.4 | Bug sort first visit defaults to last updated descending | Frontend JS / DOM substitutes | [`test_bug_sort_first_visit_defaults_to_last_updated_descending`](../tests/frontend/bug-sort-persistence.test.cjs#L145); All variants |
| <a id="tc-271"></a>TC-271 | AC-012.1 | Bug mobile labels and header relationships survive sorting | Frontend JS / DOM substitutes | [`test_bug_mobile_labels_and_header_relationships_survive_sorting`](../tests/frontend/bug-sort-persistence.test.cjs#L150); All variants |
| <a id="tc-272"></a>TC-272 | — | Bug list rejects invalid number response | Frontend JS / DOM substitutes | [`test_bug_list_rejects_invalid_number_response`](../tests/frontend/bug-sort-persistence.test.cjs#L169); All variants |
| <a id="tc-273"></a>TC-273 | AC-012.4 | Bug sort saves column and direction on header click | Frontend JS / DOM substitutes | [`test_bug_sort_saves_column_and_direction_on_header_click`](../tests/frontend/bug-sort-persistence.test.cjs#L178); All variants |
| <a id="tc-274"></a>TC-274 | AC-012.4 | Mobile sort controls reuse all columns direction and preferences | Frontend JS / DOM substitutes | [`test_mobile_sort_controls_reuse_all_columns_direction_and_preferences`](../tests/frontend/bug-sort-persistence.test.cjs#L187); All variants |
| <a id="tc-275"></a>TC-275 | AC-012.4, AC-012.5 | Mobile sort resets pagination and empty list hides toolbar | Frontend JS / DOM substitutes | [`test_mobile_sort_resets_pagination_and_empty_list_hides_toolbar`](../tests/frontend/bug-sort-persistence.test.cjs#L210); All variants |
| <a id="tc-276"></a>TC-276 | AC-012.4 | Bug sort reinitialization restores order indicators and links | Frontend JS / DOM substitutes | [`test_bug_sort_reinitialization_restores_order_indicators_and_links`](../tests/frontend/bug-sort-persistence.test.cjs#L222); All variants |
| <a id="tc-277"></a>TC-277 | AC-012.4 | Bug sort restores every supported column and direction | Frontend JS / DOM substitutes | [`test_bug_sort_restores_every_supported_column_and_direction`](../tests/frontend/bug-sort-persistence.test.cjs#L236); All variants |
| <a id="tc-278"></a>TC-278 | AC-012.4 | Bug sort preferences are isolated by project | Frontend JS / DOM substitutes | [`test_bug_sort_preferences_are_isolated_by_project`](../tests/frontend/bug-sort-persistence.test.cjs#L254); All variants |
| <a id="tc-279"></a>TC-279 | AC-012.4 | Bug sort preferences are isolated by user | Frontend JS / DOM substitutes | [`test_bug_sort_preferences_are_isolated_by_user`](../tests/frontend/bug-sort-persistence.test.cjs#L264); All variants |
| <a id="tc-280"></a>TC-280 | AC-012.4 | Bug sort invalid storage falls back to default | Frontend JS / DOM substitutes | [`test_bug_sort_invalid_storage_falls_back_to_default`](../tests/frontend/bug-sort-persistence.test.cjs#L276); All variants |
| <a id="tc-281"></a>TC-281 | AC-012.4 | Bug sort storage failures preserve working default and header sorting | Frontend JS / DOM substitutes | [`test_bug_sort_storage_failures_preserve_working_default_and_header_sorting`](../tests/frontend/bug-sort-persistence.test.cjs#L287); All variants |
| <a id="tc-282"></a>TC-282 | AC-012.4 | Bug sort back forward refresh preserves preference | Frontend JS / DOM substitutes | [`test_bug_sort_back_forward_refresh_preserves_preference`](../tests/frontend/bug-sort-persistence.test.cjs#L301); All variants |
| <a id="tc-283"></a>TC-283 | — | Project deletion clears only current users project sort preference | Frontend JS / DOM substitutes | [`test_project_deletion_clears_only_current_users_project_sort_preference`](../tests/frontend/bug-sort-persistence.test.cjs#L311); All variants |
| <a id="tc-284"></a>TC-284 | — | Failed project deletion preserves sort preference | Frontend JS / DOM substitutes | [`test_failed_project_deletion_preserves_sort_preference`](../tests/frontend/bug-sort-persistence.test.cjs#L323); All variants |
| <a id="tc-285"></a>TC-285 | — | Project deletion succeeds when sort storage is unavailable | Frontend JS / DOM substitutes | [`test_project_deletion_succeeds_when_sort_storage_is_unavailable`](../tests/frontend/bug-sort-persistence.test.cjs#L332); All variants |

## tests/frontend/fix-version-on-pass.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-286"></a>TC-286 | AC-017.5 | Passed fix version input visible and sends value | Frontend JS / DOM substitutes | [`test_passed_fix_version_input_visible_and_sends_value`](../tests/frontend/fix-version-on-pass.test.cjs#L64); All variants |
| <a id="tc-287"></a>TC-287 | AC-017.5 | Passed fix version respects eligibility | Frontend JS / DOM substitutes | [`test_passed_fix_version_respects_eligibility`](../tests/frontend/fix-version-on-pass.test.cjs#L107); All variants |
| <a id="tc-288"></a>TC-288 | AC-017.5 | Failed flow does not use fix version | Frontend JS / DOM substitutes | [`test_failed_flow_does_not_use_fix_version`](../tests/frontend/fix-version-on-pass.test.cjs#L118); All variants |

## tests/frontend/form-session.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-289"></a>TC-289 | AC-023.2 | New create after AI failure or no usable outcome | Frontend JS / DOM substitutes | [`test_new_create_after_ai_failure_or_no_usable_outcome`](../tests/frontend/form-session.test.cjs#L133); All variants |
| <a id="tc-290"></a>TC-290 | AC-023.2 | Edit save after AI failure or no usable outcome | Frontend JS / DOM substitutes | [`test_edit_save_after_ai_failure_or_no_usable_outcome`](../tests/frontend/form-session.test.cjs#L138); All variants |
| <a id="tc-291"></a>TC-291 | AC-020.8 | New create late success preserves reopened form and AI | Frontend JS / DOM substitutes | [`test_new_create_late_success_preserves_reopened_form_and_ai`](../tests/frontend/form-session.test.cjs#L209); All variants |
| <a id="tc-292"></a>TC-292 | AC-020.8 | Edit save late success preserves reopened form and AI | Frontend JS / DOM substitutes | [`test_edit_save_late_success_preserves_reopened_form_and_ai`](../tests/frontend/form-session.test.cjs#L214); All variants |
| <a id="tc-293"></a>TC-293 | AC-020.7 | New create current success closes form and discards AI | Frontend JS / DOM substitutes | [`test_new_create_current_success_closes_form_and_discards_ai`](../tests/frontend/form-session.test.cjs#L219); All variants |
| <a id="tc-294"></a>TC-294 | — | New create invalid number response preserves form | Frontend JS / DOM substitutes | [`test_new_create_invalid_number_response_preserves_form`](../tests/frontend/form-session.test.cjs#L224); All variants |
| <a id="tc-295"></a>TC-295 | AC-020.7 | Edit save current success closes form and discards AI | Frontend JS / DOM substitutes | [`test_edit_save_current_success_closes_form_and_discards_ai`](../tests/frontend/form-session.test.cjs#L239); All variants |
| <a id="tc-296"></a>TC-296 | AC-020.8 | New create late error does not overwrite reopened messages | Frontend JS / DOM substitutes | [`test_new_create_late_error_does_not_overwrite_reopened_messages`](../tests/frontend/form-session.test.cjs#L244); All variants |
| <a id="tc-297"></a>TC-297 | AC-020.8 | Edit save late error does not overwrite reopened messages | Frontend JS / DOM substitutes | [`test_edit_save_late_error_does_not_overwrite_reopened_messages`](../tests/frontend/form-session.test.cjs#L249); All variants |
| <a id="tc-298"></a>TC-298 | AC-020.8 | New create late JSON preserves newer pending submission | Frontend JS / DOM substitutes | [`test_new_create_late_json_preserves_newer_pending_submission`](../tests/frontend/form-session.test.cjs#L254); All variants |
| <a id="tc-299"></a>TC-299 | AC-020.8 | Edit save late JSON preserves newer pending submission | Frontend JS / DOM substitutes | [`test_edit_save_late_json_preserves_newer_pending_submission`](../tests/frontend/form-session.test.cjs#L259); All variants |
| <a id="tc-300"></a>TC-300 | AC-020.8 | Edit save late rejection preserves newer session | Frontend JS / DOM substitutes | [`test_edit_save_late_rejection_preserves_newer_session`](../tests/frontend/form-session.test.cjs#L265); All variants |
| <a id="tc-301"></a>TC-301 | AC-020.8 | New create stale list refresh failure preserves newer feedback | Frontend JS / DOM substitutes | [`test_new_create_stale_list_refresh_failure_preserves_newer_feedback`](../tests/frontend/form-session.test.cjs#L309); All variants |
| <a id="tc-302"></a>TC-302 | AC-020.7 | New create current list refresh failure shows error | Frontend JS / DOM substitutes | [`test_new_create_current_list_refresh_failure_shows_error`](../tests/frontend/form-session.test.cjs#L337); All variants |
| <a id="tc-303"></a>TC-303 | AC-020.8 | New create delayed list refresh response preserves newer session | Frontend JS / DOM substitutes | [`test_new_create_delayed_list_refresh_response_preserves_newer_session`](../tests/frontend/form-session.test.cjs#L403); All variants |
| <a id="tc-304"></a>TC-304 | AC-020.8 | New create delayed list refresh JSON preserves newer session | Frontend JS / DOM substitutes | [`test_new_create_delayed_list_refresh_json_preserves_newer_session`](../tests/frontend/form-session.test.cjs#L408); All variants |

## tests/frontend/lifecycle-action-disabled-state.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-305"></a>TC-305 | AC-017.1 | Bug action feedback follows controls | Frontend JS / DOM substitutes | [`test_bug_action_feedback_follows_controls`](../tests/frontend/lifecycle-action-disabled-state.test.cjs#L76); All variants |
| <a id="tc-306"></a>TC-306 | AC-017.2 | Move to open requires eligible selection and resets after transition | Frontend JS / DOM substitutes | [`test_move_to_open_requires_eligible_selection_and_resets_after_transition`](../tests/frontend/lifecycle-action-disabled-state.test.cjs#L86); All variants |
| <a id="tc-307"></a>TC-307 | AC-017.3 | Move to development requires developer selection and resets after transition | Frontend JS / DOM substitutes | [`test_move_to_development_requires_developer_selection_and_resets_after_transition`](../tests/frontend/lifecycle-action-disabled-state.test.cjs#L113); All variants |
| <a id="tc-308"></a>TC-308 | AC-017.4, AC-017.6 | Send to testing and close retain required selection behavior | Frontend JS / DOM substitutes | [`test_send_to_testing_and_close_retain_required_selection_behavior`](../tests/frontend/lifecycle-action-disabled-state.test.cjs#L143); All variants |

## tests/frontend/project-name-validation.test.cjs

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-309"></a>TC-309 | AC-005.2 | Project creation validation feedback tracks input | Frontend JS / DOM substitutes | [`test_project_creation_validation_feedback_tracks_input`](../tests/frontend/project-name-validation.test.cjs#L80); All variants |
| <a id="tc-310"></a>TC-310 | AC-005.2 | Project creation cancel clears form feedback | Frontend JS / DOM substitutes | [`test_project_creation_cancel_clears_form_feedback`](../tests/frontend/project-name-validation.test.cjs#L95); All variants |
| <a id="tc-311"></a>TC-311 | AC-005.2 | Project creation open clears previous form feedback | Frontend JS / DOM substitutes | [`test_project_creation_open_clears_previous_form_feedback`](../tests/frontend/project-name-validation.test.cjs#L106); All variants |
| <a id="tc-312"></a>TC-312 | AC-005.2 | Project creation preserves unrelated feedback | Frontend JS / DOM substitutes | [`test_project_creation_preserves_unrelated_feedback`](../tests/frontend/project-name-validation.test.cjs#L120); All variants |
| <a id="tc-313"></a>TC-313 | AC-005.2 | Project creation server validation feedback clears on correction | Frontend JS / DOM substitutes | [`test_project_creation_server_validation_feedback_clears_on_correction`](../tests/frontend/project-name-validation.test.cjs#L151); All variants |
| <a id="tc-314"></a>TC-314 | AC-007.3 | Project edit validation feedback tracks input | Frontend JS / DOM substitutes | [`test_project_edit_validation_feedback_tracks_input`](../tests/frontend/project-name-validation.test.cjs#L80); All variants |
| <a id="tc-315"></a>TC-315 | AC-007.3 | Project edit cancel clears form feedback | Frontend JS / DOM substitutes | [`test_project_edit_cancel_clears_form_feedback`](../tests/frontend/project-name-validation.test.cjs#L95); All variants |
| <a id="tc-316"></a>TC-316 | AC-007.3 | Project edit open clears previous form feedback | Frontend JS / DOM substitutes | [`test_project_edit_open_clears_previous_form_feedback`](../tests/frontend/project-name-validation.test.cjs#L106); All variants |
| <a id="tc-317"></a>TC-317 | AC-007.3 | Project edit preserves unrelated feedback | Frontend JS / DOM substitutes | [`test_project_edit_preserves_unrelated_feedback`](../tests/frontend/project-name-validation.test.cjs#L120); All variants |
| <a id="tc-318"></a>TC-318 | AC-007.3 | Project edit server validation feedback clears on correction | Frontend JS / DOM substitutes | [`test_project_edit_server_validation_feedback_clears_on_correction`](../tests/frontend/project-name-validation.test.cjs#L151); All variants |
| <a id="tc-319"></a>TC-319 | AC-007.3 | Project edit success clears prior validation feedback | Frontend JS / DOM substitutes | [`test_project_edit_success_clears_prior_validation_feedback`](../tests/frontend/project-name-validation.test.cjs#L163); All variants |
| <a id="tc-320"></a>TC-320 | AC-005.2, AC-007.3 | Project name input preserves other form feedback | Frontend JS / DOM substitutes | [`test_project_name_input_preserves_other_form_feedback`](../tests/frontend/project-name-validation.test.cjs#L175); All variants |
| <a id="tc-321"></a>TC-321 | AC-005.2 | Project creation blocks blank name submission | Frontend JS / DOM substitutes | [`test_project_creation_blocks_blank_name_submission`](../tests/frontend/project-name-validation.test.cjs#L189); All variants |
| <a id="tc-322"></a>TC-322 | AC-005.1 | Project creation submits valid name unchanged | Frontend JS / DOM substitutes | [`test_project_creation_submits_valid_name_unchanged`](../tests/frontend/project-name-validation.test.cjs#L199); All variants |
| <a id="tc-323"></a>TC-323 | AC-007.3 | Project edit blocks blank name submission | Frontend JS / DOM substitutes | [`test_project_edit_blocks_blank_name_submission`](../tests/frontend/project-name-validation.test.cjs#L189); All variants |
| <a id="tc-324"></a>TC-324 | AC-007.1 | Project edit submits valid name unchanged | Frontend JS / DOM substitutes | [`test_project_edit_submits_valid_name_unchanged`](../tests/frontend/project-name-validation.test.cjs#L199); All variants |

## tests/e2e/test_ai_triage.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-325"></a>TC-325 | AC-018.2, AC-018.3, AC-020.1, AC-020.2, AC-020.3, AC-020.4, AC-020.7 | New AI review applies only selected suggestions before create | Playwright / Chromium (mocked AI) | [`test_new_ai_review_applies_only_selected_suggestions_before_create`](../tests/e2e/test_ai_triage.py#L8); All variants |
| <a id="tc-326"></a>TC-326 | AC-020.5, AC-020.7, AC-020.8 | Edit AI cancel discards changes then save persists review | Playwright / Chromium (mocked AI) | [`test_edit_ai_cancel_discards_changes_then_save_persists_review`](../tests/e2e/test_ai_triage.py#L59); All variants |
| <a id="tc-327"></a>TC-327 | AC-018.4, AC-023.1, AC-023.2 | Recover manually and retry after AI service failure | Playwright / Chromium (mocked AI) | [`test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry`](../tests/e2e/test_ai_triage.py#L104); outcome=failure |
| <a id="tc-328"></a>TC-328 | AC-018.4, AC-019.4, AC-023.2 | Recover manually and retry after valid empty AI output | Playwright / Chromium (mocked AI) | [`test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry`](../tests/e2e/test_ai_triage.py#L104); outcome=empty |

## tests/e2e/test_auth.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-329"></a>TC-329 | AC-001.1, AC-002.1, AC-003.1, AC-003.2, AC-004.1, AC-004.2 | Registration login logout | Playwright / Chromium | [`test_registration_login_logout`](../tests/e2e/test_auth.py#L9); All variants |
| <a id="tc-330"></a>TC-330 | AC-002.2 | Invalid login feedback allows correction | Playwright / Chromium | [`test_invalid_login_feedback_allows_correction`](../tests/e2e/test_auth.py#L38); All variants |

## tests/e2e/test_authorization.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-331"></a>TC-331 | AC-006.4, AC-009.1, AC-009.2, AC-009.5 | Owner manages membership and removed user loses access | Playwright / Chromium | [`test_owner_manages_membership_and_removed_user_loses_access`](../tests/e2e/test_authorization.py#L7); All variants |
| <a id="tc-332"></a>TC-332 | AC-012.3, AC-014.2, AC-022.1 | Developer cannot delete or request AI and outsider cannot open bug | Playwright / Chromium (mocked AI) | [`test_developer_cannot_delete_or_request_ai_and_outsider_cannot_open_bug`](../tests/e2e/test_authorization.py#L49); All variants |

## tests/e2e/test_bug_list.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-333"></a>TC-333 | AC-012.2, AC-012.4, AC-012.5, AC-012.6 | Sort pagination and page size survive navigation and reload | Playwright / Chromium | [`test_sort_pagination_and_page_size_survive_navigation_and_reload`](../tests/e2e/test_bug_list.py#L9); All variants |
| <a id="tc-334"></a>TC-334 | AC-012.5, AC-012.6 | Page size preferences persist and are isolated by user | Playwright / Chromium | [`test_page_size_preferences_persist_and_are_isolated_by_user`](../tests/e2e/test_bug_list.py#L54); All variants |

## tests/e2e/test_bugs.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-335"></a>TC-335 | AC-011.1, AC-013.1, AC-014.1, AC-015.1 | Bug create edit assign and confirmed delete | Playwright / Chromium | [`test_bug_create_edit_assign_and_confirmed_delete`](../tests/e2e/test_bugs.py#L7); All variants |
| <a id="tc-336"></a>TC-336 | AC-017.2, AC-017.3, AC-017.4, AC-017.5, AC-017.7 | Bug handoff pass and reopen | Playwright / Chromium | [`test_bug_handoff_pass_and_reopen`](../tests/e2e/test_bugs.py#L53); All variants |
| <a id="tc-337"></a>TC-337 | AC-017.5 | Failed testing returns to selected developer | Playwright / Chromium | [`test_failed_testing_returns_to_selected_developer`](../tests/e2e/test_bugs.py#L98); All variants |
| <a id="tc-338"></a>TC-338 | AC-011.4, AC-013.2, AC-017.5, AC-017.6 | Fix version eligibility persistence and form reset | Playwright / Chromium | [`test_fix_version_eligibility_persistence_and_form_reset`](../tests/e2e/test_bugs.py#L126); All variants |

## tests/e2e/test_projects.py

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-339"></a>TC-339 | AC-005.1, AC-005.2, AC-007.1, AC-008.1 | Project create rename and confirmed delete | Playwright / Chromium | [`test_project_create_rename_and_confirmed_delete`](../tests/e2e/test_projects.py#L7); All variants |

## tests/frontend/native-input.test.html

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-340"></a>TC-340 | AC-020.2, AC-020.4 | AI native input browser review and apply consistency | Browser fixture / manually launched assertions | [`test_ai_native_input_browser_review_and_apply_consistency`](../tests/frontend/native-input.test.html#L12); All variants |

## tests/frontend/ui-style.test.html

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-341"></a>TC-341 | AC-012.2 | Bug details dividers preserve metadata rows | Browser fixture / manually launched assertions | [`test_bug_details_dividers_preserve_metadata_rows`](../tests/frontend/ui-style.test.html#L36); All variants |
| <a id="tc-342"></a>TC-342 | — | Destructive buttons preserve focus and disabled states | Browser fixture / manually launched assertions | [`test_destructive_buttons_preserve_focus_and_disabled_states`](../tests/frontend/ui-style.test.html#L79); All variants |

## Structured manual verification

| TC ID | AC mapping | Scenario | Test type | Implementation and parameter selector |
| --- | --- | --- | --- | --- |
| <a id="tc-343"></a>TC-343 | AC-012.1, AC-012.2 | Bug list/details presentation | Structured manual / user-reported | [M01](test-execution.md#m01); Manually executable checks; see recorded limitations |
| <a id="tc-344"></a>TC-344 | AC-012.2 | Native browser interactions | Structured manual / user-reported | [M02](test-execution.md#m02); Manually executable checks; see recorded limitations |
| <a id="tc-345"></a>TC-345 | AC-012.5 | Pagination and responsive layout | Structured manual / user-reported | [M03](test-execution.md#m03); Manually executable checks; see recorded limitations |
| <a id="tc-346"></a>TC-346 | AC-017.1 | Lifecycle scrolling | Structured manual / user-reported | [M04](test-execution.md#m04); Manually executable checks; see recorded limitations |
| <a id="tc-347"></a>TC-347 | AC-020.8 | Pending AI suggestion lifetime | Structured manual / user-reported | [M05](test-execution.md#m05); Manually executable checks; see recorded limitations |

## BDD specification appendix

These **17 scenarios are specifications only**, with no executable step bindings or
execution TC IDs. Related TCs below are links to existing implementations, not claims
that those implementations execute the feature files. Password examples map to the
current AC-001.4; password security is AC-001.5 and has no BDD scenario.

| Specification reference | Current AC mapping | Related maintained TC |
| --- | --- | --- |
| [Successfully register an account](../tests/e2e/bdd/features/authentication.feature#L6) | AC-001.1 | [TC-217](test-cases.md#tc-217) |
| [Register with an already registered email address](../tests/e2e/bdd/features/authentication.feature#L12) | AC-001.2 | [TC-218](test-cases.md#tc-218) |
| [Register with an invalid email address](../tests/e2e/bdd/features/authentication.feature#L20) | AC-001.3 | [TC-219](test-cases.md#tc-219) |
| [Register with a password that is too short](../tests/e2e/bdd/features/authentication.feature#L27) | AC-001.4 | [TC-220](test-cases.md#tc-220) |
| [Register with a password without an uppercase letter](../tests/e2e/bdd/features/authentication.feature#L34) | AC-001.4 | [TC-221](test-cases.md#tc-221) |
| [Register with a password without a lowercase letter](../tests/e2e/bdd/features/authentication.feature#L41) | AC-001.4 | [TC-222](test-cases.md#tc-222) |
| [Register with a password without a number](../tests/e2e/bdd/features/authentication.feature#L49) | AC-001.4 | [TC-223](test-cases.md#tc-223) |
| [Successfully log in](../tests/e2e/bdd/features/authentication.feature#L61) | AC-002.1 | [TC-177](test-cases.md#tc-177) |
| [Log in with invalid credentials](../tests/e2e/bdd/features/authentication.feature#L68) | AC-002.2 | [TC-178](test-cases.md#tc-178) |
| [Authenticated user accesses a protected area](../tests/e2e/bdd/features/authentication.feature#L77) | AC-003.1 | [TC-180](test-cases.md#tc-180) |
| [Unauthenticated user accesses a protected area](../tests/e2e/bdd/features/authentication.feature#L83) | AC-003.2 | [TC-329](test-cases.md#tc-329) |
| [User accesses a protected area with invalid authentication](../tests/e2e/bdd/features/authentication.feature#L90) | AC-003.3 | [TC-182](test-cases.md#tc-182) |
| [Successfully log out](../tests/e2e/bdd/features/authentication.feature#L99) | AC-004.1 | [TC-329](test-cases.md#tc-329) |
| [Attempt to access a protected area after logging out](../tests/e2e/bdd/features/authentication.feature#L106) | AC-004.2 | [TC-329](test-cases.md#tc-329) |
| [Successfully create a project](../tests/e2e/bdd/features/project_creation.feature#L6) | AC-005.1 | [TC-184](test-cases.md#tc-184) |
| [Create a project with an empty name](../tests/e2e/bdd/features/project_creation.feature#L13) | AC-005.2 | [TC-185](test-cases.md#tc-185) |
| [Unauthenticated user attempts to create a project](../tests/e2e/bdd/features/project_creation.feature#L20) | AC-005.3 | [TC-189](test-cases.md#tc-189) |
