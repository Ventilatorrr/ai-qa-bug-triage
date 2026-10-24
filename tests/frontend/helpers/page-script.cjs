const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const scripts = path.join(__dirname, "../../../frontend/js");
const authImport = /^import \{([^}]+)\} from "\.\/auth\.js";(?=\r?\n)/;
const authExport = /^export (?=(?:async )?function (\w+))/gm;
const moduleSyntax = /^\s*(?:import|export)\b/m;

// Browsers load the authenticated pages as ES modules importing auth.js. A vm
// context runs classic scripts, so the harness runs both files as strict
// (module-like) classic scripts after checking the import against the exports.
// Their functions stay context globals that tests can call or replace.
// Same-line replacements keep stack-trace line numbers aligned with the source.
function loadAuthScript(runtime) {
    const auth = fs.readFileSync(path.join(scripts, "auth.js"), "utf8");
    const classicAuth = auth.replace(authExport, "");
    if (moduleSyntax.test(classicAuth)) throw new Error("Unsupported module syntax in auth.js");
    vm.runInContext(`"use strict"; ${classicAuth}`, runtime, {filename: "auth.js"});
    return [...auth.matchAll(authExport)].map(match => match[1]);
}

function loadPageScript(runtime, script) {
    const source = fs.readFileSync(path.join(scripts, script), "utf8");
    const imported = source.match(authImport);
    if (!imported) throw new Error(`${script} must start by importing from ./auth.js`);
    const classicPage = source.replace(authImport, '"use strict";');
    if (moduleSyntax.test(classicPage)) throw new Error(`Unsupported module syntax in ${script}`);
    const exported = loadAuthScript(runtime);
    for (const name of imported[1].split(",").map(name => name.trim())) {
        if (!exported.includes(name)) throw new Error(`${script} imports ${name}, which auth.js does not export`);
    }
    vm.runInContext(classicPage, runtime, {filename: script});
}

module.exports = {loadAuthScript, loadPageScript};
