#!/usr/bin/env bash
# Deploys one immutable GHCR image to a Render service through its deploy hook, waits until
# /version reports the expected version and commit, then runs read-only smoke checks.
# Environment: HOOK_URL (secret), APP_URL, IMAGE (repository@sha256:...), EXPECTED_VERSION,
# EXPECTED_COMMIT. The hook URL is never printed.
set -euo pipefail

fail() { echo "::error::$*"; exit 1; }
summary() { echo "$*" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"; }

[[ -n "${HOOK_URL:-}" ]] || fail "RENDER_DEPLOY_HOOK_URL is not configured for this environment."
[[ "${APP_URL:-}" =~ ^https://[^/]+$ ]] || fail "APP_URL must be an https origin such as https://example.onrender.com."
[[ "${IMAGE:-}" =~ ^ghcr\.io/ventilatorrr/ai-qa-bug-triage@sha256:[0-9a-f]{64}$ ]] || fail "IMAGE must be a GHCR digest reference."
[[ "${EXPECTED_VERSION:-}" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$ ]] || fail "EXPECTED_VERSION is invalid."
[[ "${EXPECTED_COMMIT:-}" =~ ^[0-9a-f]{40}$ ]] || fail "EXPECTED_COMMIT is invalid."

is_expected_version() {
    python3 -c 'import json, os, sys
try:
    body = json.loads(sys.argv[1])
except ValueError:
    sys.exit(1)
sys.exit(body != {"version": os.environ["EXPECTED_VERSION"], "commit": os.environ["EXPECTED_COMMIT"]})' "$1"
}

http_status() { curl -s -o /dev/null --max-time 15 -w '%{http_code}' "$@"; }

before=$(curl -fsS --max-time 15 "$APP_URL/version" 2> /dev/null || echo unavailable)
summary "- Live before this deploy: \`$before\`"
summary "- Deploying: \`$IMAGE\`"

# Every deploy names the digest explicitly; without imgURL Render would use the service's
# configured image, which may be an older digest.
image_param=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$IMAGE")
separator='?'
[[ "$HOOK_URL" == *\?* ]] && separator='&'
status=$(curl -sS -o hook-response.json --max-time 30 -w '%{http_code}' -X POST \
    "${HOOK_URL}${separator}imgURL=${image_param}") || fail "The deploy hook request failed."
case "$status" in
    200)
        deploy_id=$(grep -o 'dep-[0-9a-z]*' hook-response.json | head -n 1 || true)
        echo "Render accepted the deploy ${deploy_id:-(no deploy ID in the response)}."
        summary "- Render deploy: ${deploy_id:-accepted without a deploy ID}" ;;
    202)
        # Queued behind another deploy: not a success until the new build is verified live.
        echo "::warning::Render queued this deploy behind another one; waiting for it to go live."
        summary "- Render deploy: queued behind another deploy" ;;
    *)
        rm -f hook-response.json
        fail "The deploy hook returned HTTP $status; nothing was verified." ;;
esac
rm -f hook-response.json

# A service with a persistent disk stops the old instance before starting the new one, so
# brief connection errors are expected. Only the expected version and commit count as live.
deadline=$((SECONDS + 900))
until live=$(curl -fsS --max-time 15 "$APP_URL/version" 2> /dev/null) && is_expected_version "$live"; do
    (( SECONDS < deadline )) || fail "Timed out after 15 minutes; /version did not report $EXPECTED_VERSION at $EXPECTED_COMMIT. Check the Render deploy logs."
    sleep 10
done
echo "Live: $live"

# Read-only smoke checks; nothing here writes to the application's database.
headers=$(curl -fsSI --max-time 15 "$APP_URL/login.html") || fail "/login.html did not return a success status."
grep -qi '^x-frame-options: DENY' <<< "$headers" || fail "X-Frame-Options: DENY is missing."
grep -qi '^x-content-type-options: nosniff' <<< "$headers" || fail "X-Content-Type-Options: nosniff is missing."
[[ "$(http_status "$APP_URL/privacy.html")" == 200 ]] || fail "/privacy.html did not return HTTP 200."
[[ "$(http_status "$APP_URL/projects")" == 401 ]] || fail "An unauthenticated /projects request did not return HTTP 401."

summary "- Verified live: \`$live\`; headers, Privacy Policy and authentication checks passed"
