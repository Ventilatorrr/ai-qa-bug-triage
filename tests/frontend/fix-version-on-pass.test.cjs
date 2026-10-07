const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

class PageElement extends Element {
    constructor(tag) { super(tag); if (tag === "select") this.options = []; }
    set innerHTML(value) { this.children = []; if (this.options) this.options = []; }
}

async function page({role = "QA Analyst", status = "Testing", fixVersion = null, assigned = true} = {}) {
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new PageElement(
            selector.endsWith("-assignee") || selector === "#lifecycle-resolution" ? "select"
                : selector === "#lifecycle-pass-fix-version" ? "input" : "div"
        ));
        return nodes.get(selector);
    };
    node("#edit-bug-form").hidden = true;
    const window = new Element();
    window.location = {search: "?project_id=1&bug_id=2", replace() {}};
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
    const actor = members.find(member => member.role === role);
    const bug = {id: 2, status, assignee_id: assigned ? 3 : 1, fix_version: fixVersion};
    vm.runInContext(`currentBug = ${JSON.stringify(bug)}; projectMembers = ${JSON.stringify(members)}; currentMember = ${JSON.stringify(actor)};`, runtime);
    const requests = [];
    Object.assign(runtime, {
        authenticatedFetch: async (url, options) => {
            const payload = JSON.parse(options.body);
            requests.push({url, method: options.method, payload});
            assert.equal(node("#lifecycle-pass-fix-version").disabled, true);
            Object.assign(bug, payload, {resolution: payload.testing_outcome === "Passed" ? "Fixed" : null});
            return {ok: true, status: 200, json: async () => bug};
        },
        loadBug: async () => {
            vm.runInContext(`currentBug = ${JSON.stringify(bug)}`, runtime);
            runtime.renderLifecycleControls();
            return true;
        },
        isValidBugResponse: data => data?.id === 2,
    });
    runtime.renderLifecycleControls();
    const click = async selector => {
        for (const handler of node(selector).listeners.click || []) await handler({});
    };
    return {node, click, requests, bug};
}

test("test_passed_fix_version_input_visible_and_sends_value", async () => {
    const html = fs.readFileSync(path.join(__dirname, "../../frontend/bugs.html"), "utf8");
    const input = html.match(/<input\b[^>]*id="lifecycle-pass-fix-version"[^>]*>/)?.[0];
    const field = html.match(/<div\b[^>]*id="lifecycle-pass-fix-version-field"[^>]*>([\s\S]*?)<\/div>/)?.[1];
    const labels = [...(field || "").matchAll(/<label\b([^>]*)for="lifecycle-pass-fix-version"([^>]*)>([\s\S]*?)<\/label>/g)];
    assert.ok(input, "Fix Version input exists in HTML");
    assert.doesNotMatch(input, /\brequired\b/);
    assert.equal(labels.length, 1, "One associated label exists inside the control");
    assert.equal(labels[0][3].trim(), "Fix Version (optional)");
    assert.doesNotMatch(labels[0][1] + labels[0][2], /\bhidden\b|aria-hidden="true"/, "Label is not hidden");
    assert.match(input, /placeholder=" "/, "Blank placeholder supports CSS empty-state detection");
    assert.doesNotMatch(input, /aria-label(?:ledby)?=/, "The semantic label provides the accessible name");
    assert.doesNotMatch(html, /lifecycle-confirm-pass-button/, "No Confirm Passed button");
    assert.doesNotMatch(html, /lifecycle-cancel-pass-button/, "No Cancel button");
    assert.doesNotMatch(html, /lifecycle-pass-confirmation/, "No confirmation container");
    assert.doesNotMatch(html, /lifecycle-pass-fix-version-help/, "No Passed guidance paragraph");

    for (const [current, entered, expected, role] of [
        [null, "1.3.0", "1.3.0", "QA Analyst"],
        ["1.2.0", undefined, "1.2.0", "Project Owner"],
        ["1.2.0", "1.3.0", "1.3.0", "QA Analyst"],
        [null, "", null, "QA Analyst"],
        ["1.2.0", "", null, "QA Analyst"],
        [null, " 1.3.0 ", " 1.3.0 ", "QA Analyst"],
        [null, " \t ", " \t ", "QA Analyst"],
    ]) {
        const f = await page({fixVersion: current, role});
        assert.equal(f.node("#lifecycle-testing-actions").hidden, false, "Testing controls visible on render");
        assert.equal(f.node("#lifecycle-pass-fix-version-field").hidden, false, "Input visible before Passed");
        assert.equal(f.node("#lifecycle-pass-fix-version").disabled, false, "Input enabled on render");
        assert.equal(f.node("#lifecycle-pass-button").disabled, false, "Passed enabled on render");
        assert.equal(f.node("#lifecycle-pass-fix-version").value, current || "", "Prefilled correctly");
        if (entered !== undefined) f.node("#lifecycle-pass-fix-version").value = entered;
        await f.click("#lifecycle-pass-button");
        assert.deepEqual(f.requests, [{url: "/projects/1/bugs/2/status", method: "PATCH", payload: {
            status: "Closed", testing_outcome: "Passed", fix_version: expected,
        }}]);
        assert.equal(f.bug.status, "Closed");
        assert.equal(f.bug.resolution, "Fixed");
    }
});

test("test_passed_fix_version_respects_eligibility", async () => {
    for (const settings of [{status: "Closed"}, {status: "Development"}, {role: "Developer"}, {assigned: false}]) {
        const f = await page(settings);
        assert.equal(f.node("#lifecycle-pass-fix-version").disabled, true, `Disabled for ${JSON.stringify(settings)}`);
        assert.equal(f.node("#lifecycle-pass-button").disabled, true, `Passed disabled for ${JSON.stringify(settings)}`);
        await f.click("#lifecycle-pass-button");
        assert.equal(f.requests.length, 0, `No request for ${JSON.stringify(settings)}`);
    }
});

test("test_failed_flow_does_not_use_fix_version", async () => {
    const f = await page({fixVersion: "1.2.0"});
    f.node("#lifecycle-pass-fix-version").value = "Do not apply";
    f.node("#lifecycle-developer-assignee").value = "2";
    await f.click("#lifecycle-fail-button");
    assert.deepEqual(f.requests, [{url: "/projects/1/bugs/2/status", method: "PATCH", payload: {
        status: "Development", testing_outcome: "Failed", assignee_id: 2,
    }}]);
    assert.equal(f.bug.status, "Development");
    assert.equal(f.bug.resolution, null);
    assert.equal(f.bug.fix_version, "1.2.0");
});
