const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");
const {loadPageScript} = require("./helpers/page-script.cjs");

const reply = (status, body) => ({ok: status < 400, status, json: async () => body});
const members = [
    {user_id: 1, email: "owner@example.com", role: "Project Owner"},
    {user_id: 2, email: "qa@example.com", role: "QA Analyst"},
    {user_id: 3, email: "dev@example.com", role: "Developer"}
];

function projectPage(currentUserId, {confirmed = true, leaveResponse = reply(200, {message: "You left the project."})} = {}) {
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new Element());
        return nodes.get(selector);
    };
    node("#bug-form").hidden = true;
    const state = {requests: [], destination: null, session: new Map([["bug-list-sort:" + currentUserId + ":7", "{}"]]), confirms: []};
    const window = new Element();
    window.location = {search: "?id=7", replace: url => { state.destination = url; }};
    const token = `header.${Buffer.from(JSON.stringify({user_id: currentUserId})).toString("base64")}.signature`;
    const runtime = vm.createContext({
        document: {querySelector: node, createElement: tag => new Element(tag)},
        window, URLSearchParams, atob, console,
        confirm: text => { state.confirms.push(text); return confirmed; },
        localStorage: {getItem: key => key === "access_token" ? token : null, setItem() {}, removeItem() {}},
        sessionStorage: {
            getItem: key => state.session.get(key) ?? null,
            setItem: (key, value) => state.session.set(key, value),
            removeItem: key => state.session.delete(key)
        },
        formatApiError: detail => detail,
        fetch: async (url, options = {}) => {
            state.requests.push(`${options.method || "GET"} ${url}`);
            if (options.method === "DELETE") return leaveResponse;
            return reply(200, url.endsWith("/members") ? members : url.endsWith("/bugs") ? [] : {id: 7, name: "Shared Project"});
        }
    });
    loadPageScript(runtime, "project.js");
    const leaveButtons = () => node("#members").querySelectorAll("button").filter(button => button.textContent === "Leave Project");
    return {node, state, leaveButtons};
}

// TC-487 | AC-009.6 — Leave Project is offered only to the current QA Analyst or Developer and leaves after confirmation
test("test_leave_project_offered_to_current_non_owner_and_redirects", async () => {
    const owner = projectPage(1);
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(owner.leaveButtons().length, 0);  // An owner deletes the project instead.

    for (const userId of [2, 3]) {
        const page = projectPage(userId);
        await new Promise(resolve => setImmediate(resolve));
        assert.equal(page.leaveButtons().length, 1);  // Only beside the user's own entry.
        page.leaveButtons()[0].click();
        await new Promise(resolve => setImmediate(resolve));
        assert.match(page.state.confirms[0], /leave "Shared Project"/);
        assert.ok(page.state.requests.includes(`DELETE /projects/7/members/${userId}`));
        assert.equal(page.state.destination, "/projects.html");
        assert.equal(page.state.session.get("project-list-feedback"), 'You left "Shared Project".');
        assert.equal(page.state.session.has(`bug-list-sort:${userId}:7`), false);
    }
});

// TC-488 | AC-009.6 — Cancelling or a failed leave keeps the user on the project with feedback
test("test_leave_project_cancel_or_failure_stays_on_project", async () => {
    const cancelled = projectPage(2, {confirmed: false});
    await new Promise(resolve => setImmediate(resolve));
    cancelled.leaveButtons()[0].click();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(cancelled.state.requests.some(request => request.startsWith("DELETE")), false);
    assert.equal(cancelled.state.destination, null);

    const failed = projectPage(2, {leaveResponse: reply(404, {detail: "Project not found."})});
    await new Promise(resolve => setImmediate(resolve));
    failed.leaveButtons()[0].click();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(failed.state.destination, null);
    assert.equal(failed.node("#member-message").textContent, "Project not found.");
    assert.equal(failed.leaveButtons()[0].disabled, false);  // The user can retry.
});
