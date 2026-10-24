const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {loadAuthScript} = require("./helpers/page-script.cjs");

const root = path.join(__dirname, "../../frontend");
const encode = text => Buffer.from(text).toString("base64url");
const plain = value => JSON.parse(JSON.stringify(value));

function auth(token) {
    const state = {token, requests: [], destination: null, response: {status: 200}};
    const runtime = vm.createContext({
        atob,
        localStorage: {
            getItem: key => key === "access_token" ? state.token : null,
            removeItem: key => { if (key === "access_token") state.token = null; }
        },
        window: {location: {replace: url => { state.destination = url; }}},
        fetch: async (url, options) => { state.requests.push([url, options]); return state.response; }
    });
    loadAuthScript(runtime);
    return {runtime, state};
}

// TC-414 | AC-003.2 — Missing token redirects to login without sending a request
test("test_missing_token_redirects_to_login_without_request", async () => {
    for (const token of [null, ""]) {
        const f = auth(token);
        assert.equal(await f.runtime.authenticatedFetch("/projects"), null);
        assert.equal(f.runtime.getCurrentUserId(), null);
        assert.deepEqual(f.state.requests, []);
        assert.equal(f.state.destination, "/login.html");
    }
});

// TC-415 | Technical — Authenticated fetch adds bearer token and preserves request options
test("test_authenticated_fetch_adds_bearer_token_and_preserves_request_options", async () => {
    const f = auth("valid.token.value");
    const headers = {"Content-Type": "application/json"};
    const body = JSON.stringify({name: "Example Project"});
    for (const response of [{status: 200, ok: true}, {status: 403, ok: false}]) {
        f.state.response = response;
        assert.equal(await f.runtime.authenticatedFetch("/projects", {method: "POST", headers, body}), response);
    }
    await f.runtime.authenticatedFetch("/projects/1");
    const posted = {method: "POST", headers: {...headers, Authorization: "Bearer valid.token.value"}, body};
    assert.deepEqual(plain(f.state.requests), [
        ["/projects", posted], ["/projects", posted],
        ["/projects/1", {headers: {Authorization: "Bearer valid.token.value"}}]
    ]);
    assert.deepEqual(headers, {"Content-Type": "application/json"});
    assert.equal(f.state.token, "valid.token.value");
    assert.equal(f.state.destination, null);
});

// TC-416 | Technical — HTTP 401 clears stored token and redirects to login
test("test_unauthorized_response_clears_token_and_redirects_to_login", async () => {
    const f = auth("expired.token.value");
    f.state.response = {status: 401, ok: false};
    assert.equal(await f.runtime.authenticatedFetch("/projects/1/bugs", {method: "GET"}), null);
    assert.equal(f.state.requests.length, 1);
    assert.equal(f.state.token, null);
    assert.equal(f.state.destination, "/login.html");
});

// TC-417 | Technical — Current user ID reads JWT payload and malformed tokens yield null
test("test_current_user_id_reads_jwt_payload_and_malformed_tokens_yield_null", () => {
    const valid = `header.${encode(JSON.stringify({user_id: 7, exp: 1790000000}))}.signature`;
    assert.equal(auth(valid).runtime.getCurrentUserId(), 7);
    for (const token of ["not-a-jwt", "header.%%%.signature", `header.${encode("not json")}.signature`,
        `header.${encode("null")}.signature`]) {
        const f = auth(token);
        assert.equal(f.runtime.getCurrentUserId(), null, token);
        // The backend rejects a malformed token on the next authenticated request.
        assert.equal(f.state.token, token);
        assert.equal(f.state.destination, null);
    }
});

// TC-418 | Technical — Authenticated pages load page scripts as modules sharing auth.js
test("test_authenticated_pages_load_page_scripts_as_modules_sharing_auth", async () => {
    const source = fs.readFileSync(path.join(root, "js/auth.js"), "utf8");
    const exported = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
    assert.deepEqual(Object.keys(exported).sort(), ["authenticatedFetch", "getCurrentUserId", "redirectToLogin"]);
    const modules = [];
    for (const page of fs.readdirSync(root).filter(name => name.endsWith(".html"))) {
        const html = fs.readFileSync(path.join(root, page), "utf8");
        for (const [, script] of html.matchAll(/<script type="module" src="js\/([^"]+)"><\/script>/g)) {
            modules.push([page, script]);
        }
    }
    assert.deepEqual(modules.sort(), [["bugs.html", "bugs.js"], ["project.html", "project.js"], ["projects.html", "projects.js"]]);
    for (const [, script] of modules) {
        assert.match(fs.readFileSync(path.join(root, "js", script), "utf8"), /^import \{[^}]+\} from "\.\/auth\.js";/);
    }
});
