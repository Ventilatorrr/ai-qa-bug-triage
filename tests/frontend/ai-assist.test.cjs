const test = require("node:test");
const assert = require("node:assert/strict");
const {fixture, success, deferred} = require("./helpers/ai-fixture.cjs");

function fillUnsavedForm(f, prefix) {
    const values = {
        title: "Keep unsaved title", "affected-version": "0.4", environment: "Keep environment",
        description: "Keep\nunsaved description", steps: "1. Keep\n2. Retry", expected: "Keep expected",
        actual: "Keep actual", severity: "Major", priority: "High", assignee: "7", "fix-version": "0.5"
    };
    for (const [suffix, value] of Object.entries(values)) f.inputs[`#${prefix}${suffix}`].value = value;
    return Object.fromEntries(Object.entries(f.inputs).map(([id, input]) => [id, input.value]));
}

function assertFormValues(f, expected) {
    assert.deepEqual(Object.fromEntries(Object.entries(f.inputs).map(([id, input]) => [id, input.value])), expected);
}

async function assertRetryUsesEditedValues(f, prefix) {
    f.inputs[`#${prefix}title`].value = "Manually revised title";
    f.inputs[`#${prefix}environment`].value = "Manually revised environment";
    f.inputs[`#${prefix}description`].value = "Manually revised\ncontent";
    const latest = JSON.parse(JSON.stringify(f.runtime.collectAiAssistContext(f.form, prefix)));
    await f.submit(async () => success({title: "Fresh suggestion"}));
    assert.equal(f.requests.length, 2);
    const sent = JSON.parse(f.requests[1].options.body);
    assert.deepEqual(sent, latest);
    assert.equal(sent.title, "Manually revised title");
    assert.equal(sent.environment, "Manually revised environment");
    assert.equal(sent.description, "Manually revised\ncontent");
    assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "Fresh suggestion");
    assert.equal(f.card("Title").parentElement, f.inputs[`#${prefix}title`].closest(".bug-field-row"));
    assert.equal(f.inputs[`#${prefix}title`].value, "Manually revised title");
    assert.equal(f.button.disabled, true);
    assert.match(f.message.textContent, /ready for review/);
}

test("test_ai_native_text_input_mismatches_are_excluded_before_use_or_use_all", async function test_ai_native_text_input_mismatches_are_excluded_before_use_or_use_all() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        for (const action of ["Use", "Use All"]) {
            for (const newline of ["\n", "\r", "\r\n"]) {
                const f = fixture(prefix);
                const input = f.inputs[`#${prefix}environment`];
                input.value = `Windows 11${newline}Chrome 152`;
                assert.equal(input.value, "Windows 11Chrome 152", "fixture models native text input sanitization");
                input.value = "Keep environment";
                await f.submit(async () => success({
                    title: `Bad${newline}title`, affected_version: `1${newline}2`,
                    environment: `Windows 11${newline}Chrome 152`, description: "Usable\ntext"
                }));
                assert.deepEqual(f.form.all("h4").map(node => node.textContent), ["AI Suggestion"]);
                assert.equal(f.card("Description").all("h4")[0].attributes["aria-label"], "AI suggestion: Description");
                const reviewed = f.card("Description").querySelector(".ai-suggestion-value").textContent;
                f.action(action, action === "Use" ? "Description" : undefined);
                assert.equal(f.inputs[`#${prefix}description`].value, reviewed);
                assert.equal(input.value, "Keep environment");
                assert.equal(f.inputs[`#${prefix}title`].value, "");
                assert.equal(f.inputs[`#${prefix}affected-version`].value, "");
                assert.equal(f.button.disabled, false);
            }
        }
    }
});

test("test_ai_all_native_input_mismatches_allow_manual_work_and_retry", async function test_ai_all_native_input_mismatches_allow_manual_work_and_retry() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        await f.submit(async () => success({environment: "Windows\nChrome"}));
        assert.equal(f.area.hidden, true);
        assert.match(f.message.textContent, /No usable AI suggestions/);
        assert.equal(f.button.disabled, false);
        await f.submit(async () => success({environment: "Windows / Chrome"}));
        const reviewed = f.card("Environment").querySelector(".ai-suggestion-value").textContent;
        f.action("Use", "Environment");
        assert.equal(f.inputs[`#${prefix}environment`].value, reviewed);
    }
});

test("test_collect_ai_context_preserves_blank_and_unsaved_values", function test_collect_ai_context_preserves_blank_and_unsaved_values() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const {runtime, inputs, form} = fixture(prefix);
        const snapshot = () => JSON.parse(JSON.stringify(runtime.collectAiAssistContext(form, prefix)));
        assert.deepEqual(snapshot(), {
            title: "", affected_version: "", environment: "", description: "",
            steps_to_reproduce: "", expected_result: "", actual_result: "",
            severity: "", priority: "", assignee_id: null
        });
        inputs[`#${prefix}title`].value = "  Unsaved title  ";
        inputs[`#${prefix}affected-version`].value = "0.2";
        inputs[`#${prefix}environment`].value = " Windows ";
        inputs[`#${prefix}description`].value = "Unsaved\ntext";
        inputs[`#${prefix}steps`].value = "1. Click";
        inputs[`#${prefix}expected`].value = "Success";
        inputs[`#${prefix}actual`].value = "Failure";
        inputs[`#${prefix}severity`].value = "Major";
        inputs[`#${prefix}priority`].value = "High";
        inputs[`#${prefix}assignee`].value = "7";
        inputs[`#${prefix}fix-version`].value = "Excluded";
        assert.deepEqual(snapshot(), {
            title: "  Unsaved title  ", affected_version: "0.2", environment: " Windows ",
            description: "Unsaved\ntext", steps_to_reproduce: "1. Click",
            expected_result: "Success", actual_result: "Failure", severity: "Major",
            priority: "High", assignee_id: 7
        });
        inputs[`#${prefix}description`].value = "";
        assert.equal(snapshot().description, "");
    }
});

test("test_submit_ai_context_limits_requests_and_reports_unavailable", async function test_submit_ai_context_limits_requests_and_reports_unavailable() {
    const {runtime, inputs, form, button, message} = fixture("edit-bug-");
    inputs["#edit-bug-title"].value = "Unsaved edit";
    const requests = [];
    let finish;
    const send = (url, options) => {
        requests.push({url, options});
        return new Promise(resolve => { finish = resolve; });
    };
    const submit = () => runtime.submitAiAssist(form, "edit-bug-", "/projects/1/bugs/2/ai-assist", button, message, send);
    assert.equal(requests.length, 0);
    const pending = submit();
    await submit();
    assert.equal(requests.length, 1);
    assert.equal(button.disabled, true);
    assert.equal(message.textContent, "Requesting AI assistance...");
    assert.equal(requests[0].options.method, "POST");
    assert.equal(JSON.parse(requests[0].options.body).title, "Unsaved edit");
    finish({ok: false, json: async () => ({detail: "AI assistance is not configured yet."})});
    await pending;
    assert.equal(button.disabled, false);
    assert.equal(message.textContent, "AI assistance is not configured yet.");
    const retry = submit();
    assert.equal(requests.length, 2);
    finish({ok: false, json: async () => ({detail: "AI assistance is not configured yet."})});
    await retry;
});

test("test_submit_ai_context_recovers_from_network_failure", async function test_submit_ai_context_recovers_from_network_failure() {
    const {runtime, form, button, message} = fixture("bug-");
    await runtime.submitAiAssist(form, "bug-", "/projects/1/ai-assist", button, message, async () => {
        throw new Error("Offline");
    });
    assert.equal(button.disabled, false);
    assert.equal(message.textContent, "Unable to request AI assistance. Please try again.");
});

test("test_ai_suggestions_review_separates_values_and_follows_form_order", async function test_ai_suggestions_review_separates_values_and_follows_form_order() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        f.inputs[`#${prefix}title`].value = "Original title";
        await f.submit(async () => success({assignee_id: 7, actual_result: "Failure", severity: "Major", title: "<script>bad()</script>"}));
        assert.equal(f.inputs[`#${prefix}title`].value, "Original title");
        assert.equal(f.inputs[`#${prefix}severity`].value, "");
        assert.equal(f.area.hidden, false);
        assert.equal(f.footer.hidden, false);
        assert.equal(f.area.all("h3")[0].textContent, "AI Suggestions");
        assert.deepEqual(f.form.all("h4").map(node => node.textContent), Array(4).fill("AI Suggestion"));
        assert.deepEqual(f.form.all("h4").map(node => node.attributes["aria-label"]), ["AI suggestion: Title", "AI suggestion: Actual Result", "AI suggestion: Severity", "AI suggestion: Assignee"]);
        assert.equal(f.form.classList.contains("has-ai-suggestions"), true);
        assert.equal(f.form.children[0], f.area, "review guidance precedes the field rows");
        assert.equal(f.area.querySelector(".ai-suggestions-toolbar").all("h3")[0].id, f.area.attributes["aria-labelledby"]);
        assert.equal(f.area.all("button").length, 0, "bulk controls are outside the top guidance");
        assert.deepEqual(f.footer.all("button").map(node => node.textContent), ["Use All", "Dismiss All"]);
        const rows = f.form.querySelectorAll(".bug-field-row");
        assert.ok(rows.every(row => f.form.children.indexOf(row) < f.form.children.indexOf(f.footer)), "bulk controls follow all field rows");
        assert.ok(f.form.children.indexOf(f.footer) < f.form.children.indexOf(f.button), "bulk controls precede the normal form actions");
        assert.equal(f.area.all("article").length, 0, "suggestions live beside fields");
        for (const suffix of ["affected-version", "environment", "description", "steps", "expected", "priority", "fix-version"]) {
            const input = f.inputs[`#${prefix}${suffix}`];
            assert.deepEqual(input.closest(".bug-field-row").children, [input.parentElement], "fields without suggestions have only their full-width field block");
        }
        for (const [label, suffix] of [["Title", "title"], ["Actual Result", "actual"], ["Severity", "severity"], ["Assignee", "assignee"]]) {
            const card = f.card(label), row = f.inputs[`#${prefix}${suffix}`].closest(".bug-field-row");
            assert.equal(card.parentElement, row);
            assert.deepEqual(row.children, [f.inputs[`#${prefix}${suffix}`].parentElement, card], "field precedes its suggestion in reading and stacking order");
            assert.equal(card.attributes["aria-labelledby"], card.all("h4")[0].id);
            assert.equal(card.all("h4")[0].attributes["aria-label"], `AI suggestion: ${label}`);
            assert.deepEqual(card.children, [card.all("h4")[0], card.querySelector(".ai-suggestion-value"), card.querySelector(".ai-suggestion-actions")], "all cards show heading, value, then the action row");
            assert.equal(card.all("p").length, 1, "only the suggested value is displayed");
            assert.equal(card.all("dl").length, 0, "there is no duplicate current-value comparison");
            assert.equal(card.all("button")[1].attributes["aria-label"], `Dismiss ${label} suggestion`);
        }
        assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "<script>bad()</script>");
        assert.equal(f.card("Assignee").querySelector(".ai-suggestion-value").textContent, "qa@example.com (QA Analyst)");
        assert.deepEqual(f.card("Title").all("button").map(node => node.textContent), ["Use", "Dismiss"]);
        assert.equal(f.card("Title").all("button")[0].attributes["aria-label"], "Use Title suggestion");
        const reviewButtons = [...f.footer.all("button"), ...f.form.all("article").flatMap(card => card.all("button"))];
        assert.ok(reviewButtons.every(button => button.type === "button" && button.classList.contains("ai-review-button")));
        assert.ok(reviewButtons.every(button => button.classList.contains(button.textContent.startsWith("Use") ? "ai-use-button" : "ai-dismiss-button") && !button.classList.contains("secondary-action-button")));
        assert.equal(f.form.all("script").length, 0);
        assert.equal(f.button.disabled, true);
        assert.equal(f.requests.length, 1);
    }
});

test("test_ai_review_tracks_current_values_after_manual_edits", async function test_ai_review_tracks_current_values_after_manual_edits() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        await f.submit();
        const input = f.inputs[`#${prefix}title`], card = f.card("Title");
        input.value = "Edited while pending";
        input.dispatchEvent({type: "input", bubbles: true});
        input.dispatchEvent({type: "change", bubbles: true});
        assert.equal(input.value, "Edited while pending");
        assert.equal(input.disabled, false);
        assert.equal(card.parentElement.children[0], input.parentElement);
        assert.equal(card.querySelector(".ai-suggestion-value").textContent, "Suggested title");
        assert.equal(card.all("p").length, 1);
        assert.equal(f.button.disabled, true);
    }
});

test("test_ai_use_replaces_value_removes_pending_and_remains_editable", async function test_ai_use_replaces_value_removes_pending_and_remains_editable() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        f.inputs[`#${prefix}title`].value = "Original";
        await f.submit(async () => success({title: "Suggested title", severity: "Major"}));
        f.action("Use", "Title");
        assert.equal(f.inputs[`#${prefix}title`].value, "Suggested title");
        assert.equal(f.card("Title"), undefined);
        const titleInput = f.inputs[`#${prefix}title`];
        assert.deepEqual(titleInput.closest(".bug-field-row").children, [titleInput.parentElement], "using a suggestion restores that row while other suggestions remain");
        assert.equal(f.footer.hidden, false);
        assert.equal(f.footer.all("button")[0].focused, true);
        assert.ok(f.card("Severity"));
        f.inputs[`#${prefix}title`].value = "My revision";
        assert.equal(f.inputs[`#${prefix}title`].disabled, false);
        f.action("Use", "Severity");
        assert.equal(f.inputs[`#${prefix}title`].value, "My revision");
        assert.equal(f.area.hidden, true);
        assert.equal(f.footer.hidden, true);
        assert.equal(f.footer.children.length, 0);
        assert.equal(f.form.classList.contains("has-ai-suggestions"), false);
        assert.equal(f.button.disabled, false);
        assert.equal(f.requests.length, 1);
    }
});

test("test_ai_dismiss_preserves_form_and_excludes_field_from_use_all", async function test_ai_dismiss_preserves_form_and_excludes_field_from_use_all() {
    const f = fixture("bug-");
    f.inputs["#bug-title"].value = "Keep this";
    await f.submit(async () => success({title: "Discard this", severity: "Major"}));
    f.action("Dismiss", "Title");
    assert.equal(f.inputs["#bug-title"].value, "Keep this");
    assert.equal(f.card("Title"), undefined);
    assert.deepEqual(f.inputs["#bug-title"].closest(".bug-field-row").children, [f.inputs["#bug-title"].parentElement], "dismissing a suggestion restores that row while other suggestions remain");
    assert.equal(f.footer.hidden, false);
    f.action("Use All");
    assert.equal(f.inputs["#bug-title"].value, "Keep this");
    assert.equal(f.inputs["#bug-severity"].value, "Major");
    assert.equal(f.area.hidden, true);
    assert.equal(f.footer.hidden, true);
});

test("test_ai_use_all_applies_only_pending_values_without_reapplying_used_fields", async function test_ai_use_all_applies_only_pending_values_without_reapplying_used_fields() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        f.inputs[`#${prefix}severity`].value = "Minor";
        f.inputs[`#${prefix}environment`].value = "Keep environment";
        await f.submit(async () => success({title: "AI title", environment: "Dismissed", severity: "Major", assignee_id: 7}));
        f.action("Use", "Title");
        f.inputs[`#${prefix}title`].value = "Revised after Use";
        f.action("Dismiss", "Environment");
        f.action("Use All");
        assert.equal(f.inputs[`#${prefix}title`].value, "Revised after Use");
        assert.equal(f.inputs[`#${prefix}environment`].value, "Keep environment");
        assert.equal(f.inputs[`#${prefix}severity`].value, "Major");
        assert.equal(f.inputs[`#${prefix}assignee`].value, "7");
        f.inputs[`#${prefix}severity`].value = "Moderate";
        assert.equal(f.inputs[`#${prefix}severity`].disabled, false);
        assert.equal(f.form.all("article").length, 0);
        assert.equal(f.form.classList.contains("has-ai-suggestions"), false);
        assert.equal(f.button.disabled, false);
        assert.equal(f.requests.length, 1);
    }
});

test("test_ai_dismiss_all_preserves_used_and_other_form_values", async function test_ai_dismiss_all_preserves_used_and_other_form_values() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        f.inputs[`#${prefix}severity`].value = "Minor";
        await f.submit(async () => success({title: "AI title", severity: "Major"}));
        f.action("Use", "Title");
        f.action("Dismiss All");
        assert.equal(f.inputs[`#${prefix}title`].value, "AI title");
        assert.equal(f.inputs[`#${prefix}severity`].value, "Minor");
        assert.equal(f.area.hidden, true);
        assert.equal(f.button.disabled, false);
        assert.equal(f.requests.length, 1);
    }
});

test("test_ai_repeat_request_waits_for_resolution_and_uses_latest_form", async function test_ai_repeat_request_waits_for_resolution_and_uses_latest_form() {
    const f = fixture("edit-bug-");
    await f.submit(async () => success({title: "Same suggestion", severity: "Major"}));
    await f.submit();
    assert.equal(f.requests.length, 1);
    f.action("Dismiss", "Title");
    await f.submit();
    assert.equal(f.requests.length, 1);
    f.action("Use", "Severity");
    f.inputs["#edit-bug-title"].value = "Latest unsaved title";
    await f.submit(async () => success({title: "Same suggestion", severity: "Minor"}));
    assert.equal(f.requests.length, 2);
    assert.equal(JSON.parse(f.requests[1].options.body).title, "Latest unsaved title");
    assert.equal(JSON.parse(f.requests[1].options.body).severity, "Major");
    assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "Same suggestion");
    assert.ok(f.card("Severity"));
});

test("test_ai_no_usable_suggestions_is_success_and_allows_manual_work_and_retry", async function test_ai_no_usable_suggestions_is_success_and_allows_manual_work_and_retry() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        const original = fillUnsavedForm(f, prefix);
        let submits = 0;
        f.form.addEventListener("submit", () => { submits++; });
        await f.submit(async () => ({ok: true, json: async () => ({outcome: "no_usable_suggestions", suggestions: {}})}));
        assert.match(f.message.textContent, /No usable AI suggestions/);
        assert.equal(f.area.hidden, true);
        assert.equal(f.message.classList.contains("message-error"), false);
        assert.equal(f.button.disabled, false);
        assertFormValues(f, original);
        assert.equal(f.requests.length, 1);
        assert.equal(submits, 0);
        await assertRetryUsesEditedValues(f, prefix);
        assert.equal(submits, 0);
    }
});

test("test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry", async function test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry() {
    const failures = [
        async () => { throw new Error("Offline"); },
        async () => ({ok: false, status: 503, json: async () => ({detail: "AI assistance is not configured yet."})}),
        async () => ({ok: false, status: 502, json: async () => ({detail: "AI assistance could not generate suggestions. Please try again."})}),
        async () => ({ok: false, json: async () => ({detail: "Safe provider failure"})}),
        async () => ({ok: true, json: async () => { throw new Error("Bad JSON"); }}),
        async () => ({ok: true, json: async () => ({outcome: "unexpected", suggestions: {}})}),
        async () => success({}),
        async () => success({title: " "}),
        async () => success({fix_version: "0.3"}),
        async () => success({severity: "Invalid"}),
        async () => success({assignee_id: "7"}),
        async () => ({ok: true, json: async () => ({outcome: "no_usable_suggestions", suggestions: {title: "Inconsistent"}})})
    ];
    for (const prefix of ["bug-", "edit-bug-"]) {
        for (const send of failures) {
            const f = fixture(prefix);
            const original = fillUnsavedForm(f, prefix);
            let submits = 0;
            f.form.addEventListener("submit", () => { submits++; });
            const waiting = deferred();
            const pending = f.submit(() => waiting.promise);
            assert.equal(f.button.disabled, true);
            assert.equal(f.message.textContent, "Requesting AI assistance...");
            // Manual edits made while waiting must also survive completion.
            f.inputs[`#${prefix}environment`].value = "Edited while waiting";
            original[`#${prefix}environment`] = "Edited while waiting";
            waiting.resolve(send());
            await pending;
            assert.match(f.message.textContent, /Unable|Safe provider failure|not configured|could not generate/);
            assert.equal(f.message.classList.contains("message-error"), true);
            assertFormValues(f, original);
            assert.equal(f.area.hidden, true);
            assert.equal(f.button.disabled, false);
            assert.equal(f.requests.length, 1);
            assert.equal(submits, 0);
            await assertRetryUsesEditedValues(f, prefix);
            assert.equal(f.message.classList.contains("message-error"), false);
            assert.equal(submits, 0);
        }
    }
});

test("test_ai_cancel_discards_pending_and_detached_actions_cannot_apply", async function test_ai_cancel_discards_pending_and_detached_actions_cannot_apply() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        await f.submit();
        const abandonedUse = f.card("Title").all("button")[0];
        f.runtime.endAiAssistSession(f.form);
        assert.equal(f.area.hidden, true);
        assert.equal(f.footer.hidden, true);
        assert.equal(f.area.children.length, 0);
        assert.equal(f.footer.children.length, 0);
        assert.equal(f.form.all("article").length, 0, "session cleanup also removes cards beside the fields");
        assert.equal(f.form.classList.contains("has-ai-suggestions"), false);
        assert.equal(f.message.textContent, "");
        f.begin();
        abandonedUse.click();
        assert.equal(f.inputs[`#${prefix}title`].value, "");
        await f.submit();
        assert.ok(f.card("Title"));
        assert.equal(f.form.all("article").length, 1, "reopening creates no duplicate inline cards");
    }
});

test("test_ai_late_success_or_error_cannot_populate_reopened_session", async function test_ai_late_success_or_error_cannot_populate_reopened_session() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        for (const outcome of ["success", "error", "rejection"]) {
            const f = fixture(prefix);
            const old = deferred();
            const abandoned = f.submit(() => old.promise);
            f.runtime.endAiAssistSession(f.form);
            f.begin();
            const newer = deferred();
            const pending = f.submit(() => newer.promise);
            if (outcome === "rejection") old.reject(new Error("Late failure"));
            else old.resolve(outcome === "success" ? success({title: "Old"}) : {ok: false, json: async () => ({detail: "Late error"})});
            await abandoned;
            assert.equal(f.message.textContent, "Requesting AI assistance...");
            assert.equal(f.button.disabled, true);
            newer.resolve(success({title: "New"}));
            await pending;
            assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "New");
        }
    }
});

test("test_ai_late_json_cannot_replace_later_results", async function test_ai_late_json_cannot_replace_later_results() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        for (const outcome of ["success", "error", "rejection"]) {
            const f = fixture(prefix);
            const json = deferred(), reading = deferred();
            const abandoned = f.submit(async () => ({ok: outcome !== "error", json: () => { reading.resolve(); return json.promise; }}));
            await reading.promise;
            f.runtime.endAiAssistSession(f.form);
            f.begin();
            await f.submit(async () => success({title: "Later result"}));
            if (outcome === "rejection") json.reject(new Error("Earlier JSON failure"));
            else json.resolve(outcome === "success"
                ? {outcome: "suggestions", suggestions: {title: "Earlier result"}}
                : {detail: "Earlier error"});
            await abandoned;
            assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "Later result");
            assert.equal(f.button.disabled, true);
            assert.match(f.message.textContent, /ready for review/);
        }
    }
});

test("test_ai_results_do_not_populate_hidden_or_disconnected_forms", async function test_ai_results_do_not_populate_hidden_or_disconnected_forms() {
    for (const property of ["hidden", "isConnected"]) {
        const f = fixture("bug-");
        const response = deferred();
        const pending = f.submit(() => response.promise);
        f.form[property] = property === "hidden";
        response.resolve(success({title: "Abandoned"}));
        await pending;
        assert.equal(f.area.hidden, true);
        assert.equal(f.inputs["#bug-title"].value, "");
    }
});

test("test_ai_sessions_are_isolated_between_new_and_edit_forms", async function test_ai_sessions_are_isolated_between_new_and_edit_forms() {
    const newBug = fixture("bug-"), editBug = fixture("edit-bug-", newBug.runtime);
    const response = deferred();
    const pending = newBug.submit(() => response.promise);
    newBug.runtime.endAiAssistSession(newBug.form);
    await editBug.submit(async () => success({title: "Edit suggestion"}));
    response.resolve(success({title: "New suggestion"}));
    await pending;
    assert.equal(newBug.area.hidden, true);
    assert.equal(editBug.card("Title").querySelector(".ai-suggestion-value").textContent, "Edit suggestion");
});

test("test_ai_use_all_maps_every_supported_field_without_persistence", async function test_ai_use_all_maps_every_supported_field_without_persistence() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        const suggestions = {
            title: "Title", affected_version: "0.2", environment: "Windows",
            description: "Description", steps_to_reproduce: "1. Start\n2. Submit",
            expected_result: "Success", actual_result: "Failure",
            severity: "Major", priority: "High", assignee_id: 7
        };
        f.inputs[`#${prefix}fix-version`].value = "Keep fix version";
        let saves = 0;
        f.form.addEventListener("submit", () => { saves += 1; });
        assert.equal(f.requests.length, 0);
        await f.submit(async () => success(suggestions));
        f.action("Use All");
        assert.deepEqual(JSON.parse(JSON.stringify(f.runtime.collectAiAssistContext(f.form, prefix))), suggestions);
        assert.equal(f.inputs[`#${prefix}fix-version`].value, "Keep fix version");
        assert.equal(f.requests.length, 1);
        assert.equal(saves, 0);
    }
});

test("test_ai_validated_assignee_missing_from_dropdown_is_reviewable_and_usable", async function test_ai_validated_assignee_missing_from_dropdown_is_reviewable_and_usable() {
    for (const prefix of ["bug-", "edit-bug-"]) {
        const f = fixture(prefix);
        const input = f.inputs[`#${prefix}assignee`];
        input.value = "7";
        await f.submit(async () => success({title: "Title", assignee_id: 8}));
        assert.equal(input.value, "7");
        assert.equal(input.options.length, 2);
        assert.equal(f.card("Assignee").querySelector(".ai-suggestion-value").textContent, "User 8");
        f.action("Use All");
        assert.equal(input.value, "8");
        assert.equal(input.options[2].value, "8");
        assert.equal(input.options[2].textContent, "User 8");
        assert.equal(f.inputs[`#${prefix}title`].value, "Title");
        assert.equal(f.requests.length, 1);
    }
});
