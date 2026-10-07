const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Dependency-free DOM model. Text inputs strip CR/LF as native HTML controls do;
// focused browser checks separately verify this model and actual page workflows.
class Element {
    constructor(tagName = "div") {
        this.tagName = tagName;
        this.children = [];
        this.listeners = {};
        this.attributes = {};
        this.type = tagName === "input" ? "text" : "";
        this.value = "";
        this.className = "";
        const classes = () => new Set(this.className.split(/\s+/).filter(Boolean));
        this.classList = {
            contains: name => classes().has(name),
            add: (...names) => { this.className = [...new Set([...classes(), ...names])].join(" "); },
            remove: (...names) => { this.className = [...classes()].filter(name => !names.includes(name)).join(" "); },
            toggle: (name, force) => {
                const enabled = force ?? !this.classList.contains(name);
                this.classList[enabled ? "add" : "remove"](name);
                return enabled;
            }
        };
        this.textContent = "";
        this.hidden = false;
        this.disabled = false;
        this.isConnected = true;
    }
    get value() { return this._value; }
    set value(value) {
        this._value = this.tagName === "input" && this.type === "text"
            ? String(value).replace(/[\r\n]/g, "") : String(value);
    }
    cloneNode() { const clone = new Element(this.tagName); clone.type = this.type; return clone; }
    get parentElement() { return this.parent || null; }
    appendChild(child) {
        if (child.parent) child.remove();
        child.parent = this;
        this.children.push(child);
        if (child.tagName === "option" && this.options) this.options.push(child);
        return child;
    }
    replaceChildren(...children) { this.children.forEach(child => { child.parent = null; }); this.children = []; children.forEach(child => this.appendChild(child)); }
    remove() { if (this.parent) this.parent.children = this.parent.children.filter(child => child !== this); this.parent = null; }
    setAttribute(name, value) { this.attributes[name] = value; }
    addEventListener(type, handler) { (this.listeners[type] ||= new Set()).add(handler); }
    removeEventListener(type, handler) { this.listeners[type]?.delete(handler); }
    dispatchEvent(event) {
        for (const handler of this.listeners[event.type] || []) handler(event);
        if (event.bubbles) this.parent?.dispatchEvent(event);
    }
    click() { this.dispatchEvent({type: "click"}); }
    focus() { this.focused = true; }
    all(tagName) { return this.children.flatMap(child => [...(child.tagName === tagName ? [child] : []), ...child.all(tagName)]); }
    matches(selector) {
        if (selector.startsWith(".")) return this.classList.contains(selector.slice(1));
        if (selector.startsWith("#")) return this.id === selector.slice(1);
        return this.tagName === selector;
    }
    closest(selector) { return this.matches(selector) ? this : this.parent?.closest(selector) || null; }
    querySelectorAll(selector) { return this.children.flatMap(child => [...(child.matches(selector) ? [child] : []), ...child.querySelectorAll(selector)]); }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

function fixture(prefix, sharedRuntime) {
    const runtime = sharedRuntime || vm.createContext({
        formatApiError: (detail, fallback) => detail || fallback,
        document: {createElement: tagName => new Element(tagName)},
        Event: class { constructor(type, options) { this.type = type; Object.assign(this, options); } }
    });
    if (!sharedRuntime) {
        vm.runInContext(fs.readFileSync(path.join(__dirname, "../../../frontend/js/ai-assist.js"), "utf8"), runtime);
    }
    const inputs = Object.fromEntries([
        "title", "affected-version", "environment", "description", "steps",
        "expected", "actual", "severity", "priority", "assignee", "fix-version"
    ].map(suffix => [`#${prefix}${suffix}`, new Element(["description", "steps", "expected", "actual"].includes(suffix) ? "textarea" : ["severity", "priority", "assignee"].includes(suffix) ? "select" : "input")]));
    for (const [suffix, values] of [
        ["severity", ["", "Blocker", "Major", "Moderate", "Minor"]],
        ["priority", ["", "Urgent", "High", "Medium", "Low"]],
        ["assignee", ["", "7"]]
    ]) {
        inputs[`#${prefix}${suffix}`].options = values.map(value => ({value, textContent: value === "7" ? "qa@example.com (QA Analyst)" : value}));
    }
    const form = new Element("form");
    form.className = "bug-form";
    const button = new Element("button"), message = new Element("p"), area = new Element("section"), footer = new Element("div");
    area.className = "ai-suggestions";
    footer.className = "ai-suggestions-footer";
    form.appendChild(area);
    for (const [id, input] of Object.entries(inputs)) {
        input.id = id.slice(1);
        const row = new Element("div"), field = new Element("div"), label = new Element("label");
        row.className = "bug-field-row";
        field.className = "bug-field";
        label.setAttribute("for", input.id);
        field.appendChild(label);
        field.appendChild(input);
        row.appendChild(field);
        form.appendChild(row);
    }
    form.appendChild(footer);
    form.appendChild(button);
    form.appendChild(message);
    const begin = () => runtime.beginAiAssistSession(form, prefix, button, message, area);
    begin();
    const requests = [];
    const submit = (send = async () => success({title: "Suggested title"})) => runtime.submitAiAssist(
        form, prefix, prefix === "bug-" ? "/projects/1/ai-assist" : "/projects/1/bugs/2/ai-assist",
        button, message, (url, options) => { requests.push({url, options}); return send(url, options); }
    );
    const card = label => form.all("article").find(card => card.all("h4")[0].attributes["aria-label"] === `AI suggestion: ${label}`);
    const action = (label, field) => {
        const root = field ? card(field) : footer;
        root.all("button").find(button => button.textContent === label).click();
    };
    return {runtime, inputs, form, button, message, area, footer, begin, submit, requests, card, action};
}

function success(suggestions) { return {ok: true, json: async () => ({outcome: "suggestions", suggestions})}; }
function deferred() {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
}


module.exports = {Element, fixture, success, deferred};
