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
        this.classList = {toggle() {}, add() {}, remove() {}};
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
    appendChild(child) {
        child.parent = this;
        this.children.push(child);
        if (child.tagName === "option" && this.options) this.options.push(child);
        return child;
    }
    replaceChildren(...children) { this.children = []; children.forEach(child => this.appendChild(child)); }
    remove() { this.parent.children = this.parent.children.filter(child => child !== this); }
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
    querySelector(selector) { return this.all(selector)[0] || null; }
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
    Object.values(inputs).forEach(input => form.appendChild(input));
    form.querySelector = selector => inputs[selector];
    const button = new Element("button"), message = new Element("p"), area = new Element("section");
    const begin = () => runtime.beginAiAssistSession(form, prefix, button, message, area);
    begin();
    const requests = [];
    const submit = (send = async () => success({title: "Suggested title"})) => runtime.submitAiAssist(
        form, prefix, prefix === "bug-" ? "/projects/1/ai-assist" : "/projects/1/bugs/2/ai-assist",
        button, message, (url, options) => { requests.push({url, options}); return send(url, options); }
    );
    const card = label => area.all("article").find(card => card.all("h4")[0].textContent === label);
    const action = (label, field) => {
        const root = field ? card(field) : area;
        root.all("button").find(button => button.textContent === label).click();
    };
    return {runtime, inputs, form, button, message, area, begin, submit, requests, card, action};
}

function success(suggestions) { return {ok: true, json: async () => ({outcome: "suggestions", suggestions})}; }
function deferred() {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
}


module.exports = {Element, fixture, success, deferred};
