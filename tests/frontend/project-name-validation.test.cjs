const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

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
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/projects.js"), "utf8"), runtime);
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/api-errors.js"), "utf8"), runtime);
    node("#project-form").reset = () => {};
    runtime.loadProjects = () => {};
    runtime.renderProjectView = () => {};
    let serverError = null;
    runtime.authenticatedFetch = async (url, options) => {
        requests.push({url, ...options});
        if (serverError) return {ok: false, status: serverError.status, json: async () => ({detail: serverError.detail})};
        return {ok: true, json: async () => ({id: 1, ...JSON.parse(options.body)})};
    };
    let project = {id: 1, name: "Original"};
    let editElement;
    let editInput;
    const click = selector => node(selector).click();
    return {
        node, requests,
        showPageError: text => runtime.showProjectMessage(text, "error"),
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

    test(edit ? "test_project_edit_cancel_clears_form_feedback" : "test_project_creation_cancel_clears_form_feedback", async () => {
        const page = projectPage();
        page.open(edit);
        await page.submit(edit, "");
        page.cancel(edit);
        assert.equal(page.node("#message").textContent, "");
        page.open(edit);
        assert.equal(page.node("#message").textContent, "");
    });

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
    test(edit ? "test_project_edit_blocks_blank_name_submission" : "test_project_creation_blocks_blank_name_submission", async () => {
        for (const name of ["", "   ", "\t"]) {
            const page = projectPage();
            await page.submit(edit, name);
            assert.equal(page.requests.length, 0);
            assert.equal(page.node("#message").textContent, "Project name is required.");
        }
    });

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
