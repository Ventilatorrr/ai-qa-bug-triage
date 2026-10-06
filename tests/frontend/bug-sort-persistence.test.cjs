const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

class PageElement extends Element {
    constructor(tag = "div") { super(tag); this.dataset = {}; }
    set innerHTML(value) { this.children = []; }
    getAttribute(name) { return this.attributes[name]; }
    querySelector(selector) {
        const column = selector.match(/^\[data-sort-column="(.+)"\]$/)?.[1];
        return column ? this.all("button").find(button => button.dataset.sortColumn === column) : super.querySelector(selector);
    }
}

function storage() {
    const entries = new Map();
    return {
        getItem: key => entries.get(key) ?? null,
        setItem: (key, value) => entries.set(key, value),
        removeItem: key => entries.delete(key)
    };
}

const key = (user = 1, project = 1) => `bug-list-sort:${user}:${project}`;
const bugs = [
    {id: 9, title: "Zulu", severity: "Minor", priority: "Low", status: "Open", assignee_id: 1, updated_at: "2026-10-01T00:00:00Z"},
    {id: 2, title: "Alpha", severity: "Blocker", priority: "Urgent", status: "Triage", assignee_id: 2, updated_at: "2026-10-03T00:00:00Z"},
    {id: 4, title: "Bravo", severity: "Major", priority: "Medium", status: "Closed", assignee_id: 3, updated_at: "2026-10-02T00:00:00Z"}
];
const columns = ["id", "title", "severity", "priority", "status", "assignee_id", "updated_at"];

async function page({session = storage(), user = 1, project = 1, script = "project.js", deletionOk = true} = {}) {
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new PageElement());
        return nodes.get(selector);
    };
    const window = new PageElement();
    window.location = {search: `?id=${project}`, replace() {}};
    const token = `header.${Buffer.from(JSON.stringify({user_id: user})).toString("base64")}.signature`;
    let currentToken = token;
    node("#bug-form").hidden = true;
    const runtime = vm.createContext({
        document: {querySelector: node, createElement: tag => new PageElement(tag)},
        window, URLSearchParams, atob, console, confirm: () => true,
        localStorage: {getItem: () => currentToken, removeItem() { currentToken = null; }},
        formatApiError: detail => detail,
        fetch: async (url, options) => ({
            ok: options?.method === "DELETE" ? deletionOk : true,
            status: options?.method === "DELETE" && !deletionOk ? 403 : 200,
            json: async () => options?.method === "DELETE" ? {detail: "Not authorized."}
                : script === "projects.js" ? []
                : url.endsWith("/members") ? [{user_id: user, email: "qa@example.com", role: "Project Owner"}]
                : url.endsWith("/bugs") ? bugs : {id: project, name: "QA Project"}
        })
    });
    if (session !== undefined && session !== null) {
        Object.defineProperty(runtime, "sessionStorage", session === "throwing-getter"
            ? {get() { throw new Error("Storage blocked"); }} : {value: session});
    }
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js", script), "utf8"), runtime);
    // Complete the real initial load before inspecting the rendered table.
    await new Promise(resolve => setImmediate(resolve));
    const table = () => node("#bugs");
    return {
        runtime, window, node,
        logout() {
            vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/logout.js"), "utf8"), runtime);
            node("#logout-button").click();
            assert.equal(currentToken, null);
        },
        sort: column => table().querySelector(`[data-sort-column="${column}"]`).click(),
        order: () => table().querySelector("tbody").children.map(row => row.children[0].children[0].textContent),
        active: () => table().all("th").filter(header => header.attributes["aria-sort"] !== "none").map(header => ({
            column: header.children[0].dataset.sortColumn,
            direction: header.attributes["aria-sort"],
            label: header.children[0].textContent
        })),
        async pageshow() {
            for (const handler of window.listeners.pageshow) await handler({persisted: true});
        }
    };
}

function assertDefault(f) {
    assert.deepEqual(f.order(), ["BUG-2", "BUG-4", "BUG-9"]);
    assert.deepEqual(f.active(), [{column: "updated_at", direction: "descending", label: "Last Updated ↓"}]);
}

test("test_bug_sort_first_visit_defaults_to_last_updated_descending", async () => {
    assertDefault(await page());
});

test("test_bug_sort_saves_column_and_direction_on_header_click", async () => {
    const session = storage(), f = await page({session});
    f.sort("title");
    assert.deepEqual(JSON.parse(session.getItem(key())), {column: "title", direction: "ascending"});
    f.sort("title");
    assert.deepEqual(JSON.parse(session.getItem(key())), {column: "title", direction: "descending"});
});

test("test_bug_sort_reinitialization_restores_order_indicators_and_links", async () => {
    const session = storage(), first = await page({session});
    first.sort("id");
    first.sort("id");
    const returned = await page({session});
    assert.deepEqual(returned.order(), ["BUG-9", "BUG-4", "BUG-2"]);
    assert.deepEqual(returned.active(), [{column: "id", direction: "descending", label: "Bug ID ↓"}]);
    assert.equal(returned.node("#bugs").querySelector("tbody").children[0].children[0].children[0].href, "/bugs.html?project_id=1&bug_id=9");
    const reloaded = await page({session});
    assert.deepEqual(reloaded.order(), returned.order());
    assert.deepEqual(reloaded.active(), returned.active());
});

test("test_bug_sort_restores_every_supported_column_and_direction", async () => {
    const ascending = {
        id: [2, 4, 9], title: [2, 4, 9], severity: [9, 4, 2], priority: [9, 4, 2],
        status: [2, 9, 4], assignee_id: [9, 2, 4], updated_at: [9, 4, 2]
    };
    for (const column of columns) for (const direction of ["ascending", "descending"]) {
        const session = storage();
        session.setItem(key(), JSON.stringify({column, direction}));
        const f = await page({session});
        const ids = direction === "ascending" ? ascending[column] : [...ascending[column]].reverse();
        assert.deepEqual(f.order(), ids.map(id => `BUG-${id}`), `${column} ${direction}`);
        assert.equal(f.active()[0].column, column);
        assert.equal(f.active()[0].direction, direction);
        assert.ok(f.active()[0].label.endsWith(direction === "ascending" ? " ↑" : " ↓"));
    }
});

test("test_bug_sort_preferences_are_isolated_by_project", async () => {
    const session = storage(), a = await page({session, project: 1}), b = await page({session, project: 2});
    a.sort("title");
    b.sort("severity");
    b.sort("severity");
    assert.equal((await page({session, project: 1})).active()[0].column, "title");
    assert.deepEqual((await page({session, project: 2})).active()[0], {column: "severity", direction: "descending", label: "Severity ↓"});
});

test("test_bug_sort_preferences_are_isolated_by_user", async () => {
    const session = storage(), a = await page({session, user: 1});
    a.sort("title");
    a.logout();
    const b = await page({session, user: 2});
    assertDefault(b);
    b.sort("status");
    assert.equal((await page({session, user: 1})).active()[0].column, "title");
    assert.equal((await page({session, user: 2})).active()[0].column, "status");
});

test("test_bug_sort_invalid_storage_falls_back_to_default", async () => {
    for (const saved of ["{", "null", "123", "[]", "{}", JSON.stringify({column: "created_at", direction: "ascending"}),
        JSON.stringify({column: "title", direction: "asc"}), JSON.stringify({column: 123, direction: "descending"}),
        JSON.stringify({column: "title"})]) {
        const session = storage();
        session.setItem(key(), saved);
        assertDefault(await page({session}));
    }
});

test("test_bug_sort_storage_failures_preserve_working_default_and_header_sorting", async () => {
    const throwing = () => { throw new Error("Storage unavailable"); };
    for (const session of [null, "throwing-getter", {getItem: throwing, setItem: throwing, removeItem: throwing},
        {getItem: () => null, setItem: throwing, removeItem() {}}]) {
        const f = await page({session});
        assertDefault(f);
        f.sort("id");
        f.sort("id");
        assert.deepEqual(f.order(), ["BUG-9", "BUG-4", "BUG-2"]);
        assert.equal(f.active()[0].column, "id");
    }
});

test("test_bug_sort_back_forward_refresh_preserves_preference", async () => {
    const session = storage(), f = await page({session});
    f.sort("title");
    f.sort("title");
    await f.pageshow();
    assert.deepEqual(f.order(), ["BUG-9", "BUG-4", "BUG-2"]);
    assert.equal(f.active()[0].direction, "descending");
});

test("test_project_deletion_clears_only_current_users_project_sort_preference", async () => {
    const session = storage();
    for (const entry of [key(1, 1), key(1, 2), key(2, 1), "unrelated"]) session.setItem(entry, "saved");
    const f = await page({session, script: "projects.js"});
    const element = new PageElement();
    element.remove = () => {};
    await f.runtime.deleteProject({id: 1, name: "QA Project"}, element);
    assert.equal(session.getItem(key(1, 1)), null);
    for (const entry of [key(1, 2), key(2, 1), "unrelated"]) assert.equal(session.getItem(entry), "saved");
});

test("test_failed_project_deletion_preserves_sort_preference", async () => {
    const session = storage();
    session.setItem(key(), "saved");
    const f = await page({session, script: "projects.js", deletionOk: false});
    await f.runtime.deleteProject({id: 1, name: "QA Project"}, new PageElement());
    assert.equal(session.getItem(key()), "saved");
});

test("test_project_deletion_succeeds_when_sort_storage_is_unavailable", async () => {
    for (const session of [null, "throwing-getter", {removeItem() { throw new Error("Storage blocked"); }, getItem: () => null}]) {
        const f = await page({session, script: "projects.js"});
        const element = new PageElement();
        let removed = false;
        element.remove = () => { removed = true; };
        await f.runtime.deleteProject({id: 1, name: "QA Project"}, element);
        assert.equal(removed, true);
        assert.match(f.node("#message").textContent, /deleted successfully/);
    }
});
