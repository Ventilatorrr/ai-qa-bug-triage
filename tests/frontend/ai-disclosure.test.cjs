const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {Element} = require("./helpers/ai-fixture.cjs");
const root = path.join(__dirname, "../../frontend");
const source = fs.readFileSync(path.join(root, "js/ai-notice.js"), "utf8");
const preferenceKey = "ai-data-sharing-notice-dismissed";
const disclosure = "AI Assist sends the current bug, up to five recently updated bugs from this project, and eligible assignee information to OpenAI. Avoid passwords, API keys, and sensitive personal information. For more information, see the Privacy Policy.";

function noticeFixture(prefix = "new-bug", stored = new Map(), blocked = false) {
    const notice = new Element("div"), text = new Element("p");
    const button = new Element("button"), dismiss = new Element("button");
    notice.dataset = {aiButton: `${prefix}-ai-assist`};
    text.id = `${prefix}-ai-disclosure-text`;
    dismiss.className = "ai-notice-dismiss";
    notice.appendChild(text);
    notice.appendChild(dismiss);
    notice.hidden = true;
    button.getAttribute = name => button.attributes[name] || null;
    button.removeAttribute = name => { delete button.attributes[name]; };
    const listeners = {}, observers = [];
    vm.runInNewContext(source, {
        document: {querySelectorAll: () => [notice], getElementById: id => { assert.equal(id, notice.dataset.aiButton); return button; }},
        window: {addEventListener: (type, callback) => { listeners[type] = callback; }},
        localStorage: {
            getItem: key => { if (blocked) throw new Error("blocked"); return stored.get(key) || null; },
            setItem: (key, value) => { if (blocked) throw new Error("blocked"); stored.set(key, value); }
        },
        MutationObserver: class {
            constructor(callback) { observers.push(callback); }
            observe(target, options) { assert.equal(target, button); assert.deepEqual(Array.from(options.attributeFilter), ["hidden"]); }
        }
    });
    return {notice, text, button, dismiss, stored, listeners, availability: hidden => { button.hidden = hidden; observers.forEach(callback => callback()); }};
}

for (const [mode, page, formId, prefix] of [
    ["new", "project.html", "bug-form", "new-bug"],
    ["edit", "bugs.html", "edit-bug-form", "edit-bug"]
]) {
    // TC-252, TC-253 | AC-022.2 — Verify separately registered form variants
    test(`test_${mode}_bug_ai_disclosure_is_near_and_describes_ai_assist`, () => {
        const html = fs.readFileSync(path.join(root, page), "utf8");
        const form = html.match(new RegExp(`<form\\b[^>]*id="${formId}"[^>]*>[\\s\\S]*?</form>`))[0];
        const notice = form.match(new RegExp(`<div\\b[^>]*id="${prefix}-ai-disclosure"[^>]*>[\\s\\S]*?</div>`));
        assert.ok(notice);
        const noticeText = notice[0].match(/<p\b[^>]*>([\s\S]*?)<\/p>/)[1];
        assert.equal(noticeText.replace(/<[^>]+>/g, ""), disclosure);
        assert.equal((noticeText.match(/<a\b/g) || []).length, 1, "only Privacy Policy is linked");
        assert.match(notice[0], /role="note"/);
        assert.match(notice[0], new RegExp(`data-ai-button="${prefix}-ai-assist"`));
        assert.match(notice[0], new RegExp(`<p id="${prefix}-ai-disclosure-text">`));
        assert.match(notice[0], /href="\/privacy.html">Privacy Policy<\/a>/);
        assert.match(notice[0], /<button[^>]*type="button"[^>]*aria-label="Dismiss AI data-sharing notice"/);
        assert.doesNotMatch(notice[0], /role="(?:alert|status)"/);
        const button = form.match(new RegExp(`<button\\b[^>]*id="${prefix}-ai-assist"[^>]*>`))[0];
        assert.doesNotMatch(button, /aria-describedby=/, "hidden initial notice must not describe AI Assist");
        assert.match(form.slice(notice.index + notice[0].length, form.indexOf(button)), /^\s*<div class="form-actions creation-form-actions">\s*$/);
        assert.match(html, /<script src="js\/ai-notice.js"><\/script>/);
    });
}

// TC-254 | AC-022.2 — AI notice availability and dismissal update accessible description
test("test_ai_notice_availability_and_dismissal_update_accessible_description", () => {
    for (const prefix of ["new-bug", "edit-bug"]) {
        const f = noticeFixture(prefix);
        assert.equal(f.notice.hidden, false);
        assert.equal(f.button.getAttribute("aria-describedby"), f.text.id);
        f.button.setAttribute("aria-describedby", `other-help ${f.text.id}`);
        f.availability(true);
        assert.equal(f.notice.hidden, true);
        assert.equal(f.button.getAttribute("aria-describedby"), "other-help");
        f.availability(false);
        assert.equal(f.notice.hidden, false);
        assert.equal(f.button.getAttribute("aria-describedby"), `other-help ${f.text.id}`);
        f.dismiss.click();
        assert.equal(f.notice.hidden, true);
        assert.equal(f.button.getAttribute("aria-describedby"), "other-help");
        assert.equal(f.button.focused, true);
        assert.equal(f.stored.get(preferenceKey), "1");
    }
});

// TC-255 | AC-022.2 — AI notice dismissal persists across new edit and reload
test("test_ai_notice_dismissal_persists_across_new_edit_and_reload", () => {
    for (const [first, second] of [["new-bug", "edit-bug"], ["edit-bug", "new-bug"]]) {
        const stored = new Map([["theme", "light"], ["access_token", "synthetic-fixture-token"]]);
        noticeFixture(first, stored).dismiss.click();
        for (const prefix of [first, second, first]) {
            const next = noticeFixture(prefix, stored);
            next.availability(true);
            next.availability(false);
            assert.equal(next.notice.hidden, true);
            assert.equal(next.button.getAttribute("aria-describedby"), null);
        }
        assert.equal(stored.get("theme"), "light");
        assert.equal(stored.get("access_token"), "synthetic-fixture-token");
    }
});

// TC-256 | AC-022.2 — AI notice dismissal preserves focus during AI loading or review
test("test_ai_notice_dismissal_preserves_focus_during_ai_loading_or_review", () => {
    for (const pending of [false, true]) {
        const f = noticeFixture();
        const next = new Element("button");
        f.button.disabled = true;
        f.button.form = {querySelector: selector => selector.includes("ai-suggestions-footer") && !pending ? null : next};
        f.dismiss.click();
        assert.equal(f.notice.hidden, true);
        assert.equal(next.focused, true);
        assert.equal(f.button.disabled, true, "dismissal must not unlock AI Assist");
    }
});

// TC-257 | AC-022.2 — AI notice restores preference on cached navigation and storage events
test("test_ai_notice_restores_preference_on_cached_navigation_and_storage_events", () => {
    const f = noticeFixture();
    f.stored.set(preferenceKey, "1");
    f.listeners.pageshow({persisted: true});
    assert.equal(f.notice.hidden, true);
    f.stored.delete(preferenceKey);
    f.listeners.storage({key: "theme"});
    assert.equal(f.notice.hidden, true, "unrelated preferences must not change the notice");
    f.listeners.storage({key: null});
    assert.equal(f.notice.hidden, false);
    f.stored.set(preferenceKey, "1");
    f.listeners.storage({key: preferenceKey});
    assert.equal(f.notice.hidden, true);
    assert.equal(f.button.getAttribute("aria-describedby"), null);
});

// TC-258 | AC-022.2 — AI notice storage failure still allows in page dismissal
test("test_ai_notice_storage_failure_still_allows_in_page_dismissal", () => {
    const f = noticeFixture("edit-bug", new Map(), true);
    assert.equal(f.notice.hidden, false);
    f.dismiss.click();
    f.listeners.pageshow({persisted: true});
    f.availability(true);
    f.availability(false);
    assert.equal(f.notice.hidden, true);
    assert.equal(f.button.getAttribute("aria-describedby"), null);
    assert.equal(noticeFixture("edit-bug", new Map(), true).notice.hidden, false, "unavailable storage cannot promise persistence");
});

// TC-259 | Technical — Privacy policy links cover all page footers
test("test_privacy_policy_links_cover_all_page_footers", () => {
    for (const page of fs.readdirSync(root).filter(name => name.endsWith(".html"))) {
        const html = fs.readFileSync(path.join(root, page), "utf8");
        const footer = html.match(/<footer>[\s\S]*?<\/footer>/);
        assert.ok(footer, `${page}: footer missing`);
        assert.match(footer[0], /href="\/privacy.html">Privacy Policy<\/a>/, `${page}: policy link missing`);
    }
    const privacy = fs.readFileSync(path.join(root, "privacy.html"), "utf8");
    assert.match(privacy, /<html lang="en">/);
    assert.match(privacy, /Last updated/);
    assert.match(privacy, /<script src="js\/theme.js">/);
    assert.match(privacy, /<script src="js\/logout.js">/);
    assert.doesNotMatch(privacy, /js\/(?:project|projects|bugs|login|register)\.js|http-equiv="refresh"/);
});

// TC-260 | Technical — Registration subtitle links only privacy without extra paragraphs
test("test_registration_subtitle_links_only_privacy_without_extra_paragraphs", () => {
    const html = fs.readFileSync(path.join(root, "register.html"), "utf8");
    const main = html.match(/<main>[\s\S]*?<\/main>/)[0];
    assert.match(main, /<h2>Register<\/h2>/);
    assert.equal((main.match(/<p[^>]*class="page-description"/g) || []).length, 1);
    assert.match(main, /<p id="register-description" class="page-description">\s*Create an account &middot; <a href="\/privacy.html">Privacy Policy<\/a>\s*<\/p>\s*<form id="register-form">/);
    assert.equal((html.match(/href="\/privacy.html"/g) || []).length, 2, "subtitle and footer both link to the policy");
});

// TC-261 | Technical — About navigation preserves guest and authenticated controls
test("test_about_navigation_preserves_guest_and_authenticated_controls", () => {
    const about = fs.readFileSync(path.join(root, "about.html"), "utf8");
    assert.doesNotMatch(about, /href="\/about.html"/);
    assert.match(about, /id="about-project-navigation"[^>]*hidden/);
    for (const signedIn of [false, true]) {
        for (const aboutPage of [false, true]) {
            const guest = new Element("nav"), logout = new Element("button"), projects = new Element("a");
            const navigation = aboutPage ? new Element("nav") : null;
            vm.runInNewContext(fs.readFileSync(path.join(root, "js/logout.js"), "utf8"), {
                localStorage: {getItem: () => signedIn ? "synthetic-navigation-fixture" : null},
                document: {querySelector: selector => ({"#guest-account-actions": guest, "#logout-button": logout, "#about-projects-link": projects, "#about-project-navigation": navigation})[selector]}
            });
            assert.equal(guest.hidden, signedIn);
            assert.equal(logout.hidden, !signedIn);
            assert.equal(projects.hidden, !signedIn);
            if (navigation) assert.equal(navigation.hidden, !signedIn);
        }
    }
    const privacy = fs.readFileSync(path.join(root, "privacy.html"), "utf8");
    assert.match(privacy, /href="\/about.html">About<\/a>/);
});
