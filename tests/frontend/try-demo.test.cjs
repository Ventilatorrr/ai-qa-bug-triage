const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");
const {loadPageScript} = require("./helpers/page-script.cjs");

const scripts = path.join(__dirname, "../../frontend/js");
const reply = (status, body) => ({ok: status < 400, status, json: async () => body});
const failureMessage = "The Demo could not be created. Please try again.";

function loginPage(responses, existingToken = null) {
    const classes = new Set();
    const listeners = {};
    const control = name => ({addEventListener(type, handler) { listeners[name] = handler; }});
    const attributes = {};
    const demoButton = {
        ...control("demo"), disabled: false, textContent: "Try Demo", attributes,
        setAttribute: (name, value) => { attributes[name] = value; },
        removeAttribute: name => { delete attributes[name]; }
    };
    const statusClasses = new Set();
    const nodes = {
        "#login-form": control("login"),
        "#email": {value: ""},
        "#password": {value: ""},
        "#message": {textContent: "", classList: {add: name => classes.add(name), remove: (...names) => names.forEach(name => classes.delete(name))}},
        "#try-demo": demoButton,
        "#demo-status": {textContent: "", classList: {toggle: (name, on) => on ? statusClasses.add(name) : statusClasses.delete(name)}}
    };
    const state = {requests: [], stored: [], destination: null};
    const runtime = vm.createContext({
        document: {querySelector: selector => nodes[selector]},
        localStorage: {
            getItem: key => key === "access_token" ? existingToken : null,
            setItem: (key, value) => state.stored.push([key, value])
        },
        window: {location: {replace: url => { state.destination = url; }}, addEventListener() {}},
        fetch: async (url, options) => {
            state.requests.push({url, ...options});
            const next = responses.shift();
            if (next instanceof Error) throw next;
            return typeof next === "function" ? next() : next;
        }
    });
    for (const script of ["api-errors.js", "login.js"]) {
        vm.runInContext(fs.readFileSync(path.join(scripts, script), "utf8"), runtime, {filename: script});
    }
    return {state, classes, statusClasses, demoButton, message: nodes["#message"], status: nodes["#demo-status"], clickDemo: () => listeners.demo()};
}

// TC-450 | AC-024.1 — Try Demo signs in through the returned token once and opens Projects
test("test_try_demo_signs_in_once_and_opens_projects", async () => {
    let finish;
    const page = loginPage([() => new Promise(resolve => { finish = resolve; })]);
    const first = page.clickDemo();
    assert.equal(page.demoButton.disabled, true);
    assert.equal(page.demoButton.textContent, "Creating Demo...");
    assert.equal(page.demoButton.attributes["aria-busy"], "true");
    // Progress is shown on the button itself, not as a separate page message.
    assert.equal(page.message.textContent, "");
    assert.equal(page.status.textContent, "");
    await page.clickDemo();  // A second click while pending sends nothing.
    finish(reply(201, {access_token: "demo.owner.token", token_type: "bearer"}));
    await first;
    assert.deepEqual(page.state.requests, [{url: "/demo", method: "POST"}]);  // No credentials or body.
    assert.deepEqual(page.state.stored, [["access_token", "demo.owner.token"]]);
    assert.equal(page.state.destination, "/projects.html");
    assert.equal(page.demoButton.disabled, true);  // Stays disabled while navigating.
    assert.doesNotMatch(page.message.textContent, /demo\.owner\.token/);
});

// TC-451 | AC-024.1, AC-024.8 — Failed Try Demo keeps the visitor signed out on Login and allows retry
test("test_failed_try_demo_shows_error_and_allows_retry", async () => {
    const page = loginPage([
        reply(500, {detail: failureMessage}),
        new Error("Network down"),
        {ok: false, status: 502, json: async () => { throw new Error("Not JSON"); }},
        reply(201, {access_token: "retry.token", token_type: "bearer"})
    ]);
    for (let attempt = 0; attempt < 3; attempt++) {
        await page.clickDemo();
        // The error appears in the status line under the button; the Login message stays empty.
        assert.equal(page.status.textContent, failureMessage);
        assert.equal(page.statusClasses.has("message-error"), true);
        assert.equal(page.message.textContent, "");
        assert.equal("aria-busy" in page.demoButton.attributes, false);
        assert.deepEqual(page.state.stored, []);
        assert.equal(page.state.destination, null);
        assert.equal(page.demoButton.disabled, false);
        assert.equal(page.demoButton.textContent, "Try Demo");
    }
    await page.clickDemo();
    assert.deepEqual(page.state.stored, [["access_token", "retry.token"]]);
    assert.equal(page.state.destination, "/projects.html");
    assert.equal(page.state.requests.length, 4);
});

// TC-452, TC-462 | AC-024.3, AC-024.4 — Server-marked E-Commerce note and historical introduction visibility
test("test_demo_note_appears_only_for_demo_ecommerce_project", async () => {
    for (const [name, visible, demoKind] of [
        ["E-Commerce Demo", true, "ecommerce"], ["Renamed Shop", true, "ecommerce"],
        ["E-Commerce Demo", false], ["AI QA Bug Triage", false], ["Shop", false],
        ["AI QA Bug Triage", false, "history"], ["Renamed Demo", false, "history"],
        ["AI QA Bug Triage", false, "unrecognized"],
    ]) {
        const nodes = new Map();
        const node = selector => {
            if (!nodes.has(selector)) nodes.set(selector, new Element());
            return nodes.get(selector);
        };
        node("#bug-form").hidden = true;
        node("#demo-note").hidden = true;
        node("#demo-history-note").hidden = true;
        const window = new Element();
        window.location = {search: "?id=1", replace() {}};
        const token = `header.${Buffer.from(JSON.stringify({user_id: 1})).toString("base64")}.signature`;
        const runtime = vm.createContext({
            document: {querySelector: node, createElement: tag => new Element(tag)},
            window, URLSearchParams, atob, console, confirm: () => true,
            localStorage: {getItem: key => key === "access_token" ? token : null, setItem() {}, removeItem() {}},
            sessionStorage: {getItem: () => null, setItem() {}, removeItem() {}},
            formatApiError: detail => detail,
            fetch: async url => reply(200, url.endsWith("/members")
                ? [{user_id: 1, email: "owner@example.com", role: "Project Owner"}]
                : url.endsWith("/bugs") ? [] : {id: 1, name, demo_kind: demoKind})
        });
        loadPageScript(runtime, "project.js");
        await new Promise(resolve => setImmediate(resolve));
        assert.equal(node("#project-name").textContent, name);
        assert.equal(node("#demo-note").hidden, !visible, name);
        assert.equal(node("#demo-history-note").hidden, demoKind !== "history", name);
    }
    const html = fs.readFileSync(path.join(__dirname, "../../frontend/project.html"), "utf8");
    const note = html.match(/<p id="demo-history-note" class="page-description" hidden>([\s\S]*?)<\/p>/)[1];
    assert.equal(note.replace(/\s+/g, " ").trim(),
        "This project showcases the testing and quality assurance work behind AI QA Bug Triage.<br> It contains genuine reports of defects discovered during development.");
    assert.ok(html.indexOf('id="toggle-members"') < html.indexOf('id="demo-history-note"'));
    assert.ok(html.indexOf('id="demo-history-note"') < html.indexOf('id="show-bug-form"'));
});

// TC-457 | AC-024.1 — Login shows the Demo introduction, button and session notice together; other pages do not
test("test_login_demo_section_text_is_only_on_login", () => {
    const html = name => fs.readFileSync(path.join(__dirname, "../../frontend", name), "utf8").replace(/\s+/g, " ");
    const intro = "Explore bug tracking and AI-assisted triage with an interactive Demo. No registration required.";
    const notice = ["Demo work won't be accessible after logout or session expiry.<br>",
        '<a href="/register.html">Register an account</a> to create projects you can return to later.'];
    const section = html("login.html").match(/<div class="demo-start">(.*?)<\/div>/)[1];
    assert.ok(section.indexOf(intro) < section.indexOf('id="try-demo"'));
    // The two notice sentences follow the button on consecutive lines.
    assert.ok(section.indexOf('id="try-demo"') < section.indexOf(notice[0]));
    assert.ok(section.indexOf(notice[0]) < section.indexOf(notice[1]));
    for (const page of ["register.html", "projects.html", "project.html", "bugs.html"]) {
        assert.doesNotMatch(html(page), /Demo work won't be accessible/, page);
    }
});
