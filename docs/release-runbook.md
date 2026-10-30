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
| `v1.0.0-rc.1` (image tag `1.0.0-rc.1`) | `22af3b38b924173f3cb0e765a9b3ffc2f497c1e7` | `sha256:521487fab6b59b20c1aafbfad4ef1a8b4a7993a16479ff8ecca1d18bc60a3bef` |

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
  starting the service, so old tokens cannot attach to different accounts. After restoring
  a snapshot, re-apply any account deletions in the request log made after that snapshot.
- **Staging database:** start staging for v1.0.0 on a new database. Demos created before
  schema version 4 have no Demo record, so they are never deleted automatically.
- **Demo retention and capacity:** the cleanup at startup and every hour deletes each Demo
  once it is seven days old, which frees capacity. `Try Demo refused: limit … reached` means
  stored Demos fill the cap: wait for expiries, raise `DEMO_TOTAL_LIMIT` (maximum 2000) or set
  it to `0` to switch Try Demo off. Never delete Demo data by hand or reset the database.
- **Cleanup failures** are logged as `Expired Demo <id> (created …) was not deleted: <reason>`.
  That Demo is kept whole and retried every hour. In Render Shell, `python -m app.admin status`
  lists Demos past retention; one more than about 2 hours past needs manual resolution: take
  a backup of the database first and investigate the logged reason. Never insert or alter
  `demo_accounts` associations by hand, and never delete ordinary accounts' data to force
  cleanup. Once resolved, run `python -m app.admin run-retention`.
- **Account deletion on request:** confirm the request comes from the account's email
  address. Set `READ_ONLY_MODE=1` on the running service in its Render environment settings
  (the service restarts). The command checks only its own environment, so setting it just for
  the command does not stop the application's writes. Before confirming, check that a write
  to the application returns HTTP 503 with the maintenance message. In Render Shell, run
  `python -m app.admin delete-account EMAIL`, review the dry run, then add `--confirm`.
  Remove `READ_ONLY_MODE` from the service, record the request and reply
  within one month. Owned projects are deleted; reports in other people's projects are kept
  without attribution.
- **Privacy-request records** stay in the privacy mailbox with only the information needed
  to show how each request was handled. Delete them 12 months after the request is resolved,
  unless a legal obligation or a specific dispute requires keeping them longer.
- **Suspension and retirement:** suspending a service keeps its disk and database. To retire
  a service permanently, delete the service and its persistent disk; Render keeps each daily
  snapshot for 7 days after it was created.
- **AI failures** are logged as `AI provider request failed: <type> (HTTP status <code>)`.

## 5. Smoke checklist (staging, then production)

**Manual smoke testing**

- [ ] `/version` returns the expected version; the About page shows it.
- [ ] Register three accounts for the Project Owner, QA Analyst and Developer roles.
      Registration logs in automatically, so also log out and log in again explicitly.
- [ ] Create a project, add the QA Analyst and Developer as members, and create and assign a bug.
- [ ] Move the bug through Triage → Open → Development → Testing → Closed with the required
      roles and assignments.
- [ ] Try Demo opens both seeded Demo projects; AI Assist returns real suggestions.
- [ ] The QA Analyst and Developer members can each leave a project.
- [ ] Restart the Render service: the projects, members and bugs created above are still there.

**Deployment verification**

- [ ] In Render Shell, `python -m app.admin status` shows the expected database path and no errors.
- [ ] Response headers include `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff`.

## 6. Go/No-Go and promotion

Go when all of these hold:

- Staging passes every smoke item.
- No Blocker or Major defect is open, and bug report statuses in the tracker are reconciled.
- The privacy and data-handling review is complete, and the Privacy Policy matches the
  release, including the controller and a privacy contact. The production service matches
  its hosting statements: Frankfurt (EU Central) region, Hobby workspace (7-day logs) and
  the database on the persistent disk at `/var/data`.
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
