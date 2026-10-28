const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const frontend = path.join(__dirname, "../../frontend");

// TC-493 | AC-009.1, AC-009.2, AC-011.1 — Project page status messages are announced to assistive technology (BUG-51 regression)
test("test_project_page_status_messages_are_live_regions", () => {
    const html = fs.readFileSync(path.join(frontend, "project.html"), "utf8");
    for (const id of ["member-message", "bug-message"]) {
        const element = html.match(new RegExp(`<p id="${id}"[^>]*>`));
        assert.ok(element, id);
        assert.match(element[0], /class="section-message"/, id);
        assert.match(element[0], /role="status"/, id);
        assert.match(element[0], /aria-live="polite"/, id);
    }

    // A live region must stay in the accessibility tree while empty, or new text is not
    // announced: empty messages may collapse but must never be display: none.
    const css = fs.readFileSync(path.join(frontend, "style.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    const emptyRules = [...css.matchAll(/([^{}]*\.section-message:empty[^{}]*)\{([^}]*)\}/g)];
    assert.ok(emptyRules.length > 0);
    for (const [, selector, body] of emptyRules) {
        assert.doesNotMatch(body, /display\s*:\s*none|visibility\s*:\s*hidden/, selector.trim());
    }
});
