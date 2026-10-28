# Release runbook

How a release candidate becomes a production release. Evidence lives in the
[execution report](test-execution.md); this page only lists the steps and settings.

## 1. Freeze the release candidate

1. Set `APP_VERSION` in `app/version.py` to the release version (for example `1.0.0`).
2. Merge to `main` with all five required status checks passing (three Application CI
   jobs, Postman and JMeter). Record the CI runs in the execution report.
3. Tag the commit as a pre-release (for example `v1.0.0-rc.1`).

## 2. Build the image

Run the **Release image** workflow with the full commit SHA, the tag `1.0.0-rc.1` and
**publish** on. (With publish off it only builds and smoke-tests, which is useful as a dry run.)
It builds exactly that commit, smoke-tests the container and pushes
`ghcr.io/ventilatorrr/ai-qa-bug-triage:<tag>`. Record the digest from the job summary
below. The GHCR package must be public so Render can pull it.

| Release | Commit | Image digest |
| --- | --- | --- |
| | | |

## 3. Render services

Staging and production are separate Render web services that deploy the image **by digest**.

| Setting | Staging | Production |
| --- | --- | --- |
| Image | `ghcr.io/ventilatorrr/ai-qa-bug-triage@sha256:…` | Same digest as staging |
| Persistent disk | Own disk mounted at `/var/data` | Own disk mounted at `/var/data` |
| `DATABASE_NAME` | `/var/data/bugtriage.db` | `/var/data/bugtriage.db` |
| `JWT_SECRET_KEY` | New random value (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) | Different new random value |
| `OPENAI_API_KEY` | Optional | Required for AI Assist |
| `AI_DAILY_USER_LIMIT` / `AI_DAILY_GLOBAL_LIMIT` | `5` / `20` | `20` / `500` |
| `DEMO_TOTAL_LIMIT` | `1000` (default) | `1000` (default) |
| Health check path | `/version` | `/version` |
| Instances | 1 | 1 |

The application runs as a non-root user. If the disk mount is not writable for it, startup
fails with a database error: fix the mount permissions rather than changing the path.

## 4. Rules

- **Secrets:** never reuse a secret between environments or from an earlier deployment.
  Whenever a database is replaced, recreated or restored, rotate `JWT_SECRET_KEY` before
  starting the service, so old tokens cannot attach to different accounts.
- **Demo capacity:** a log line `Try Demo refused: limit … reached` means capacity is used
  up. Raise `DEMO_TOTAL_LIMIT` (maximum 2000) or set it to `0` to switch Try Demo off.
  Never delete Demo accounts or reset the database to recover capacity.
- **AI failures** are logged as `AI provider request failed: <type> (HTTP status <code>)`.

## 5. Smoke checklist (staging, then production)

- [ ] `/version` returns the expected version; About shows it.
- [ ] Register, log in and log out; create a project and a bug; move it through the lifecycle.
- [ ] Try Demo opens both seeded projects; AI Assist returns suggestions (when configured).
- [ ] A QA Analyst can leave a project.
- [ ] Restart the service: the data created above is still there.
- [ ] Response headers include `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff`.
      Add HSTS only if Render does not already send `Strict-Transport-Security`.

## 6. Go/No-Go and promotion

Go when all of these hold:

- Staging passes every smoke item.
- No Blocker or Major defect is open, and bug report statuses in the tracker are reconciled.
- The privacy and data-handling review is complete, and the Privacy Policy matches the
  release, including the controller and a privacy contact.
- Deferred review findings have been assessed for release impact.
- The release candidate's CI and verification evidence is recorded in the execution report.

Deploy the same digest to production, repeat the smoke checklist, then publish the GitHub Release.

**Rollback within v1.0.x:** redeploy the previous v1.0.x digest on the same disk. Versions
before 1.0.0 cannot open a schema-3 database, so never roll back below 1.0.0 on an existing disk.

**First release:** v1.0.0 has no earlier v1.0.x image to roll back to. Keep the separate
v0.2.0 service and its disk until v1.0.0 production passes its smoke test, so the previous
deployment remains available if the launch is abandoned before public use. It is not a
safe rollback target after launch: v0.2.0 lacks the v1.0.0 public-hosting hardening and
cannot carry over v1.0.0 accounts or data. If v1.0.0 fails after public launch, protect its
disk and data first, then assess recovery; do not send public users to v0.2.0 automatically.

## 7. Retire the v0.2.0 service

After production passes its smoke test, shut down the old v0.2.0 Render service and delete
its disk. Its database is not migrated, and the first-release fallback is no longer available.
