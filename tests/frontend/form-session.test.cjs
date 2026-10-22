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
        openButton, saveButton: node("#save-edit-button"), createButton: node("#create-bug-button"),
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
    assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "Newer AI title");
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

// TC-289 | AC-023.2 — New create after AI failure or no usable outcome
test("test_new_create_after_ai_failure_or_no_usable_outcome", async function test_new_create_after_ai_failure_or_no_usable_outcome() {
    await check_manual_save_after_ai_failure_or_no_usable_outcome(false);
});

// TC-290 | AC-023.2 — Edit save after AI failure or no usable outcome
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
    assert.equal(f.form.all("article").length, 0, "Create/Save clears cards from every field row");
    assert.equal(f.form.classList.contains("has-ai-suggestions"), false);
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


// TC-291 | AC-020.8 — New create late success preserves reopened form and AI
test("test_new_create_late_success_preserves_reopened_form_and_ai", async function test_new_create_late_success_preserves_reopened_form_and_ai() {
    await check_late_success_preserves_reopened_form_and_ai(false);
});

// TC-292 | AC-020.8 — Edit save late success preserves reopened form and AI
test("test_edit_save_late_success_preserves_reopened_form_and_ai", async function test_edit_save_late_success_preserves_reopened_form_and_ai() {
    await check_late_success_preserves_reopened_form_and_ai(true);
});

// TC-293 | AC-020.7 — New create current success closes form and discards AI
test("test_new_create_current_success_closes_form_and_discards_ai", async function test_new_create_current_success_closes_form_and_discards_ai() {
    await check_current_success_closes_form_and_discards_ai(false);
});

// TC-294 | Technical — New create invalid number response preserves form
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

// TC-295 | AC-020.7 — Edit save current success closes form and discards AI
test("test_edit_save_current_success_closes_form_and_discards_ai", async function test_edit_save_current_success_closes_form_and_discards_ai() {
    await check_current_success_closes_form_and_discards_ai(true);
});

// TC-296 | AC-020.8 — New create late error does not overwrite reopened messages
test("test_new_create_late_error_does_not_overwrite_reopened_messages", async function test_new_create_late_error_does_not_overwrite_reopened_messages() {
    await check_late_error_does_not_overwrite_reopened_messages(false);
});

// TC-297 | AC-020.8 — Edit save late error does not overwrite reopened messages
test("test_edit_save_late_error_does_not_overwrite_reopened_messages", async function test_edit_save_late_error_does_not_overwrite_reopened_messages() {
    await check_late_error_does_not_overwrite_reopened_messages(true);
});

// TC-298 | AC-020.8 — New create late JSON preserves newer pending submission
test("test_new_create_late_json_preserves_newer_pending_submission", async function test_new_create_late_json_preserves_newer_pending_submission() {
    await check_late_json_preserves_newer_pending_submission(false);
});

// TC-299 | AC-020.8 — Edit save late JSON preserves newer pending submission
test("test_edit_save_late_json_preserves_newer_pending_submission", async function test_edit_save_late_json_preserves_newer_pending_submission() {
    await check_late_json_preserves_newer_pending_submission(true);
});


// TC-300 | AC-020.8 — Edit save late rejection preserves newer session
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

// TC-301 | AC-020.8 — New create stale list refresh failure preserves newer feedback
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

// TC-302 | AC-020.7 — New create current list refresh failure shows error
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
        assert.equal(f.card("Title").querySelector(".ai-suggestion-value").textContent, "Newer pending title");
        assert.equal(f.area.hidden, false);
        assert.equal(f.button.disabled, true);
        assert.equal(renders, ok ? 1 : 0);
        if (ok) assert.deepEqual(JSON.parse(vm.runInContext("JSON.stringify(projectBugs)", f.runtime)), list,
            "successful refresh may still update the surrounding persisted bug list");
    }
}

// TC-303 | AC-020.8 — New create delayed list refresh response preserves newer session
test("test_new_create_delayed_list_refresh_response_preserves_newer_session", async function test_new_create_delayed_list_refresh_response_preserves_newer_session() {
    await check_delayed_create_list_refresh_preserves_newer_session("response");
});

// TC-304 | AC-020.8 — New create delayed list refresh JSON preserves newer session
test("test_new_create_delayed_list_refresh_json_preserves_newer_session", async function test_new_create_delayed_list_refresh_json_preserves_newer_session() {
    await check_delayed_create_list_refresh_preserves_newer_session("json");
});

// TC-393 | Technical — New create repeated submission sends one POST while pending (BUG-37)
test("test_new_create_repeated_submission_sends_one_post_while_pending", async () => {
    const f = pageFixture(false), pending = deferred(), writes = [];
    await f.open();
    assert.equal(f.createButton.disabled, false);
    f.inputs["#bug-title"].value = "Single submission";
    f.send = (url, options) => { writes.push({url, method: options.method}); return pending.promise; };
    // Double-click and repeated Enter before the first response arrives.
    const saves = [f.save(), f.save(), f.save(), f.save()];
    assert.deepEqual(writes, [{url: "/projects/1/bugs", method: "POST"}], "only the first Create reaches the server");
    assert.equal(f.createButton.disabled, true, "Create stays unavailable while the request is pending");
    assert.equal(f.form.hidden, false);

    pending.resolve({ok: true, json: async () => ({...f.stored, title: "Single submission"})});
    await Promise.all(saves);
    assert.equal(writes.length, 1);
    assert.equal(f.form.hidden, true);
    assert.equal(f.refreshes(), 1);
    assert.equal(f.messages.filter(([text]) => /created successfully/.test(text)).length, 1);

    await f.open();
    assert.equal(f.createButton.disabled, false, "a newly opened form can create again");
});

// TC-394 | Technical — New create failure re-enables Create for retry (BUG-37)
test("test_new_create_failure_reenables_create_for_retry", async () => {
    for (const failure of ["http_error", "invalid_json", "network_error"]) {
        const f = pageFixture(false), pending = deferred(), titles = [];
        await f.open();
        f.inputs["#bug-title"].value = "Retry after failure";
        f.send = (url, options) => { titles.push(JSON.parse(options.body).title); return pending.promise; };
        const first = f.save();
        assert.equal(f.createButton.disabled, true);
        if (failure === "network_error") pending.reject(new Error("Offline"));
        else if (failure === "invalid_json") pending.resolve({ok: false, json: async () => { throw new SyntaxError("Unexpected token <"); }});
        else pending.resolve({ok: false, json: async () => ({detail: "Bug title is required."})});
        await first;
        assert.equal(f.createButton.disabled, false, `${failure} allows another submission`);
        assert.equal(f.form.hidden, false);
        assert.equal(f.inputs["#bug-title"].value, "Retry after failure");
        assert.match(f.messages.at(-1)[0], failure === "http_error" ? /Bug title is required/ : /Unable to create bug/);
        assert.equal(f.refreshes(), 0);

        f.send = async (url, options) => {
            titles.push(JSON.parse(options.body).title);
            return {ok: true, json: async () => ({...f.stored, title: "Retry after failure"})};
        };
        await f.save();
        assert.deepEqual(titles, ["Retry after failure", "Retry after failure"]);
        assert.equal(f.form.hidden, true);
    }
});

// TC-395 | Technical — Late Create completion does not unlock or close a reopened form (BUG-37)
test("test_new_create_late_completion_keeps_reopened_create_guard", async () => {
    for (const outcome of ["success", "error", "rejection"]) {
        const f = pageFixture(false), old = deferred(), newer = deferred(), titles = [];
        await f.open();
        f.inputs["#bug-title"].value = "First submission";
        f.send = (url, options) => { titles.push(JSON.parse(options.body).title); return old.promise; };
        const oldSave = f.save();
        assert.equal(f.createButton.disabled, true);
        await f.cancel();
        assert.equal(f.createButton.disabled, false, "Cancel ends the abandoned session's guard");
        await f.open();
        assert.equal(f.createButton.disabled, false, "a reopened form can submit");

        f.inputs["#bug-title"].value = "Newer submission";
        f.send = (url, options) => { titles.push(JSON.parse(options.body).title); return newer.promise; };
        const newerSaves = [f.save(), f.save()];
        assert.deepEqual(titles, ["First submission", "Newer submission"], "the newer session is guarded too");

        const count = f.messages.length;
        if (outcome === "rejection") old.reject(new Error("Old transport error"));
        else if (outcome === "error") old.resolve({ok: false, json: async () => ({detail: "Old error"})});
        else old.resolve({ok: true, json: async () => ({...f.stored, title: "First submission"})});
        await oldSave;
        assert.equal(f.createButton.disabled, true, `late ${outcome} must not unlock the newer pending Create`);
        assert.equal(f.form.hidden, false);
        assert.equal(f.inputs["#bug-title"].value, "Newer submission");
        assert.equal(f.messages.length, count, `late ${outcome} writes no feedback`);

        newer.resolve({ok: true, json: async () => ({...f.stored, title: "Newer submission"})});
        await Promise.all(newerSaves);
        assert.equal(f.form.hidden, true);
        assert.equal(titles.length, 2);
        await f.open();
        assert.equal(f.createButton.disabled, false);
    }
});

// Add Member runs in the same project page; reuse the New Bug page fixture.
function memberFixture() {
    const f = pageFixture(false);
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/api-errors.js"), "utf8"), f.runtime);
    const form = f.node("#member-form"), email = f.node("#member-email"), role = f.node("#member-role");
    form.reset = () => { email.value = ""; role.value = "QA Analyst"; };
    let memberRefreshes = 0;
    f.runtime.loadMembers = async () => { memberRefreshes++; };
    const posts = [];
    const respond = (status, body) => ({ok: status < 400, status, json: async () => body});
    return Object.assign(f, {
        email, role, posts, respond,
        addButton: f.node("#add-member-button"),
        memberMessage: f.node("#member-message"),
        memberForm: form,
        memberRefreshes: () => memberRefreshes,
        openMember: () => f.node("#show-member-form").click(),
        cancelMember: () => f.node("#cancel-member-form").click(),
        // A real click or Enter dispatches submit; the page has one submit handler.
        addMember(value, selectedRole = "QA Analyst") {
            email.value = value;
            role.value = selectedRole;
            const [handler] = form.listeners.submit;
            return handler({preventDefault() {}});
        },
        reply(handle) {
            f.send = (url, options) => {
                posts.push({url, method: options.method, ...JSON.parse(options.body)});
                return handle();
            };
        }
    });
}

// TC-400 | Technical — Add member repeated submission sends one POST while pending
test("test_add_member_repeated_submission_sends_one_post_while_pending", async () => {
    const f = memberFixture(), pending = deferred();
    f.openMember();
    assert.equal(f.addButton.disabled, false);
    f.reply(() => pending.promise);
    // Double-click and repeated Enter before the first response arrives.
    const submits = [1, 2, 3, 4].map(() => f.addMember("qa@example.com"));
    assert.deepEqual(f.posts, [{url: "/projects/1/members", method: "POST", email: "qa@example.com", role: "QA Analyst"}],
        "only the first Add reaches the server");
    assert.equal(f.addButton.disabled, true, "Add stays unavailable while the request is pending");

    pending.resolve(f.respond(201, {project_id: 1, user_id: 7, email: "qa@example.com", role: "QA Analyst"}));
    await Promise.all(submits);
    assert.equal(f.posts.length, 1);
    assert.equal(f.memberMessage.textContent, 'Member "qa@example.com" (QA Analyst) added successfully.',
        "no 409 from requests that were never needed");
    assert.equal(f.memberForm.hidden, true);
    assert.equal(f.memberRefreshes(), 1);
    assert.equal(f.refreshes(), 1, "bug list refreshes once");
    assert.equal(f.addButton.disabled, false);
});

// TC-401 | Technical — Add member failure re-enables Add for correction and retry
test("test_add_member_failure_reenables_add_for_retry", async () => {
    for (const [failure, expected] of [
        ["conflict", "This user is already a member of this project."],
        ["not_found", "User not found."],
        ["invalid_json", "Request failed. Please try again."],
        ["network_error", "Unable to add member. Please try again."]
    ]) {
        const f = memberFixture(), pending = deferred();
        f.openMember();
        f.reply(() => pending.promise);
        const first = f.addMember("missing@example.com", "Developer");
        assert.equal(f.addButton.disabled, true);
        if (failure === "network_error") pending.reject(new Error("Offline"));
        else if (failure === "invalid_json") pending.resolve({ok: false, status: 500, json: async () => { throw new SyntaxError("Unexpected token <"); }});
        else pending.resolve(f.respond(failure === "conflict" ? 409 : 404, {detail: expected}));
        await first;
        assert.equal(f.addButton.disabled, false, `${failure} allows another submission`);
        assert.equal(f.memberMessage.textContent, expected, `${failure} feedback is shown, not hidden`);
        assert.equal(f.memberForm.hidden, false);
        assert.equal(f.email.value, "missing@example.com");
        assert.equal(f.role.value, "Developer");
        assert.equal(f.memberRefreshes(), 0);

        f.reply(async () => f.respond(201, {project_id: 1, user_id: 8, email: "dev@example.com", role: "Developer"}));
        await f.addMember("dev@example.com", "Developer");
        assert.deepEqual(f.posts.map(post => post.email), ["missing@example.com", "dev@example.com"]);
        assert.equal(f.memberMessage.textContent, 'Member "dev@example.com" (Developer) added successfully.');
        assert.equal(f.memberForm.hidden, true);
        assert.equal(f.memberRefreshes(), 1);
    }
});

// TC-402 | Technical — Late Add Member completion does not affect a reopened form
test("test_add_member_late_completion_keeps_reopened_form", async () => {
    for (const outcome of ["success", "conflict", "rejection"]) {
        const f = memberFixture(), old = deferred(), newer = deferred();
        f.openMember();
        f.reply(() => old.promise);
        const oldAdd = f.addMember("first@example.com");
        f.cancelMember();
        assert.equal(f.addButton.disabled, false, "Cancel ends the abandoned interaction's guard");
        f.openMember();
        assert.equal(f.addButton.disabled, false);

        f.reply(() => newer.promise);
        const newerAdds = [f.addMember("newer@example.com", "Developer"), f.addMember("newer@example.com", "Developer")];
        assert.deepEqual(f.posts.map(post => post.email), ["first@example.com", "newer@example.com"],
            "the newer interaction is guarded too");
        f.memberMessage.textContent = "Newer feedback";

        if (outcome === "rejection") old.reject(new Error("Old transport error"));
        else if (outcome === "conflict") old.resolve(f.respond(409, {detail: "This user is already a member of this project."}));
        else old.resolve(f.respond(201, {project_id: 1, user_id: 7, email: "first@example.com", role: "QA Analyst"}));
        await oldAdd;
        assert.equal(f.addButton.disabled, true, `late ${outcome} must not unlock the newer pending Add`);
        assert.equal(f.memberForm.hidden, false, `late ${outcome} must not close the newer form`);
        assert.equal(f.email.value, "newer@example.com");
        assert.equal(f.memberMessage.textContent, "Newer feedback", `late ${outcome} writes no feedback`);
        assert.equal(f.memberRefreshes(), outcome === "success" ? 1 : 0, "a late added member still refreshes the list");

        newer.resolve(f.respond(201, {project_id: 1, user_id: 8, email: "newer@example.com", role: "Developer"}));
        await Promise.all(newerAdds);
        assert.equal(f.memberForm.hidden, true);
        assert.equal(f.memberMessage.textContent, 'Member "newer@example.com" (Developer) added successfully.');
        assert.equal(f.addButton.disabled, false);
    }
});
