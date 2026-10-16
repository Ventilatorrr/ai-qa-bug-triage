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
    {id: 9, bug_number: 2, title: "Zulu", severity: "Minor", priority: "Low", status: "Open", assignee_id: 1, updated_at: "2026-10-01T00:00:00Z"},
    {id: 2, bug_number: 11, title: "Alpha", severity: "Blocker", priority: "Urgent", status: "Triage", assignee_id: 2, updated_at: "2026-10-03T00:00:00Z"},
    {id: 4, bug_number: 1, title: "Bravo", severity: "Major", priority: "Medium", status: "Closed", assignee_id: 3, updated_at: "2026-10-02T00:00:00Z"}
];
const columns = ["id", "title", "severity", "priority", "status", "assignee_id", "updated_at"];

async function page({
    session = storage(), preferences = storage(), user = 1, project = 1,
    script = "project.js", deletionOk = true, reports = bugs
} = {}) {
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
        localStorage: {
            getItem: key => key === "access_token" ? currentToken : preferences.getItem(key),
            setItem: (key, value) => preferences.setItem(key, value),
            removeItem() { currentToken = null; }
        },
        formatApiError: detail => detail,
        fetch: async (url, options) => ({
            ok: options?.method === "DELETE" ? deletionOk : true,
            status: options?.method === "DELETE" && !deletionOk ? 403 : 200,
            json: async () => options?.method === "DELETE" ? {detail: "Not authorized."}
                : script === "projects.js" ? []
                : url.endsWith("/members") ? [{user_id: user, email: "qa@example.com", role: "Project Owner"}]
                : url.endsWith("/bugs") ? reports : {id: project, name: "QA Project"}
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
    assert.deepEqual(f.order(), ["BUG-11", "BUG-1", "BUG-2"]);
    assert.deepEqual(f.active(), [{column: "updated_at", direction: "descending", label: "Last Updated ↓"}]);
}

// TC-268 | AC-012.6 — Page size invalid or unavailable reads fall back to ten
test("test_page_size_invalid_or_unavailable_reads_fall_back_to_ten", async () => {
    const reports = Array.from({length: 21}, (_, i) => ({...bugs[0], id: i + 1, bug_number: i + 1}));
    for (const value of [null, "", "0", "15", "-1", "20.0", "{}", "null"]) {
        const preferences = storage();
        if (value !== null) preferences.setItem("bug-list-page-size:1", value);
        const f = await page({preferences, reports});
        assert.equal(f.node("#bug-page-size").value, "10");
        assert.equal(f.order().length, 10);
        assert.equal(f.node("#bug-page-indicator").textContent, "Page 1 of 3");
    }

    const f = await page({reports, preferences: {
        getItem() { throw new Error("Storage read blocked"); }, setItem() {}
    }});
    assert.equal(f.node("#bug-page-size").value, "10");
    assert.equal(f.order().length, 10);
    f.node("#bug-next-page").click();
    assert.equal(f.node("#bug-page-indicator").textContent, "Page 2 of 3");
});

// TC-269 | AC-012.6 — Page size blocked writes preserve current pagination and sort
test("test_page_size_blocked_writes_preserve_current_pagination_and_sort", async () => {
    const reports = Array.from({length: 51}, (_, i) => ({...bugs[0], id: i + 1, bug_number: i + 1}));
    const preferences = {
        getItem: () => null,
        setItem() { throw new Error("Storage write blocked"); }
    };
    const f = await page({preferences, reports});
    f.sort("id");
    f.node("#bug-page-size").value = "20";
    f.node("#bug-page-size").dispatchEvent({type: "change"});
    assert.equal(f.order().length, 20);
    assert.equal(f.active()[0].column, "id");
    assert.equal(f.active()[0].direction, "ascending");
    f.node("#bug-next-page").click();
    assert.equal(f.node("#bug-page-indicator").textContent, "Page 2 of 3");
    assert.equal(f.order()[0], "BUG-21");

    const reloaded = await page({preferences, reports});
    assert.equal(reloaded.node("#bug-page-size").value, "10");
    assert.equal(reloaded.order().length, 10);
});

// TC-270 | AC-012.4 — Bug sort first visit defaults to last updated descending
test("test_bug_sort_first_visit_defaults_to_last_updated_descending", async () => {
    assertDefault(await page());
});

// TC-271 | AC-012.1 — Bug mobile labels and header relationships survive sorting
test("test_bug_mobile_labels_and_header_relationships_survive_sorting", async () => {
    const f = await page();
    for (const column of columns) {
        f.sort(column);
        const table = f.node("#bugs");
        const headers = table.all("th");
        for (const row of table.querySelector("tbody").children) {
            assert.equal(row.children.length, 7);
            row.children.forEach((cell, index) => {
                assert.equal(cell.dataset.label, ["Bug ID", "Title", "Severity", "Priority", "Status", "Assignee", "Last Updated"][index]);
                assert.equal(cell.attributes.headers, headers[index].id);
                assert.equal(cell.attributes.role, "cell");
            });
            assert.match(row.children[0].children[0].href, /^\/bugs.html\?project_id=1&bug_number=\d+$/);
        }
    }
});

// TC-272 | Technical — Bug list rejects invalid number response
test("test_bug_list_rejects_invalid_number_response", async () => {
    for (const bug_number of [undefined, null, 0, -1, 1.5, "11"]) {
        const f = await page({reports: [{...bugs[0], bug_number}]});
        assert.match(f.node("#bug-message").textContent, /Invalid server response/);
        assert.equal(f.node("#bugs").querySelector("tbody"), null);
    }
});

// TC-273 | AC-012.4 — Bug sort saves column and direction on header click
test("test_bug_sort_saves_column_and_direction_on_header_click", async () => {
    const session = storage(), f = await page({session});
    f.sort("title");
    assert.deepEqual(JSON.parse(session.getItem(key())), {column: "title", direction: "ascending"});
    f.sort("title");
    assert.deepEqual(JSON.parse(session.getItem(key())), {column: "title", direction: "descending"});
});

// TC-274 | AC-012.4 — Mobile sort controls reuse all columns direction and preferences
test("test_mobile_sort_controls_reuse_all_columns_direction_and_preferences", async () => {
    const session = storage(), f = await page({session});
    for (const column of columns) {
        f.node("#bug-sort-field").value = column;
        f.node("#bug-sort-field").dispatchEvent({type: "change"});
        assert.equal(f.active()[0].column, column);
        assert.equal(f.active()[0].direction, "ascending");
        assert.equal(f.node("#bug-sort-direction").getAttribute("aria-label"), "Sort descending");
        const ascending = [...f.order()];
        f.node("#bug-sort-direction").click();
        assert.deepEqual(f.order(), [...ascending].reverse());
        assert.equal(f.node("#bug-sort-direction").textContent, "↓ Descending");
        assert.deepEqual(JSON.parse(session.getItem(key())), {column, direction: "descending"});
    }
    const restored = await page({session});
    assert.equal(restored.node("#bug-sort-field").value, "updated_at");
    assert.equal(restored.node("#bug-sort-direction").textContent, "↓ Descending");
    restored.sort("title");
    assert.equal(restored.node("#bug-sort-field").value, "title");
    assert.equal(restored.node("#bug-sort-direction").textContent, "↑ Ascending");
});

// TC-275 | AC-012.4, AC-012.5 — Mobile sort resets pagination and empty list hides toolbar
test("test_mobile_sort_resets_pagination_and_empty_list_hides_toolbar", async () => {
    const reports = Array.from({length: 11}, (_, i) => ({...bugs[0], id: i + 1, bug_number: i + 1}));
    const f = await page({reports});
    f.node("#bug-next-page").click();
    assert.equal(f.order().length, 1);
    f.node("#bug-sort-direction").click();
    assert.equal(f.order().length, 10);
    assert.equal(f.node("#bug-page-indicator").textContent, "Page 1 of 2");
    assert.equal((await page({reports: []})).node("#bug-mobile-sort").hidden, true);
});

// TC-276 | AC-012.4 — Bug sort reinitialization restores order indicators and links
test("test_bug_sort_reinitialization_restores_order_indicators_and_links", async () => {
    const session = storage(), first = await page({session});
    first.sort("id");
    first.sort("id");
    const returned = await page({session});
    assert.deepEqual(returned.order(), ["BUG-11", "BUG-2", "BUG-1"]);
    assert.deepEqual(returned.active(), [{column: "id", direction: "descending", label: "Bug ID ↓"}]);
    assert.equal(returned.node("#bugs").querySelector("tbody").children[0].children[0].children[0].href, "/bugs.html?project_id=1&bug_number=11");
    const reloaded = await page({session});
    assert.deepEqual(reloaded.order(), returned.order());
    assert.deepEqual(reloaded.active(), returned.active());
});

// TC-277 | AC-012.4 — Bug sort restores every supported column and direction
test("test_bug_sort_restores_every_supported_column_and_direction", async () => {
    const ascending = {
        id: [4, 9, 2], title: [2, 4, 9], severity: [9, 4, 2], priority: [9, 4, 2],
        status: [2, 9, 4], assignee_id: [9, 2, 4], updated_at: [9, 4, 2]
    };
    for (const column of columns) for (const direction of ["ascending", "descending"]) {
        const session = storage();
        session.setItem(key(), JSON.stringify({column, direction}));
        const f = await page({session});
        const ids = direction === "ascending" ? ascending[column] : [...ascending[column]].reverse();
        assert.deepEqual(f.order(), ids.map(id => `BUG-${bugs.find(bug => bug.id === id).bug_number}`), `${column} ${direction}`);
        assert.equal(f.active()[0].column, column);
        assert.equal(f.active()[0].direction, direction);
        assert.ok(f.active()[0].label.endsWith(direction === "ascending" ? " ↑" : " ↓"));
    }
});

// TC-278 | AC-012.4 — Bug sort preferences are isolated by project
test("test_bug_sort_preferences_are_isolated_by_project", async () => {
    const session = storage(), a = await page({session, project: 1}), b = await page({session, project: 2});
    a.sort("title");
    b.sort("severity");
    b.sort("severity");
    assert.equal((await page({session, project: 1})).active()[0].column, "title");
    assert.deepEqual((await page({session, project: 2})).active()[0], {column: "severity", direction: "descending", label: "Severity ↓"});
});

// TC-279 | AC-012.4 — Bug sort preferences are isolated by user
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

// TC-280 | AC-012.4 — Bug sort invalid storage falls back to default
test("test_bug_sort_invalid_storage_falls_back_to_default", async () => {
    for (const saved of ["{", "null", "123", "[]", "{}", JSON.stringify({column: "created_at", direction: "ascending"}),
        JSON.stringify({column: "title", direction: "asc"}), JSON.stringify({column: 123, direction: "descending"}),
        JSON.stringify({column: "title"})]) {
        const session = storage();
        session.setItem(key(), saved);
        assertDefault(await page({session}));
    }
});

// TC-281 | AC-012.4 — Bug sort storage failures preserve working default and header sorting
test("test_bug_sort_storage_failures_preserve_working_default_and_header_sorting", async () => {
    const throwing = () => { throw new Error("Storage unavailable"); };
    for (const session of [null, "throwing-getter", {getItem: throwing, setItem: throwing, removeItem: throwing},
        {getItem: () => null, setItem: throwing, removeItem() {}}]) {
        const f = await page({session});
        assertDefault(f);
        f.sort("id");
        f.sort("id");
        assert.deepEqual(f.order(), ["BUG-11", "BUG-2", "BUG-1"]);
        assert.equal(f.active()[0].column, "id");
    }
});

// TC-282 | AC-012.4 — Bug sort back forward refresh preserves preference
test("test_bug_sort_back_forward_refresh_preserves_preference", async () => {
    const session = storage(), f = await page({session});
    f.sort("title");
    f.sort("title");
    await f.pageshow();
    assert.deepEqual(f.order(), ["BUG-2", "BUG-1", "BUG-11"]);
    assert.equal(f.active()[0].direction, "descending");
});

// TC-283 | Technical — Project deletion clears only current users project sort preference
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

// TC-284 | Technical — Failed project deletion preserves sort preference
test("test_failed_project_deletion_preserves_sort_preference", async () => {
    const session = storage();
    session.setItem(key(), "saved");
    const f = await page({session, script: "projects.js", deletionOk: false});
    await f.runtime.deleteProject({id: 1, name: "QA Project"}, new PageElement());
    assert.equal(session.getItem(key()), "saved");
});

// TC-285 | Technical — Project deletion succeeds when sort storage is unavailable
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

// TC-348 (severity), TC-349 (priority), TC-350 (status) | AC-012.4 — Complete rank sorting in both directions
for (const [column, values, ascending, descending] of [
    ["severity", ["Major", "Minor", "Blocker", "Moderate"],
        ["Minor", "Moderate", "Major", "Blocker"], ["Blocker", "Major", "Moderate", "Minor"]],
    ["priority", ["High", "Low", "Urgent", "Medium"],
        ["Low", "Medium", "High", "Urgent"], ["Urgent", "High", "Medium", "Low"]],
    ["status", ["Testing", "Triage", "Closed", "Open", "Development"],
        ["Triage", "Open", "Development", "Testing", "Closed"],
        ["Closed", "Testing", "Development", "Open", "Triage"]],
]) {
    test(`test_bug_sort_complete_${column}_rank_order`, async () => {
        const reports = values.map((value, index) => ({
            ...bugs[0], id: 100 + index, bug_number: index + 1, [column]: value
        }));
        const f = await page({reports});
        const displayedValues = () => f.node("#bugs").querySelector("tbody").children
            .map(row => row.children[columns.indexOf(column)].textContent);

        f.sort(column);

        assert.deepEqual(displayedValues(), ascending);
        assert.deepEqual(f.order(), ascending.map(value => `BUG-${values.indexOf(value) + 1}`));

        f.sort(column);

        assert.deepEqual(displayedValues(), descending);
        assert.deepEqual(f.order(), descending.map(value => `BUG-${values.indexOf(value) + 1}`));
    });
}
