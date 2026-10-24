const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const scripts = path.join(__dirname, "../../frontend/js");
const credentials = {email: "new.tester@example.com", password: "TestPassword123!"};
const reply = (status, body) => ({ok: status < 400, status, json: async () => body});

function registerPage(responses) {
    const classes = new Set();
    const message = {
        textContent: "",
        children: [],
        classList: {add: name => classes.add(name), remove: (...names) => names.forEach(name => classes.delete(name))},
        append(...children) { this.children.push(...children); }
    };
    const nodes = {
        "#register-form": {listeners: [], addEventListener(type, handler) { this.listeners.push(handler); }},
        "#email": {value: credentials.email},
        "#password": {value: credentials.password},
        "#register-form button[type='submit']": {disabled: false},
        "#message": message
    };
    const state = {requests: [], stored: [], destination: null};
    const runtime = vm.createContext({
        document: {querySelector: selector => nodes[selector], createElement: () => ({})},
        localStorage: {setItem: (key, value) => state.stored.push([key, value])},
        window: {location: {replace: url => { state.destination = url; }}, addEventListener() {}},
        fetch: async (url, options) => {
            state.requests.push([url, JSON.parse(options.body)]);
            const next = responses[url].shift();
            if (next instanceof Error) throw next;
            return typeof next === "function" ? next() : next;
        }
    });
    for (const script of ["api-errors.js", "register.js"]) {
        vm.runInContext(fs.readFileSync(path.join(scripts, script), "utf8"), runtime, {filename: script});
    }
    const submit = () => nodes["#register-form"].listeners[0]({preventDefault() {}});
    return {state, message, classes, button: nodes["#register-form button[type='submit']"], submit};
}

// TC-419 | AC-001.1, AC-002.1 — Registration logs in through /login once and opens Projects
test("test_successful_registration_logs_in_and_opens_projects_once", async () => {
    let finishRegistration;
    const page = registerPage({
        "/register": [() => new Promise(resolve => { finishRegistration = resolve; })],
        "/login": [reply(200, {access_token: "new.user.token", token_type: "bearer"})]
    });
    const first = page.submit();
    assert.equal(page.button.disabled, true);
    await page.submit();
    finishRegistration(reply(201, {message: "User registered successfully."}));
    await first;
    assert.deepEqual(page.state.requests, [["/register", credentials], ["/login", credentials]]);
    assert.deepEqual(page.state.stored, [["access_token", "new.user.token"]]);
    assert.equal(page.state.destination, "/projects.html");
    assert.equal(page.button.disabled, true);
    assert.doesNotMatch(page.message.textContent, /new\.user\.token|TestPassword123!/);
});

// TC-420 | AC-001.2, AC-001.3, AC-001.4 — Rejected registration never authenticates or redirects
test("test_rejected_registration_does_not_authenticate", async () => {
    const rejections = [
        [reply(409, {detail: "Email already registered."}), "Email already registered."],
        [reply(422, {detail: [{msg: "value is not a valid email address"}]}), "value is not a valid email address"],
        [reply(422, {detail: [{msg: "Password must contain at least one number."}]}),
            "Password must contain at least one number."],
        [new TypeError("Failed to fetch"), "Unable to connect to the server. Please try again."]
    ];
    for (const [response, expected] of rejections) {
        const page = registerPage({"/register": [response], "/login": []});
        await page.submit();
        assert.deepEqual(page.state.requests.map(([url]) => url), ["/register"]);
        assert.deepEqual(page.state.stored, []);
        assert.equal(page.state.destination, null);
        assert.equal(page.message.textContent, expected);
        assert.deepEqual([...page.classes], ["message-error"]);
        assert.equal(page.button.disabled, false);
    }
});

// TC-421 | AC-001.1 — Login failure after registration reports the created account and directs to login
test("test_login_failure_after_registration_directs_to_manual_login", async () => {
    for (const failure of [reply(401, {detail: "Invalid email or password."}), reply(200, {}),
        new TypeError("Failed to fetch")]) {
        const page = registerPage({"/register": [reply(201, {message: "User registered successfully."})], "/login": [failure]});
        await page.submit();
        assert.deepEqual(page.state.requests.map(([url]) => url), ["/register", "/login"]);
        assert.deepEqual(page.state.stored, []);
        assert.equal(page.state.destination, null);
        assert.equal(page.message.textContent,
            "Your account was created, but automatic login failed. Please log in to continue.");
        assert.deepEqual([...page.classes], []);
        assert.deepEqual(page.message.children, [" ", {href: "/login.html", textContent: "Go to Login"}]);
        // The account exists, so resubmitting would only produce a duplicate-email error.
        assert.equal(page.button.disabled, true);
    }
});
