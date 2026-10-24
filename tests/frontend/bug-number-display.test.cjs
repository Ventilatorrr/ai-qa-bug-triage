const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");
const {loadPageScript} = require("./helpers/page-script.cjs");

function page(search = "?project_id=3&bug_number=7") {
    const nodes = new Map(), feedback = new Map(), calls = [];
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new Element());
        return nodes.get(selector);
    };
    let destination;
    const document = {querySelector: node, querySelectorAll: () => [], createElement: tag => new Element(tag)};
    const window = new Element();
    window.location = {search, replace: url => { destination = url; }};
    const runtime = vm.createContext({document, window, URLSearchParams, console, confirm: () => true,
        localStorage: {getItem: () => null, removeItem() {}},
        sessionStorage: {setItem: (key, value) => feedback.set(key, value)}});
    loadPageScript(runtime, "bugs.js");
    runtime.authenticatedFetch = async (url, options) => { calls.push([url, options?.method]); return {status: 204}; };
    const bug = {id: 42, project_id: 3, bug_number: 7, title: "Example", status: "Triage", assignee_id: null};
    return {runtime, node, document, feedback, calls, bug, destination: () => destination};
}

// TC-262 | AC-012.2 — Bug details and deletion use local resource number
test("test_bug_details_and_deletion_use_local_resource_number", async () => {
    const f = page();
    f.runtime.renderBug(f.bug);
    assert.equal(f.document.title, "BUG-7: Example - AI QA Bug Triage");
    assert.equal(f.node("#bug-reference").textContent, "BUG-7");
    vm.runInContext(`currentBug = ${JSON.stringify(f.bug)}`, f.runtime);
    for (const handler of f.node("#delete-bug-button").listeners.click) await handler();
    assert.deepEqual(f.calls, [["/projects/3/bugs/7", "DELETE"]]);
    assert.equal(f.feedback.get("bug-deletion-feedback"), 'BUG-7 "Example" deleted successfully.');
    assert.equal(f.destination(), "/project.html?id=3");
});

// TC-263 | AC-014.1 — Bug deletion requires confirmation and preserves cancelled report
test("test_bug_deletion_requires_confirmation_and_preserves_cancelled_report", async function test_bug_deletion_requires_confirmation_and_preserves_cancelled_report() {
    for (const confirmed of [false, true]) {
        const f = page();
        const prompts = [];
        const initialDestination = f.destination();
        f.runtime.confirm = message => { prompts.push(message); return confirmed; };
        vm.runInContext(`currentBug = ${JSON.stringify(f.bug)}`, f.runtime);
        for (const handler of f.node("#delete-bug-button").listeners.click) await handler();
        assert.deepEqual(prompts, ['Are you sure you want to delete "Example"?']);
        assert.equal(f.node("#delete-bug-button").disabled, false);
        if (confirmed) {
            assert.deepEqual(f.calls, [["/projects/3/bugs/7", "DELETE"]]);
            assert.equal(f.destination(), "/project.html?id=3");
        } else {
            assert.deepEqual(f.calls, []);
            assert.equal(f.destination(), initialDestination, "cancellation causes no additional navigation");
            assert.equal(f.feedback.size, 0);
            assert.equal(vm.runInContext("currentBug.title", f.runtime), "Example");
        }
    }
});

// TC-264 | AC-012.2 — Bug response validates project and local resource number
test("test_bug_response_validates_project_and_local_resource_number", () => {
    const f = page();
    assert.equal(f.runtime.isValidBugResponse(f.bug), true);
    for (const bug_number of [undefined, null, 0, -1, 1.5, "7"]) {
        assert.equal(f.runtime.isValidBugResponse({...f.bug, bug_number}), false);
    }
    assert.equal(f.runtime.isValidBugResponse({...f.bug, id: 66}), true);
    for (const id of [undefined, null, 0, -1, 1.5, "42"]) {
        assert.equal(f.runtime.isValidBugResponse({...f.bug, id}), false);
    }
    assert.equal(f.runtime.isValidBugResponse({...f.bug, bug_number: 42}), false);
    assert.equal(f.runtime.isValidBugResponse({...f.bug, project_id: 4}), false);
});

// TC-265 | Technical — Project navigation preserves full name as text and focus tooltip
test("test_project_navigation_preserves_full_name_as_text_and_focus_tooltip", async () => {
    const f = page();
    const name = 'A very long project name with <literal markup> and "quotes"';
    f.runtime.authenticatedFetch = async () => ({ok: true, json: async () => ({name})});
    await f.runtime.loadProjectNavigation();
    const link = f.node("#back-to-project");
    assert.equal(link.children.length, 1);
    assert.equal(link.children[0].tagName, "span");
    assert.equal(link.children[0].textContent, name);
    assert.equal(link.title, name);
    assert.equal(link.hidden, false);
});

// TC-266 | AC-012.2 — Bug detail get and AI assist use local resource number
test("test_bug_detail_get_and_ai_assist_use_local_resource_number", async () => {
    const f = page();
    f.runtime.localStorage.getItem = () => "token";
    f.runtime.authenticatedFetch = async (url, options) => {
        f.calls.push([url, options?.method || "GET"]);
        return {ok: true, status: 200, json: async () => f.bug};
    };
    f.runtime.loadProjectMembers = async () => true;
    f.runtime.renderRoleSpecificActions = () => {};
    assert.equal(await f.runtime.loadBug(), true);
    assert.deepEqual(f.calls, [["/projects/3/bugs/7", "GET"]]);
    f.runtime.submitAiAssist = (form, prefix, url) => f.calls.push([url, "POST"]);
    for (const handler of f.node("#edit-bug-ai-assist").listeners.click) handler();
    assert.deepEqual(f.calls[1], ["/projects/3/bugs/7/ai-assist", "POST"]);
});

// TC-267 | AC-012.2 — Bug number query rejects invalid missing and legacy identity
test("test_bug_number_query_rejects_invalid_missing_and_legacy_identity", async () => {
    for (const search of [
        "?project_id=3", "?project_id=3&bug_id=42", "?project_id=3&bug_number=",
        ...["0", "-1", "1.5", "abc", "07", "1e2"].map(value => `?project_id=3&bug_number=${value}`),
    ]) {
        const f = page(search);
        f.runtime.localStorage.getItem = () => "token";
        assert.equal(await f.runtime.loadBug(), false);
        assert.deepEqual(f.calls, []);
        assert.match(f.node("#bug-message").textContent, /Invalid bug number/);
    }
});
