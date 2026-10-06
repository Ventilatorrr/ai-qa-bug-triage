const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");

function projectPage() {
    const nodes = new Map();
    const node = selector => {
        if (!nodes.has(selector)) nodes.set(selector, new Element());
        return nodes.get(selector);
    };
    const requests = [];
    const runtime = vm.createContext({
        document: {querySelector: node},
        localStorage: {getItem: () => "test-token"},
        window: {location: {replace() {}}, addEventListener() {}},
        fetch: async () => ({ok: true, json: async () => []}),
        console
    });
    vm.runInContext(fs.readFileSync(path.join(__dirname, "../../frontend/js/projects.js"), "utf8"), runtime);
    node("#project-form").reset = () => {};
    runtime.loadProjects = () => {};
    runtime.renderProjectView = () => {};
    runtime.authenticatedFetch = async (url, options) => {
        requests.push({url, ...options});
        return {ok: true, json: async () => ({id: 1, ...JSON.parse(options.body)})};
    };
    return {
        node, requests,
        async submit(edit, name) {
            if (edit) {
                await runtime.saveProjectEdit({id: 1, name: "Original"}, {value: name}, new Element());
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
