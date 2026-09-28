const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function fixture(prefix) {
    const runtime = vm.createContext({formatApiError: (detail) => detail});
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/ai-assist.js"), "utf8"), runtime);
    const inputs = Object.fromEntries([
        "title", "affected-version", "environment", "description", "steps",
        "expected", "actual", "severity", "priority", "assignee", "fix-version"
    ].map(suffix => [`#${prefix}${suffix}`, {value: ""}]));
    const form = {querySelector: selector => inputs[selector]};
    return {runtime, inputs, form};
}

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
    const {runtime, inputs, form} = fixture("edit-bug-");
    inputs["#edit-bug-title"].value = "Unsaved edit";
    const button = {disabled: false};
    const message = {textContent: ""};
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
    const {runtime, form} = fixture("bug-");
    const button = {disabled: false};
    const message = {textContent: ""};
    await runtime.submitAiAssist(form, "bug-", "/projects/1/ai-assist", button, message, async () => {
        throw new Error("Offline");
    });
    assert.equal(button.disabled, false);
    assert.equal(message.textContent, "Unable to request AI assistance. Please try again.");
});
