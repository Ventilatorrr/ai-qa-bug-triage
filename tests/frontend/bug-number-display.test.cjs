const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

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
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/bugs.js"), "utf8"), runtime);
    runtime.authenticatedFetch = async (url, options) => { calls.push([url, options?.method]); return {status: 204}; };
    const bug = {id: 42, project_id: 3, bug_number: 7, title: "Example", status: "Triage", assignee_id: null};
    return {runtime, node, document, feedback, calls, bug, destination: () => destination};
}

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
