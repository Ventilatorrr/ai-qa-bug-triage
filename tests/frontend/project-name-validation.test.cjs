const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element, deferred} = require("./helpers/ai-fixture.cjs");
const {loadPageScript} = require("./helpers/page-script.cjs");

function projectPage() {
    const element = tag => {
        const value = new Element(tag);
        value.append = (...children) => children.forEach(child => value.appendChild(child));
        return value;
    };
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, element(selector === "#project-name" ? "input" : "div"));
        return nodes.get(selector);
    };
    const requests = [];
    const runtime = vm.createContext({
        document: {querySelector: node, createElement: element},
        localStorage: {getItem: () => "test-token"},
        window: {location: {replace() {}}, addEventListener() {}},
        fetch: async () => ({ok: true, json: async () => []}),
        console
    });
    loadPageScript(runtime, "projects.js");
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/api-errors.js"), "utf8"), runtime);
    node("#project-form").reset = () => {};
    const realLoadProjects = runtime.loadProjects; let refreshes = 0; runtime.loadProjects = () => { refreshes++; };
    runtime.renderProjectView = () => {};
    let serverError = null, send = null;
    runtime.authenticatedFetch = async (url, options) => {
        requests.push({url, ...options}); if (send) return send(url, options);
        if (serverError) return {ok: false, status: serverError.status, json: async () => ({detail: serverError.detail})};
        return {ok: true, json: async () => ({id: 1, ...JSON.parse(options.body)})};
    };
    let project = {id: 1, name: "Original"};
    let editElement;
    let editInput;
    const click = selector => node(selector).click();
    return {
        node, requests, runtime, realLoadProjects, createButton: node("#create-project-button"), refreshes: () => refreshes, setSend: fn => { send = fn; },
        showPageError: text => runtime.showProjectMessage(text, "error"), editRow: () => ({element: editElement, input: editInput, button: label => editElement.all("button").find(button => button.textContent === label)}),
        setServerError: (status, detail) => { serverError = {status, detail}; },
        open(edit, id = 1) {
            if (edit) {
                project = {id, name: "Original"};
                editElement = element("div");
                runtime.startProjectEdit(project, editElement);
                editInput = editElement.querySelector("input");
            } else click("#show-project-form");
        },
        cancel(edit) {
            if (edit) editElement.all("button").find(button => button.textContent === "Cancel").click();
            else click("#cancel-project-form");
        },
        input(edit, name) {
            const input = edit ? editInput : node("#project-name");
            input.value = name;
            input.dispatchEvent({type: "input", target: input});
        },
        async submit(edit, name) {
            if (edit) {
                const input = editInput || {value: name};
                input.value = name;
                await runtime.saveProjectEdit(project, input, editElement || element("div"));
            } else {
                node("#project-name").value = name;
                for (const handler of node("#project-form").listeners.submit) {
                    await handler({preventDefault() {}});
                }
            }
        }
    };
}

for (const edit of [false, true]) {
    // TC-309, TC-314 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_validation_feedback_tracks_input" : "test_project_creation_validation_feedback_tracks_input", async () => {
        for (const correction of ["QA Project", "  Pasted Project  "]) {
            const page = projectPage();
            page.open(edit);
            await page.submit(edit, "   ");
            assert.equal(page.node("#message").textContent, "Project name is required.");
            page.input(edit, "\t  ");
            assert.equal(page.node("#message").textContent, "Project name is required.");
            page.input(edit, correction);
            assert.equal(page.node("#message").textContent, "");
            assert.equal(page.requests.length, 0);
        }
    });

    // TC-310, TC-315 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_cancel_clears_form_feedback" : "test_project_creation_cancel_clears_form_feedback", async () => {
        const page = projectPage();
        page.open(edit);
        await page.submit(edit, "");
        page.cancel(edit);
        assert.equal(page.node("#message").textContent, "");
        page.open(edit);
        assert.equal(page.node("#message").textContent, "");
    });

    // TC-311, TC-316 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_open_clears_previous_form_feedback" : "test_project_creation_open_clears_previous_form_feedback", async () => {
        for (const previous of ["create-validation", "edit-validation", "create-success"]) {
            const page = projectPage();
            const priorEdit = previous === "edit-validation";
            page.open(priorEdit);
            await page.submit(priorEdit, previous === "create-success" ? "QA Project" : "");
            assert.notEqual(page.node("#message").textContent, "");
            if (previous === "create-success") assert.match(page.node("#message").textContent, /created successfully/);
            page.open(edit, 2);
            assert.equal(page.node("#message").textContent, "");
        }
    });

    // TC-312, TC-317 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_preserves_unrelated_feedback" : "test_project_creation_preserves_unrelated_feedback", async () => {
        for (const error of ["Unable to load projects.", "Network unavailable.", "Authentication required."]) {
            const page = projectPage();
            page.open(edit);
            await page.submit(edit, "");
            page.showPageError(error);
            page.input(edit, "Corrected Project");
            assert.equal(page.node("#message").textContent, error);
            await page.submit(edit, "Corrected Project");
            // Create replaces feedback with its new success; Edit should preserve the page error.
            if (edit) assert.equal(page.node("#message").textContent, error);
            page.showPageError(error);
            page.cancel(edit);
            assert.equal(page.node("#message").textContent, error);
            page.open(edit);
            assert.equal(page.node("#message").textContent, error);
        }
        for (const [status, detail] of [[503, "Service unavailable."], [403, "Not authorized."]]) {
            const page = projectPage();
            page.open(edit);
            page.setServerError(status, detail);
            await page.submit(edit, "QA Project");
            page.input(edit, "Corrected Project");
            assert.equal(page.node("#message").textContent, detail);
            page.cancel(edit);
            page.open(edit);
            assert.equal(page.node("#message").textContent, detail);
        }
    });

    // TC-313, TC-318 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_server_validation_feedback_clears_on_correction" : "test_project_creation_server_validation_feedback_clears_on_correction", async () => {
        const page = projectPage();
        page.open(edit);
        page.setServerError(422, "Project name is required.");
        await page.submit(edit, "Submitted Project");
        assert.equal(page.node("#message").textContent, "Project name is required.");
        page.input(edit, "Corrected Project");
        assert.equal(page.node("#message").textContent, "");
    });
}

// TC-319 | AC-007.3 — Project edit success clears prior validation feedback
test("test_project_edit_success_clears_prior_validation_feedback", async () => {
    const page = projectPage();
    page.open(true);
    await page.submit(true, "");
    // Save must also remove stale validation if the value changes without an input event.
    await page.submit(true, "Updated Project");
    assert.equal(page.requests.length, 1);
    assert.equal(JSON.parse(page.requests[0].body).name, "Updated Project");
    assert.equal(page.node("#message").textContent, "");
});

// TC-320 | AC-005.2, AC-007.3 — Project name input preserves other form feedback
test("test_project_name_input_preserves_other_form_feedback", async () => {
    const page = projectPage();
    page.open(true);
    page.open(false);
    await page.submit(false, "");
    page.input(true, "Corrected Edit");
    page.cancel(true);
    assert.equal(page.node("#message").textContent, "Project name is required.");
    page.input(false, "Corrected Create");
    assert.equal(page.node("#message").textContent, "");
});

for (const edit of [false, true]) {
    // TC-321, TC-323 | AC-005.2, AC-007.3 — Verify separately registered form variants
    test(edit ? "test_project_edit_blocks_blank_name_submission" : "test_project_creation_blocks_blank_name_submission", async () => {
        for (const name of ["", "   ", "\t"]) {
            const page = projectPage();
            await page.submit(edit, name);
            assert.equal(page.requests.length, 0);
            assert.equal(page.node("#message").textContent, "Project name is required.");
        }
    });

    // TC-322, TC-324 | AC-005.1, AC-007.1 — Verify separately registered form variants
    test(edit ? "test_project_edit_submits_valid_name_unchanged" : "test_project_creation_submits_valid_name_unchanged", async () => {
        for (const name of ["QA Project", "  QA Project  "]) {
            const page = projectPage();
            await page.submit(edit, name);
            assert.equal(page.requests.length, 1);
            assert.equal(page.requests[0].url, edit ? "/projects/1" : "/projects");
            assert.equal(page.requests[0].method, edit ? "PUT" : "POST");
            assert.equal(JSON.parse(page.requests[0].body).name, name);
        }
    });
}

const created = name => ({ok: true, status: 201, json: async () => ({id: 7, name})});
const tick = () => new Promise(resolve => setImmediate(resolve));

// TC-396 | Technical — New project repeated submission sends one POST while pending
test("test_new_project_repeated_submission_sends_one_post_while_pending", async () => {
    const page = projectPage(), pending = deferred();
    page.open(false);
    assert.equal(page.createButton.disabled, false);
    page.setSend(() => pending.promise);
    // Double-click and repeated Enter before the first response arrives.
    const submits = [1, 2, 3, 4].map(() => page.submit(false, "Single Project"));
    assert.equal(page.requests.length, 1, "only the first Create reaches the server");
    assert.equal(page.requests[0].method, "POST");
    assert.equal(page.createButton.disabled, true, "Create stays unavailable while the request is pending");
    assert.equal(page.node("#project-form").hidden, false);

    pending.resolve(created("Single Project"));
    await Promise.all(submits);
    assert.equal(page.requests.length, 1);
    assert.equal(page.node("#project-form").hidden, true);
    assert.equal(page.refreshes(), 1);
    assert.equal(page.node("#message").textContent, 'Project "Single Project" created successfully.');
    page.open(false);
    assert.equal(page.createButton.disabled, false);
});

// TC-397 | Technical — New project failure re-enables Create for retry
test("test_new_project_failure_reenables_create_for_retry", async () => {
    for (const failure of ["http_error", "invalid_json", "network_error"]) {
        const page = projectPage(), pending = deferred();
        page.open(false);
        page.setSend(() => pending.promise);
        const first = page.submit(false, "Retry Project");
        assert.equal(page.createButton.disabled, true);
        if (failure === "network_error") pending.reject(new Error("Offline"));
        else if (failure === "invalid_json") pending.resolve({ok: false, status: 500, json: async () => { throw new SyntaxError("Unexpected token <"); }});
        else pending.resolve({ok: false, status: 503, json: async () => ({detail: "Service unavailable."})});
        await first;
        assert.equal(page.createButton.disabled, false, `${failure} allows another submission`);
        assert.equal(page.node("#project-form").hidden, false);
        assert.equal(page.node("#project-name").value, "Retry Project");
        assert.equal(page.node("#message").textContent,
            failure === "http_error" ? "Service unavailable." : "Unable to create project. Please try again.");
        assert.equal(page.refreshes(), 0);

        page.setSend(async () => created("Retry Project"));
        await page.submit(false, "Retry Project");
        assert.equal(page.requests.filter(request => request.method === "POST").length, 2);
        assert.equal(page.node("#project-form").hidden, true);
        assert.equal(page.refreshes(), 1);
    }
});

// TC-398 | Technical — Late project Create completion does not affect a reopened form
test("test_new_project_late_completion_keeps_reopened_form", async () => {
    for (const outcome of ["success", "error", "rejection"]) {
        const page = projectPage(), old = deferred(), newer = deferred();
        page.open(false);
        page.setSend(() => old.promise);
        const oldSubmit = page.submit(false, "First Project");
        page.cancel(false);
        assert.equal(page.createButton.disabled, false, "Cancel ends the abandoned interaction's guard");
        page.open(false);
        assert.equal(page.createButton.disabled, false);

        page.setSend(() => newer.promise);
        const newerSubmits = [page.submit(false, "Newer Project"), page.submit(false, "Newer Project")];
        assert.equal(page.requests.length, 2, "the newer interaction is guarded too");
        page.showPageError("Newer feedback");

        if (outcome === "rejection") old.reject(new Error("Old transport error"));
        else if (outcome === "error") old.resolve({ok: false, status: 503, json: async () => ({detail: "Old error"})});
        else old.resolve(created("First Project"));
        await oldSubmit;
        assert.equal(page.createButton.disabled, true, `late ${outcome} must not unlock the newer pending Create`);
        assert.equal(page.node("#project-form").hidden, false, `late ${outcome} must not close the newer form`);
        assert.equal(page.node("#project-name").value, "Newer Project");
        assert.equal(page.node("#message").textContent, "Newer feedback", `late ${outcome} writes no feedback`);
        assert.equal(page.refreshes(), outcome === "success" ? 1 : 0, "a saved late project still refreshes the list");

        newer.resolve(created("Newer Project"));
        await Promise.all(newerSubmits);
        assert.equal(page.node("#project-form").hidden, true);
        assert.equal(page.node("#message").textContent, 'Project "Newer Project" created successfully.');
    }
});

// TC-399 | Technical — Overlapping project list refreshes render each project once
test("test_overlapping_project_list_refreshes_render_each_project_once", async () => {
    for (const finish of ["interleaved", "superseded_last"]) {
        const page = projectPage(), lists = [], roles = [];
        page.setSend(() => { const response = deferred(); lists.push(response); return response.promise; });
        page.runtime.getProjectRole = id => { const role = deferred(); roles.push({id, role}); return role.promise; };
        page.runtime.renderProjectView = (element, project) => { element.textContent = project.name; };
        const answer = list => ({ok: true, json: async () => list});
        // Both refreshes can wait on the same project's role: pick the older or newer request.
        const resolveRole = async (id, which = "older") => {
            for (let i = 0; i < 20 && !roles.some(entry => entry.id === id); i++) await tick();
            const matches = roles.filter(entry => entry.id === id);
            assert.ok(matches.length, `role request for project ${id}`);
            const entry = which === "newer" ? matches.at(-1) : matches[0];
            roles.splice(roles.indexOf(entry), 1);
            entry.role.resolve("Project Owner");
            await tick();
        };

        // A: an earlier refresh (initial load); B: the refresh after a successful Create.
        const a = page.realLoadProjects();
        lists[0].resolve(answer([{id: 1, name: "Alpha"}, {id: 2, name: "Beta"}]));
        await resolveRole(1);
        const b = page.realLoadProjects();
        lists[1].resolve(answer([{id: 1, name: "Alpha"}, {id: 2, name: "Beta"}, {id: 3, name: "Gamma"}]));
        if (finish === "interleaved") {
            await resolveRole(1);
            await resolveRole(2);
            await resolveRole(2);
            await resolveRole(3);
        } else {
            // B finishes first; the superseded A completes afterwards.
            await resolveRole(1);
            await resolveRole(2, "newer");
            await resolveRole(3);
            await b;
            await resolveRole(2);
        }
        await Promise.all([a, b]);
        assert.deepEqual(page.node("#projects").children.map(row => row.textContent), ["Alpha", "Beta", "Gamma"],
            `${finish}: the latest list renders once and a superseded refresh adds nothing`);
    }
});

const renamed = name => ({ok: true, status: 200, json: async () => ({id: 1, name})});
const rowLocked = row => ({
    input: row.input.readOnly,
    ...Object.fromEntries(["Delete", "Cancel", "Save"].map(label => [label, row.button(label).disabled]))
});

// TC-467 | AC-007.1 — Project edit Save locks the row and sends one PUT while pending
test("test_project_edit_save_locks_row_and_sends_one_put_while_pending", async () => {
    const page = projectPage(), pending = deferred(), views = [];
    page.runtime.renderProjectView = (element, project) => views.push(project.name);
    page.open(true);
    const row = page.editRow();
    page.setSend(() => pending.promise);
    const save = page.submit(true, "Saved Name");
    // Newer typing, Cancel/re-edit, Delete and repeated Save cannot race the pending response.
    assert.deepEqual(rowLocked(row), {input: true, Delete: true, Cancel: true, Save: true});
    row.button("Save").click();
    row.button("Save").click();
    assert.equal(page.requests.length, 1, "only the first Save reaches the server");

    pending.resolve(renamed("Saved Name"));
    await save;
    assert.equal(page.requests.length, 1);
    assert.deepEqual(views, ["Saved Name"]);
});

// TC-468 | AC-007.1 — Project edit Save failure restores the row for retry
test("test_project_edit_save_failure_restores_row_for_retry", async () => {
    for (const failure of ["http_error", "invalid_json", "network_error"]) {
        const page = projectPage(), pending = deferred(), views = [];
        page.runtime.renderProjectView = (element, project) => views.push(project.name);
        page.open(true);
        const row = page.editRow();
        page.setSend(() => pending.promise);
        const save = page.submit(true, "Retry Name");
        assert.equal(row.input.readOnly, true);
        if (failure === "network_error") pending.reject(new Error("Offline"));
        else if (failure === "invalid_json") pending.resolve({ok: false, status: 500, json: async () => { throw new SyntaxError("Unexpected token <"); }});
        else pending.resolve({ok: false, status: 503, json: async () => ({detail: "Service unavailable."})});
        await save;
        assert.deepEqual(rowLocked(row), {input: false, Delete: false, Cancel: false, Save: false}, `${failure} allows a retry`);
        assert.equal(row.input.value, "Retry Name");
        assert.equal(page.node("#message").textContent,
            failure === "http_error" ? "Service unavailable." : "Unable to save project. Please try again.");
        assert.deepEqual(views, [], `${failure} keeps the edit open`);

        page.setSend(async () => renamed("Retry Name"));
        await page.submit(true, "Retry Name");
        assert.equal(page.requests.length, 2);
        assert.deepEqual(views, ["Retry Name"]);
    }
});

// TC-469 | AC-007.1 — Late project Save does not end another project's edit session
test("test_late_project_save_keeps_other_project_edit_session", async () => {
    const page = projectPage(), pending = deferred(), views = [];
    page.runtime.renderProjectView = element => views.push(element);
    page.open(true, 1);
    const x = page.editRow();
    page.setSend(() => pending.promise);
    const save = page.submit(true, "X Renamed");
    page.open(true, 2);
    const y = page.editRow();
    page.input(true, "Y Unsaved");

    pending.resolve(renamed("X Renamed"));
    await save;
    assert.deepEqual(views, [x.element], "only project X's row leaves edit mode");
    assert.equal(y.input.value, "Y Unsaved");

    // A later list refresh must still render project Y in edit mode.
    page.runtime.getProjectRole = async () => "Project Owner";
    page.setSend(async () => ({ok: true, json: async () => [{id: 1, name: "X Renamed"}, {id: 2, name: "Original"}]}));
    await page.realLoadProjects();
    const [, refreshedY] = page.node("#projects").children;
    assert.equal(refreshedY, y.element);
    assert.equal(refreshedY.querySelector("input").value, "Y Unsaved");
});

// TC-470 | AC-007.1 — Project list refresh keeps a pending Save row locked
test("test_project_list_refresh_keeps_pending_save_row_locked", async () => {
    const page = projectPage(), pending = deferred(), views = [];
    page.runtime.renderProjectView = element => views.push(element);
    page.runtime.getProjectRole = async () => "Project Owner";
    page.open(true);
    const x = page.editRow();
    page.setSend((url, options) => options?.method === "PUT" ? pending.promise
        : {ok: true, json: async () => [{id: 1, name: "Original"}]});
    const save = page.submit(true, "Saved Name");

    // A refresh (for example after New Project) must not redraw the pending row unlocked.
    await page.realLoadProjects();
    const [refreshed] = page.node("#projects").children;
    assert.equal(refreshed, x.element, "the refreshed list keeps the pending row");
    assert.equal(refreshed.querySelector("input").readOnly, true);
    refreshed.all("button").find(button => button.textContent === "Save").click();
    assert.equal(page.requests.filter(request => request.method === "PUT").length, 1);

    pending.resolve(renamed("Saved Name"));
    await save;
    assert.deepEqual(views, [x.element], "the response settles the row shown in the list");
});

// TC-471 | AC-007.1 — Project list refresh preserves an unsaved project name edit
test("test_project_list_refresh_preserves_unsaved_project_name_edit", async () => {
    const page = projectPage();
    page.runtime.renderProjectView = (element, project) => { element.textContent = project.name; };
    page.runtime.getProjectRole = async () => "Project Owner";
    page.open(true);
    page.input(true, "Unsaved Name");

    // Creating another project refreshes the list while the rename is unsaved.
    page.setSend((url, options) => options?.method === "PUT" ? renamed(JSON.parse(options.body).name)
        : {ok: true, json: async () => [{id: 1, name: "Original"}, {id: 2, name: "New Project"}]});
    await page.realLoadProjects();
    const [edited, created] = page.node("#projects").children;
    assert.equal(edited.querySelector("input")?.value, "Unsaved Name", "the typed name survives the refresh");
    assert.equal(created.textContent, "New Project");

    edited.all("button").find(button => button.textContent === "Save").click();
    await tick();
    assert.deepEqual(page.requests.filter(request => request.method === "PUT").map(request => JSON.parse(request.body)),
        [{name: "Unsaved Name"}]);
});
