const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const css = fs.readFileSync(path.join(__dirname, "../../frontend/style.css"), "utf8");

// Top-level rules only; media/supports blocks are skipped so that responsive
// overrides cannot satisfy the page-wide baseline.
function topLevelRules() {
    const source = css.replace(/\/\*[\s\S]*?\*\//g, "");
    const rules = [];
    let depth = 0, start = 0, selector = "";
    for (let index = 0; index < source.length; index++) {
        if (source[index] === "{") {
            if (depth === 0) selector = source.slice(start, index).trim();
            depth++;
            start = index + 1;
        } else if (source[index] === "}") {
            depth--;
            if (depth === 0 && !selector.startsWith("@")) {
                rules.push({selector, body: source.slice(start, index)});
            }
            start = index + 1;
        }
    }
    return rules;
}

function fontFamily(selector) {
    const families = topLevelRules()
        .filter(rule => rule.selector.split(",").map(part => part.trim()).includes(selector))
        .map(rule => rule.body.match(/font-family:\s*([^;]+);/))
        .filter(Boolean)
        .map(match => match[1].trim());
    return families.at(-1);
}

// TC-410 | Technical — Base font applies to page text and form controls
test("test_base_font_applies_to_page_text_and_form_controls", () => {
    assert.equal(fontFamily("body"), "Arial, sans-serif", "page text must not fall back to the browser default font");
    for (const control of ["button", "input", "select", "textarea"]) {
        assert.equal(fontFamily(control), "inherit", `${control} must inherit the page font`);
    }
    assert.match(
        css,
        /\.ai-suggestion > h4,\s*\.ai-suggestion > \.ai-suggestion-value \{\s*font-family: "Oxanium", Arial, sans-serif;/,
        "distinctive AI suggestion typography is preserved"
    );
});
