# Release runbook

How a release candidate becomes a production release. Evidence lives in the
[execution report](test-execution.md); this page only lists the steps and settings.

## 1. Freeze the release candidate

1. Set `APP_VERSION` in `app/version.py` to the release version (for example `1.0.0`).
2. Merge to `main` with all five required status checks passing (three Application CI
   jobs, Postman and JMeter). Record the CI runs in the execution report.
3. Tag the commit as a pre-release (for example `v1.0.0-rc.1`).

## 2. Build and deploy the image

Run the **Release image** workflow from `main` with the full commit SHA, an image tag that
starts with `APP_VERSION` (for example `1.0.1-rc.1`) and a mode:

| Mode | What it does |
| --- | --- |
| `build-only` | Builds and smoke-tests any commit; publishes and deploys nothing (dry run) |
| `staging` | Publishes the image and deploys it to staging only; no production approval is requested |
| `staging-then-production` | As `staging`, then waits for approval and deploys the same digest to production |

For both deploy modes the commit must be the current `main` HEAD with all five required checks
passed. The workflow builds that commit once, records it in the image, smoke-tests the
container and pushes `ghcr.io/ventilatorrr/ai-qa-bug-triage:<tag>`. Each deploy calls the
environment's Render deploy hook with an explicit `imgURL=<image>@sha256:…`, waits until
`/version` reports the expected version and commit, then checks the security headers, the
Privacy Policy page and that an unauthenticated `/projects` request returns 401. Timeouts and
errors fail the run; nothing writes to either database. Production is never rebuilt and
never deploys on a merge. Only one run executes at a time: a newer run waits, and replaces
(cancels) any run that was already waiting. A `staging` run cannot be promoted later; to
release, start a `staging-then-production` run with a new tag.

Record the digest from the job summary below. The GHCR package must be public so Render can pull it.

**GitHub environments** (Settings → Environments):

| Setting | `staging` | `production` |
| --- | --- | --- |
| Deployment branches | `main` only | `main` only |
| Required reviewers | None | The maintainer; **Prevent self-review off** (a single maintainer approves their own run) |
| Allow administrators to bypass | — | Off |
| Secret `RENDER_DEPLOY_HOOK_URL` | Staging service deploy hook | Production service deploy hook |
| Variable `APP_URL` | Staging `https://…` origin | `https://ai-qa-bug-triage.onrender.com` |

Copy each deploy hook straight from the Render service settings into its environment secret;
regenerate the hook in Render if it is ever exposed. Configure both environments **before** the
first deploy run: GitHub creates an environment that a workflow references without any
protection rules, so the `production` name alone does not require approval. Never add a
repository-level `RENDER_DEPLOY_HOOK_URL` secret, which every job could read without approval.

| Release | Commit | Image digest |
| --- | --- | --- |
| `v1.0.0-rc.1` (image tag `1.0.0-rc.1`) | `22af3b38b924173f3cb0e765a9b3ffc2f497c1e7` | `sha256:521487fab6b59b20c1aafbfad4ef1a8b4a7993a16479ff8ecca1d18bc60a3bef` |
| `v1.0.0` (promoted release candidate, not rebuilt) | `22af3b38b924173f3cb0e765a9b3ffc2f497c1e7` | `sha256:521487fab6b59b20c1aafbfad4ef1a8b4a7993a16479ff8ecca1d18bc60a3bef` |
| `v1.0.1` (image tag `1.0.1-rc.1`, promoted from staging by digest) | `7aabfdf13ac10c93585101c32c97c97f97e62002` | `sha256:051f0df6ce4083c6dfff7c83ef002b6f39ddf980574af1ef5cad0c3b6d7f9328` |

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

**Configured image:** a deploy hook with `imgURL` deploys that digest but does not change the
service's configured image, which stays at the previous digest. **Manual Deploy → Deploy latest
reference**, or a hook call without `imgURL`, would redeploy that older image. After each
successful deploy, review the service's Image URL in its Render settings and update it to the
deployed digest; until then, use only the workflow to deploy. Before relying on restarts after
the first automated staging deploy, restart staging once and confirm `/version` still reports
the deployed commit. A service with a disk stops its old instance before starting the new one,
so each deploy causes a brief outage.

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

Approve the production job of the `staging-then-production` run, so production receives the
digest that staging verified in the same run. After it passes, align both services' configured
images (section 3), repeat the manual smoke checklist, then publish the GitHub Release.

**Rollback within v1.0.x (manual):** in the production service's Render settings, set the Image
URL to the previous known-good digest from the table in section 2, save, and deploy that
reference. Confirm `/version` reports that release (images before 1.0.1 report only `version`;
later ones also report their commit), check the headers and sign-in, and record the rollback.
Restoring a disk snapshot is not part of a rollback: it loses later data and needs its own
review. Versions before 1.0.0 cannot open a schema-3 database, so never roll back below 1.0.0
on an existing disk, and check that the target image supports the database's schema version.

**First release:** v1.0.0 has no earlier v1.0.x image to roll back to, and v0.2.0 is not a
rollback target: its service was converted for v1.0.0 (section 7), it lacks the v1.0.0
public-hosting hardening and it cannot carry over v1.0.0 accounts or data. If v1.0.0 fails,
protect its disk and data first, then assess recovery.

## 7. v0.2.0 service conversion (completed)

For v1.0.0, the existing `ai-qa-bug-triage` Render service, which ran v0.2.0 from Git with
Python, was converted to the approved Docker image. It keeps its service identity and URL,
<https://ai-qa-bug-triage.onrender.com/>. Its old persistent disk was deleted and a new 1 GB
disk attached at `/var/data`, so no v0.2.0 data was migrated. No separate v0.2.0 service or
disk remains to retire; this service is now production.
