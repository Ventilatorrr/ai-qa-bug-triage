const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element, fixture, success, deferred} = require("./helpers/ai-fixture.cjs");

// Execute actual page scripts and event handlers; stub only surrounding APIs/rendering.
function pageFixture(edit, {realListRefresh = false} = {}) {
    const prefix = edit ? "edit-bug-" : "bug-";
    const f = fixture(prefix);
    const nodes = new Map(Object.entries(f.inputs));
    nodes.set(edit ? "#edit-bug-form" : "#bug-form", f.form);
    nodes.set(edit ? "#edit-bug-ai-assist" : "#new-bug-ai-assist", f.button);
    nodes.set(edit ? "#edit-bug-ai-message" : "#new-bug-ai-message", f.message);
    nodes.set(edit ? "#edit-bug-ai-suggestions" : "#new-bug-ai-suggestions", f.area);
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new Element());
        return nodes.get(selector);
    };
    const window = new Element();
    window.location = {search: "?id=1&project_id=1&bug_number=11", replace() {}};
    Object.assign(f.runtime, {
        window, URLSearchParams, console,
        localStorage: {getItem() { return null; }, removeItem() {}},
        document: {createElement: tag => new Element(tag), querySelector: node, querySelectorAll: () => []}
    });
    f.form.reset = () => Object.values(f.inputs).forEach(input => { input.value = ""; });
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js", edit ? "bugs.js" : "project.js"), "utf8"), f.runtime);
    const actualLoadBugs = f.runtime.loadBugs;
    const actualShowBugMessage = f.runtime.showBugMessage;
    const stored = {id: 2, project_id: 1, bug_number: 11, title: "Stored", status: "Triage", assignee_id: null};
    for (const field of ["environment", "description", "steps_to_reproduce", "expected_result", "actual_result", "severity", "priority", "affected_version", "fix_version"]) stored[field] = null;
    if (edit) vm.runInContext(`currentBug = ${JSON.stringify(stored)}`, f.runtime);
    const messages = [], rendered = [];
    let refreshes = 0;
    Object.assign(f.runtime, {
        updateSelectPromptStyle() {}, loadBugAssignees: async () => {},
        updateBugAssigneeVisibility: async () => { f.button.hidden = false; },
        loadBugs: realListRefresh ? actualLoadBugs : async ({ silent = false } = {}) => { refreshes++; if (f.loadBugsFailure && !silent) node("#bug-message").textContent = f.loadBugsFailure; },
        loadProjectMembers: async () => true,
        isValidBugResponse: f.runtime.isValidBugResponse,
        renderBug: data => rendered.push(data.title), renderRoleSpecificActions() {},
        showBugMessage: realListRefresh ? actualShowBugMessage : (...args) => messages.push(args),
        showMessage: (target, text) => { target.textContent = text; messages.push([text]); },
        populateEditForm: () => { f.form.reset(); f.inputs[`#${prefix}title`].value = stored.title; },
        authenticatedFetch: async (url, options) => options?.method
            ? f.send(url, options) : f.loadBugsFailure
                ? {ok: false, json: async () => ({detail: f.loadBugsFailure})}
                : {ok: true, json: async () => f.serverData || stored}
    });
    const event = async (target, type) => {
        for (const handler of target.listeners[type] || []) await handler({preventDefault() {}});
    };
    const openButton = node(edit ? "#show-edit-bug-form" : "#show-bug-form");
    const cancelButton = node(edit ? "#cancel-edit-form" : "#cancel-bug-form");
    return Object.assign(f, {
        prefix, node, stored, messages, rendered, window,
        openButton, saveButton: node("#save-edit-button"),
        open: () => event(openButton, "click"), cancel: () => event(cancelButton, "click"),
        save: () => event(f.form, "submit"), refreshes: () => refreshes
    });
}

async function check_late_success_preserves_reopened_form_and_ai(edit) {
    const f = pageFixture(edit), old = deferred();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "First submission";
    f.send = () => old.promise;
    const pending = f.save();
    await f.cancel();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "Newer unsaved title";
    f.inputs[`#${f.prefix}environment`].value = "Newer environment";
    await f.submit(async () => success({title: "Newer AI title"}));
    f.serverData = {...f.stored, title: "First submission"};
    old.resolve({ok: true, json: async () => f.serverData});
    await pending;
    assert.equal(f.form.hidden, false);
    assert.equal(f.openButton.hidden, true);
    assert.equal(f.inputs[`#${f.prefix}title`].value, "Newer unsaved title");
    assert.equal(f.inputs[`#${f.prefix}environment`].value, "Newer environment");
    assert.equal(f.card("Title").all("dd")[1].textContent, "Newer AI title");
    assert.equal(f.button.disabled, true);
    if (edit) assert.ok(f.rendered.includes("First submission"), "persisted result remains visible in surrounding details");
    else assert.equal(f.refreshes(), 1, "persisted result refreshes bug list");
}


async function check_manual_save_after_ai_failure_or_no_usable_outcome(edit) {
    for (const outcome of ["http_failure", "network_failure", "no_usable"]) {
        const f = pageFixture(edit), writes = [];
        await f.open();
        f.inputs[`#${f.prefix}title`].value = "Unsaved before AI";
        f.inputs[`#${f.prefix}environment`].value = "Keep environment";
        f.inputs[`#${f.prefix}description`].value = "Keep\nmanual description";
        const before = Object.fromEntries(Object.entries(f.inputs).map(([id, input]) => [id, input.value]));
        f.send = async (url, options) => {
            writes.push({url, method: options.method, body: JSON.parse(options.body)});
            return {ok: true, json: async () => ({...f.stored, title: "Saved manually after AI"})};
        };
        await f.submit(async () => {
            if (outcome === "network_failure") throw new Error("Offline");
            if (outcome === "http_failure") return {ok: false, json: async () => ({detail: "Safe AI failure"})};
            return {ok: true, json: async () => ({outcome: "no_usable_suggestions", suggestions: {}})};
        });
        assert.equal(writes.length, 0, "AI completion must not invoke the page's Create/Save path");
        assert.deepEqual(Object.fromEntries(Object.entries(f.inputs).map(([id, input]) => [id, input.value])), before);
        assert.equal(f.form.hidden, false);
        assert.equal(f.openButton.hidden, true);
        assert.equal(f.area.hidden, true);
        assert.equal(f.button.disabled, false);
        assert.match(f.message.textContent, outcome === "no_usable" ? /No usable/ : /failure|Unable/);
        if (edit) assert.equal(f.saveButton.disabled, false);

        f.inputs[`#${f.prefix}title`].value = "Saved manually after AI";
        f.inputs[`#${f.prefix}environment`].value = "Manually revised environment";
        await f.save();
        assert.equal(writes.length, 1);
        assert.equal(writes[0].method, edit ? "PATCH" : "POST");
        assert.equal(writes[0].url, edit ? "/projects/1/bugs/11" : "/projects/1/bugs");
        assert.equal(writes[0].body.title, "Saved manually after AI");
        assert.equal(writes[0].body.environment, "Manually revised environment");
        assert.equal(writes[0].body.description, "Keep\nmanual description");
        assert.equal(f.form.hidden, true);
        assert.equal(f.openButton.hidden, false);
        assert.ok(f.messages.some(([text]) => /successfully/.test(text)));
        if (edit) assert.equal(f.saveButton.disabled, false);
    }
}

test("test_new_create_after_ai_failure_or_no_usable_outcome", async function test_new_create_after_ai_failure_or_no_usable_outcome() {
    await check_manual_save_after_ai_failure_or_no_usable_outcome(false);
});

test("test_edit_save_after_ai_failure_or_no_usable_outcome", async function test_edit_save_after_ai_failure_or_no_usable_outcome() {
    await check_manual_save_after_ai_failure_or_no_usable_outcome(true);
});


async function check_current_success_closes_form_and_discards_ai(edit) {
    const f = pageFixture(edit);
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "Current submission";
    await f.submit();
    f.send = async () => ({ok: true, json: async () => ({...f.stored, title: "Current submission"})});
    await f.save();
    assert.equal(f.form.hidden, true);
    assert.equal(f.openButton.hidden, false);
    assert.equal(f.area.hidden, true);
    assert.ok(f.messages.some(([text]) => /successfully/.test(text)));
    if (edit) assert.equal(f.saveButton.disabled, false);
    else {
        assert.equal(f.inputs[`#${f.prefix}title`].value, "");
        assert.ok(f.messages.some(([text]) => text === 'BUG-11 "Current submission" created successfully.'));
    }
}


async function check_late_error_does_not_overwrite_reopened_messages(edit) {
    const f = pageFixture(edit), old = deferred();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "First submission";
    f.send = () => old.promise;
    const pending = f.save();
    await f.cancel();
    await f.open();
    await f.submit();
    const count = f.messages.length;
    old.resolve({ok: false, json: async () => ({detail: "Old error"})});
    await pending;
    assert.equal(f.form.hidden, false);
    assert.equal(f.messages.length, count);
    assert.ok(f.card("Title"));
}


async function check_late_json_preserves_newer_pending_submission(edit) {
    const f = pageFixture(edit), json = deferred(), reading = deferred(), newer = deferred();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "First submission";
    f.send = async () => ({ok: true, json: () => { reading.resolve(); return json.promise; }});
    const old = f.save();
    await reading.promise;
    await f.cancel();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "Newer submission";
    await f.submit();
    f.send = () => newer.promise;
    const pending = f.save();
    json.resolve({...f.stored, title: "First submission"});
    await old;
    assert.equal(f.form.hidden, false);
    assert.equal(f.inputs[`#${f.prefix}title`].value, "Newer submission");
    assert.ok(f.card("Title"));
    if (edit) assert.equal(f.saveButton.disabled, true, "old finally must not unlock newer Save");
    newer.resolve({ok: true, json: async () => ({...f.stored, title: "Newer submission"})});
    await pending;
    assert.equal(f.form.hidden, true);
    if (edit) assert.equal(f.saveButton.disabled, false);
}


test("test_new_create_late_success_preserves_reopened_form_and_ai", async function test_new_create_late_success_preserves_reopened_form_and_ai() {
    await check_late_success_preserves_reopened_form_and_ai(false);
});

test("test_edit_save_late_success_preserves_reopened_form_and_ai", async function test_edit_save_late_success_preserves_reopened_form_and_ai() {
    await check_late_success_preserves_reopened_form_and_ai(true);
});

test("test_new_create_current_success_closes_form_and_discards_ai", async function test_new_create_current_success_closes_form_and_discards_ai() {
    await check_current_success_closes_form_and_discards_ai(false);
});

test("test_new_create_invalid_number_response_preserves_form", async () => {
    for (const bug_number of [undefined, null, 0, -1, 1.5, "11"]) {
        const f = pageFixture(false);
        await f.open();
        f.inputs["#bug-title"].value = "Keep unsaved report";
        f.send = async () => ({ok: true, json: async () => ({...f.stored, bug_number})});
        await f.save();
        assert.equal(f.form.hidden, false);
        assert.equal(f.inputs["#bug-title"].value, "Keep unsaved report");
        assert.equal(f.refreshes(), 0);
        assert.ok(f.messages.some(([text]) => /Invalid server response/.test(text)));
    }
});

test("test_edit_save_current_success_closes_form_and_discards_ai", async function test_edit_save_current_success_closes_form_and_discards_ai() {
    await check_current_success_closes_form_and_discards_ai(true);
});

test("test_new_create_late_error_does_not_overwrite_reopened_messages", async function test_new_create_late_error_does_not_overwrite_reopened_messages() {
    await check_late_error_does_not_overwrite_reopened_messages(false);
});

test("test_edit_save_late_error_does_not_overwrite_reopened_messages", async function test_edit_save_late_error_does_not_overwrite_reopened_messages() {
    await check_late_error_does_not_overwrite_reopened_messages(true);
});

test("test_new_create_late_json_preserves_newer_pending_submission", async function test_new_create_late_json_preserves_newer_pending_submission() {
    await check_late_json_preserves_newer_pending_submission(false);
});

test("test_edit_save_late_json_preserves_newer_pending_submission", async function test_edit_save_late_json_preserves_newer_pending_submission() {
    await check_late_json_preserves_newer_pending_submission(true);
});


test("test_edit_save_late_rejection_preserves_newer_session", async function test_edit_save_late_rejection_preserves_newer_session() {
    const f = pageFixture(true), old = deferred();
    await f.open();
    f.inputs["#edit-bug-title"].value = "First submission";
    f.send = () => old.promise;
    const pending = f.save();
    await f.cancel();
    await f.open();
    await f.submit();
    const count = f.messages.length;
    old.reject(new Error("Old transport error"));
    await pending;
    assert.equal(f.messages.length, count);
    assert.equal(f.form.hidden, false);
    assert.ok(f.card("Title"));
});

async function check_stale_create_list_refresh_failure_preserves_newer_feedback(edit) {
    const f = pageFixture(edit, {realListRefresh: true}), old = deferred();
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "First submission";
    f.send = () => old.promise;
    const pending = f.save();
    await f.cancel();
    await f.open();
    // Validation feedback belongs to the newer form session.
    f.inputs[`#${f.prefix}title`].value = "";
    const validationText = "Title must not be blank.";
    const bugMsg = f.node(edit ? "#edit-bug-message" : "#bug-message");
    bugMsg.textContent = validationText;
    assert.equal(bugMsg.textContent, validationText);
    // Old Create succeeds but its follow-up loadBugs fails.
    f.loadBugsFailure = "Unable to load bug list.";
    f.serverData = {...f.stored, title: "First submission"};
    old.resolve({ok: true, json: async () => f.serverData});
    await pending;
    // Newer validation feedback must survive.
    assert.equal(bugMsg.textContent, validationText,
        "stale list-refresh failure must not overwrite newer validation feedback");
    assert.equal(f.form.hidden, false);
    assert.equal(f.inputs[`#${f.prefix}title`].value, "");
}

test("test_new_create_stale_list_refresh_failure_preserves_newer_feedback", async function test_new_create_stale_list_refresh_failure_preserves_newer_feedback() {
    await check_stale_create_list_refresh_failure_preserves_newer_feedback(false);
});

async function check_current_create_list_refresh_failure_shows_error(edit) {
    const f = pageFixture(edit, {realListRefresh: true});
    await f.open();
    f.inputs[`#${f.prefix}title`].value = "Current submission";
    
    // Create succeeds
    f.send = async () => ({ok: true, json: async () => ({...f.stored, title: "Current submission"})});
    
    // loadBugs fails
    f.loadBugsFailure = "Unable to load bug list.";
    
    await f.save();
    
    // Form should be closed (because it was a successful create/save)
    assert.equal(f.form.hidden, true);
    assert.equal(f.openButton.hidden, false);
    
    // Because it was a current session, the loadBugs failure should still write its error
    const bugMsg = f.node(edit ? "#edit-bug-message" : "#bug-message");
    assert.equal(bugMsg.textContent, "Unable to load bug list.", 
        "normal current-session list-refresh failure must show its error");
}

test("test_new_create_current_list_refresh_failure_shows_error", async function test_new_create_current_list_refresh_failure_shows_error() {
    await check_current_create_list_refresh_failure_shows_error(false);
});

async function check_delayed_create_list_refresh_preserves_newer_session(boundary) {
    for (const ok of [false, true]) {
        const f = pageFixture(false, {realListRefresh: true});
        const started = deferred(), delayed = deferred();
        const list = [{id: 2, bug_number: 11, title: "Persisted earlier Create"}];
        const result = ok ? list : {detail: "Unable to load bug list."};
        let renders = 0;
        f.runtime.renderBugs = () => { renders++; };
        f.runtime.authenticatedFetch = async (url, options) => {
            if (options?.method) return f.send(url, options);
            assert.equal(url, "/projects/1/bugs");
            if (boundary === "response") {
                started.resolve();
                return delayed.promise;
            }
            return {ok, json: () => { started.resolve(); return delayed.promise; }};
        };

        await f.open();
        f.inputs["#bug-title"].value = "Current Create";
        await f.submit();
        f.send = async () => ({ok: true, json: async () => ({id: 2, bug_number: 11, title: "Current Create"})});
        const first = f.save();
        await started.promise;
        assert.equal(f.form.hidden, true, "current Create performs normal cleanup before refresh finishes");
        assert.equal(f.openButton.hidden, false);
        assert.equal(f.inputs["#bug-title"].value, "");
        assert.equal(f.area.hidden, true);
        assert.equal(f.button.disabled, false);
        assert.match(f.node("#bug-message").textContent, /created successfully/);

        await f.open();
        f.inputs["#bug-title"].value = "   ";
        f.inputs["#bug-environment"].value = "Newer environment";
        f.inputs["#bug-description"].value = "Newer description";
        await f.submit(async () => success({title: "Newer pending title"}));
        const aiFeedback = f.message.textContent;
        f.send = async () => ({ok: false, json: async () => ({detail: "Title must not be blank."})});
        await f.save();
        assert.equal(f.node("#bug-message").textContent, "Title must not be blank.");

        if (boundary === "response") delayed.resolve({ok, json: async () => result});
        else delayed.resolve(result);
        await first;
        assert.equal(f.node("#bug-message").textContent, "Title must not be blank.",
            "earlier refresh must not overwrite validation feedback in the newer session");
        assert.equal(f.form.hidden, false);
        assert.equal(f.openButton.hidden, true);
        assert.equal(f.inputs["#bug-title"].value, "   ");
        assert.equal(f.inputs["#bug-environment"].value, "Newer environment");
        assert.equal(f.inputs["#bug-description"].value, "Newer description");
        assert.equal(f.message.textContent, aiFeedback);
        assert.equal(f.card("Title").all("dd")[1].textContent, "Newer pending title");
        assert.equal(f.area.hidden, false);
        assert.equal(f.button.disabled, true);
        assert.equal(renders, ok ? 1 : 0);
        if (ok) assert.deepEqual(JSON.parse(vm.runInContext("JSON.stringify(projectBugs)", f.runtime)), list,
            "successful refresh may still update the surrounding persisted bug list");
    }
}

test("test_new_create_delayed_list_refresh_response_preserves_newer_session", async function test_new_create_delayed_list_refresh_response_preserves_newer_session() {
    await check_delayed_create_list_refresh_preserves_newer_session("response");
});

test("test_new_create_delayed_list_refresh_json_preserves_newer_session", async function test_new_create_delayed_list_refresh_json_preserves_newer_session() {
    await check_delayed_create_list_refresh_preserves_newer_session("json");
});
