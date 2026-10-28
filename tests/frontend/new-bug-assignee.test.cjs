const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");
const {loadPageScript} = require("./helpers/page-script.cjs");

const reply = (status, body) => ({ok: status < 400, status, json: async () => body});
const settle = () => new Promise(resolve => setImmediate(resolve));

// A select substitute whose innerHTML reset clears its options, like the DOM.
class Select extends Element {
    constructor() {
        super("select");
        this.options = [];
    }
    set innerHTML(value) {
        this.children = [];
        this.options = [];
        this.value = "";  // The first rebuilt option ("Unassigned") becomes selected.
    }
}

function projectPage() {
    const owner = {user_id: 1, email: "owner@example.com", role: "Project Owner"};
    const qa = {user_id: 2, email: "qa@example.com", role: "QA Analyst"};
    const developer = {user_id: 3, email: "dev@example.com", role: "Developer"};
    const state = {members: [owner, qa, developer]};
    const nodes = new Map([["#bug-assignee", new Select()]]);
    const node = selector => {
        if (!nodes.has(selector)) {
            const element = new Element();
            element.getAttribute = name => element.attributes[name] ?? null;
            nodes.set(selector, element);
        }
        return nodes.get(selector);
    };
    node("#bug-form").hidden = true;
    node("#member-form").hidden = true;
    node("#member-form").reset = () => {};
    const window = new Element();
    window.location = {search: "?id=7", replace() {}};
    const token = `header.${Buffer.from(JSON.stringify({user_id: 1})).toString("base64")}.signature`;
    const runtime = vm.createContext({
        document: {querySelector: node, createElement: tag => new Element(tag)},
        window, URLSearchParams, atob, console, confirm: () => true,
        // AI Assist is a separate classic script; its session hooks are not under test here.
        beginAiAssistSession() {}, endAiAssistSession() {},
        localStorage: {getItem: key => key === "access_token" ? token : null, setItem() {}, removeItem() {}},
        sessionStorage: {getItem: () => null, setItem() {}, removeItem() {}},
        formatApiError: detail => detail,
        fetch: async (url, options = {}) => {
            if (options.method === "POST") {
                state.members = [...state.members, {user_id: 4, email: "new@example.com", role: "QA Analyst"}];
                return reply(201, {email: "new@example.com", role: "QA Analyst"});
            }
            if (options.method === "DELETE") {
                state.members = state.members.filter(member => member.user_id !== 3);
                return reply(200, {message: "Project member removed successfully."});
            }
            return reply(200, url.endsWith("/members") ? state.members : url.endsWith("/bugs") ? [] : {id: 7, name: "Project"});
        }
    });
    loadPageScript(runtime, "project.js");
    return {node};
}

// TC-492 | AC-011.1, AC-015.1 — New Bug keeps the selected assignee when members change, and reports a removed one (BUG-50 regression)
test("test_new_bug_keeps_selected_assignee_when_members_change", async () => {
    const page = projectPage();
    await settle();
    page.node("#show-bug-form").click();
    await settle();
    const assignee = page.node("#bug-assignee");
    assert.deepEqual(assignee.options.map(option => option.value), ["", "2", "3"].map(String));
    assignee.value = "3";

    // Adding a member rebuilds the options but keeps the open form's choice.
    page.node("#member-email").value = "new@example.com";
    page.node("#member-role").value = "QA Analyst";
    page.node("#member-form").dispatchEvent({type: "submit", preventDefault() {}});
    await settle();
    await settle();
    assert.deepEqual(assignee.options.map(option => option.value), ["", "2", "3", "4"]);
    assert.equal(assignee.value, "3");

    // Removing the chosen member leaves it unassigned and tells the user.
    const removeDeveloper = page.node("#members").querySelectorAll("button")
        .find(button => button.parent.children[0].children[0].textContent === "dev@example.com");
    removeDeveloper.click();
    await settle();
    await settle();
    assert.deepEqual(assignee.options.map(option => option.value), ["", "2", "4"]);
    assert.equal(assignee.value, "");
    assert.equal(page.node("#bug-message").textContent, "The selected assignee is no longer a project member.");
});
