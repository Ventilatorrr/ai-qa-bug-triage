const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

class PageElement extends Element {
    constructor(tag) { super(tag); if (tag === "select") this.options = []; }
    set innerHTML(value) {
        this.children = [];
        if (this.options) { this.options = []; this.value = ""; }
    }
}

async function page(status, role = "Project Owner", assignee = 2) {
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new PageElement(
            selector.endsWith("-assignee") || selector === "#lifecycle-resolution" ? "select" : "div"
        ));
        return nodes.get(selector);
    };
    node("#edit-bug-form").hidden = true;
    const window = new Element();
    window.location = {search: "?project_id=1&bug_number=2", replace() {}};
    const runtime = vm.createContext({
        document: {querySelector: node, querySelectorAll: () => [], createElement: tag => new PageElement(tag)},
        window, URLSearchParams, console,
        localStorage: {getItem: () => null, removeItem() {}},
        endAiAssistSession() {}, formatApiError: (detail, fallback) => detail || fallback,
    });
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/bugs.js"), "utf8"), runtime);
    await new Promise(resolve => setImmediate(resolve));
    const members = [
        {user_id: 1, email: "owner@example.com", role: "Project Owner"},
        {user_id: 2, email: "dev@example.com", role: "Developer"},
        {user_id: 3, email: "qa@example.com", role: "QA Analyst"},
    ];
    const bug = {id: 42, project_id: 1, bug_number: 2, title: "Example", status, assignee_id: assignee, resolution: null};
    const render = () => {
        vm.runInContext(`currentBug = ${JSON.stringify(bug)}`, runtime);
        runtime.renderLifecycleControls();
    };
    vm.runInContext(`projectMembers = ${JSON.stringify(members)}; currentMember = ${JSON.stringify(members.find(member => member.role === role))}`, runtime);
    const requests = [];
    Object.assign(runtime, {
        authenticatedFetch: async (url, options) => {
            const payload = JSON.parse(options.body);
            requests.push({url, method: options.method, payload});
            Object.assign(bug, payload);
            return {ok: true, status: 200, json: async () => bug};
        },
        loadBug: async () => { render(); return true; },
    });
    render();
    const change = (selector, value) => {
        node(selector).value = value;
        node(selector).dispatchEvent({type: "change"});
    };
    // Invoke handlers directly to exercise defensive validation even for disabled buttons.
    const click = async selector => {
        for (const handler of node(selector).listeners.click || []) await handler({});
    };
    return {node, change, click, requests, bug};
}

const action = "#lifecycle-action-button";
const assignee = "#lifecycle-assignee";
const qa = "#lifecycle-qa-assignee";
const resolution = "#lifecycle-resolution";
const close = "#lifecycle-close-button";
const request = payload => [{url: "/projects/1/bugs/2/status", method: "PATCH", payload}];

test("test_bug_action_feedback_follows_controls", () => {
    const html = fs.readFileSync(path.join(__dirname, "../../frontend/bugs.html"), "utf8");
    assert.match(html,
        /<section\b[^>]*class="bug-actions"[^>]*>[\s\S]*?<\/section>\s*<p id="bug-message" class="section-message" role="status" aria-live="polite">/,
        "Bug actions precede their existing feedback live region in normal document flow");
    assert.equal((html.match(/id="bug-message"/g) || []).length, 1,
        "The feedback live region is not duplicated");
});

test("test_move_to_open_requires_eligible_selection_and_resets_after_transition", async () => {
    for (const [role, selected] of [["Project Owner", "2"], ["Project Owner", "3"], ["QA Analyst", "2"]]) {
        const f = await page("Triage", role);
        assert.equal(f.node(action).textContent, "Move to Open");
        assert.equal(f.node(assignee).disabled, false);
        assert.equal(f.node(action).disabled, true, "Empty selection disables Move to Open on render");
        f.change(assignee, selected);
        assert.equal(f.node(action).disabled, false);
        for (const invalid of ["", "1", "999"]) {
            f.change(assignee, invalid);
            assert.equal(f.node(action).disabled, true, "Empty/ineligible selection disables Move to Open");
            await f.click(action);
            assert.equal(f.requests.length, 0);
            assert.equal(f.node("#lifecycle-guidance").textContent, "Select a QA Analyst or Developer before moving to Open.");
            f.change(assignee, selected);
            assert.equal(f.node(action).disabled, false);
        }
        await f.click(action);
        assert.deepEqual(f.requests, request({status: "Open", assignee_id: Number(selected)}));
        assert.equal(f.bug.status, "Open");
        assert.equal(f.bug.assignee_id, Number(selected));
        assert.equal(f.node(action).disabled, true, "Next lifecycle state starts with no selection");
        assert.equal(f.node(assignee).value, "");
    }
});

test("test_move_to_development_requires_developer_selection_and_resets_after_transition", async () => {
    for (const [role, currentAssignee] of [["Project Owner", 3], ["Developer", 2]]) {
        const f = await page("Open", role, currentAssignee);
        assert.equal(f.node(action).textContent, "Move to Development");
        assert.equal(f.node(assignee).disabled, false);
        assert.equal(f.node(action).disabled, true, "Empty selection disables Move to Development on render");
        f.change(assignee, "2");
        assert.equal(f.node(action).disabled, false);
        for (const invalid of ["", "3", "999"]) {
            f.change(assignee, invalid);
            assert.equal(f.node(action).disabled, true, "Empty/non-Developer selection disables Move to Development");
            await f.click(action);
            assert.equal(f.requests.length, 0);
            assert.equal(f.node("#lifecycle-guidance").textContent, "Select a Developer before moving to Development.");
            f.change(assignee, "2");
            assert.equal(f.node(action).disabled, false);
        }
        await f.click(action);
        assert.deepEqual(f.requests, request({status: "Development", assignee_id: 2}));
        assert.equal(f.bug.status, "Development");
        assert.equal(f.bug.assignee_id, 2);
        assert.equal(f.node(action).textContent, "Send to Testing");
        assert.equal(f.node(action).disabled, true);
        assert.equal(f.node("#lifecycle-assignee-field").hidden, true);
        assert.equal(f.node("#lifecycle-qa-field").hidden, false);
        assert.equal(f.node(qa).value, "");
    }
});

test("test_send_to_testing_and_close_retain_required_selection_behavior", async () => {
    for (const [selector, button, selected, payload] of [
        [qa, action, "3", {status: "Testing", assignee_id: 3}],
        [resolution, close, "Duplicate", {status: "Closed", resolution: "Duplicate"}],
    ]) {
        const f = await page("Development");
        assert.equal(f.node(button).disabled, true);
        await f.click(button);
        assert.equal(f.requests.length, 0);
        f.change(selector, selected);
        assert.equal(f.node(button).disabled, false);
        f.change(selector, "");
        assert.equal(f.node(button).disabled, true);
        await f.click(button);
        assert.equal(f.requests.length, 0);
        f.change(selector, selected);
        assert.equal(f.node(button).disabled, false);
        await f.click(button);
        assert.deepEqual(f.requests, request(payload));
        assert.equal(f.bug.status, payload.status);
        assert.equal(f.node("#lifecycle-qa-field").hidden, true);
        if (payload.status === "Closed") {
            assert.equal(f.node(resolution).value, "");
            assert.equal(f.node(action).textContent, "Move to Triage");
            assert.equal(f.node(action).disabled, false, "Return to Triage requires no selection");
        }
    }
});
