// Read-only static fixture server. No app database, credentials, or provider calls.
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "../..");
const routes = new Map([
    ["/", ["tests/frontend/native-input.test.html", "text/html"]],
    ["/project.html", ["frontend/project.html", "text/html"]],
    ["/bugs.html", ["frontend/bugs.html", "text/html"]],
    ["/js/ai-assist.js", ["frontend/js/ai-assist.js", "text/javascript"]]
]);
http.createServer((request, response) => {
    const route = routes.get(request.url);
    if (request.method !== "GET" || !route) {
        response.writeHead(404).end();
        return;
    }
    response.writeHead(200, {"Content-Type": route[1], "Cache-Control": "no-store"});
    response.end(fs.readFileSync(path.join(root, route[0])));
}).listen(8128, "127.0.0.1", () => {
    console.log("Native input regressions: http://127.0.0.1:8128/ (Ctrl+C to stop)");
});
