# Frontend QA Verification Report

**Verification period:** 12–13 October 2026; final verification on 13 October.
**Baseline:** About-page commit `80e5e29` plus reviewed frontend refinements.
This report consolidates recorded evidence; its editorial revision adds no test runs.

## Scope and traceability

Verification covered both permanent themes, Bug List/Details, form controls,
AI review, lifecycle dropdowns, destructive controls and About, with separate backend/API regressions.

Sources: [requirements](requirements.md), [traceability matrix](traceability-matrix.md),
[Definition of Done](definition-of-done.md), [stylesheet](../frontend/style.css), [Bug Details markup](../frontend/bugs.html),
[bug handlers](../frontend/js/bugs.js) and [AI review helper](../frontend/js/ai-assist.js).

- **REQ-012 — Bug Access:** targeted Details layout and display evidence.
- **REQ-014 — Bug Deletion:** confirmation-handler, API and control-state evidence.
- **REQ-020:** individual/bulk AI review, form sessions and native input handling.
- **REQ-021 / AC-021.1 — Identify Pending AI Suggestions:** separate labelled
  suggestion cards, accessible group name and pending-only guidance.

Broader Partial coverage and increment/release completion are not upgraded; requirement IDs and AC titles are unchanged.

## Environments and verification methods

| Method | Environment and purpose |
| --- | --- |
| Automated backend tests | Project virtual environment; serial pytest execution against disposable test databases. |
| Automated frontend tests | Node test runner; DOM substitutes and handler/helper assertions, not a complete browser suite. |
| Browser fixture assertions | Manually triggered checks using real HTML/CSS/native controls in the Codex in-app Chromium browser. |
| Manual browser testing | Visual inspection and trusted pointer/keyboard actions on isolated previews and disposable FastAPI pages. |
| Computed-style measurements | Browser foreground/font/background readings; ancestor alpha layers and gradients included in contrast calculations. |

Final static previews used actual renderers and AI code with deterministic
responses, without backend handlers/database access. Earlier integrated checks
used disposable FastAPI data on localhost port 8137; neither used a live provider.
Unchanged development database SHA-256: `74A1555AC5B50D476CCD9998952C4FAA4DFE3A1928741008639047F0914491FB`.
The disposable `test_bugtriage.db` was absent after pytest.

## Final approved state and pre-commit verification — 2026-10-13

Manual source updates after earlier handoffs were preserved; historical measurements are labelled separately.

| Surface | Dark | Light |
| --- | --- | --- |
| Bug List normal rows / read-only Details base | `#1B2D46` | `#F7FAFC` |
| Inputs / AI cards | `#0C1A2E` / `#0C1A2E` | `#FFFFFF` / `#EFF7FA` |
| Table header | `#122238` | `#E4EEF4` |
| Row hover / keyboard focus | Approximately `#1D334B` | `#EFF7FA` |
| Internal Details/table dividers | `#30465F` | `#C5D4DF` |

Dark hover is `color-mix(in srgb, var(--bug-surface-background) 97%, var(--title-text))`,
computed as `color(srgb 0.114824 0.198471 0.295569)`.
The 38px toggle, button roles, AI Assist and About were preserved. Rejected
semantic backgrounds/strokes/oversizing are absent; no external lab code is loaded.

Final review removed three unused properties from both theme blocks:
`--header-button-background`, `--header-button-hover`, `--ai-instruction-background`.
**30 page/theme fixture audits found zero computed-style, protected-control or
geometry changes** against the pre-cleanup snapshot. Custom-property enumeration
was excluded because removing unused declarations was intentional.
A targeted pending-file scan found no common key prefixes/private-key headers or accidental database/temp files;
this was not a full security audit.

## Automated regression and static checks

The final full suites passed; later cleanup was CSS-only and did not trigger reruns.
No configured applicable lint tool was found. Browser cases are separate below.

| Recorded command / check | Result |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pytest` | **544 passed, 0 failed, 0 skipped**, 315.97s; exit 0 |
| `node --test --test-reporter=tap tests/frontend/*.test.cjs` | **80 passed, 0 failed, 0 skipped/cancelled/todo**, 302.2254ms; exit 0 |
| `node --check` on the seven files listed below | All passed; exit 0 |
| Node `vm.Script` compilation of inline scripts in both native fixtures | Both passed; exit 0 |
| `git diff --check` | Passed; no output |

Syntax checks covered `frontend/js/ai-assist.js`, `frontend/js/bugs.js`, `frontend/js/project.js`,
`frontend/js/projects.js`, `tests/frontend/ai-assist.test.cjs`,
`tests/frontend/bug-number-display.test.cjs` and `tests/frontend/native-input-server.cjs` individually.

Frontend coverage includes individual/bulk review, pending-only application, stale sessions/responses,
supported fields, normalization, request context, errors, permissions, sorting/pagination and confirmation.
[AI tests](../tests/frontend/ai-assist.test.cjs) include
`test_ai_pending_guidance_uses_bottom_status_and_clears_after_review` for New/Edit,
final review, reset, error and no-usable states. [Deletion-handler coverage](../tests/frontend/bug-number-display.test.cjs)
includes `test_bug_deletion_requires_confirmation_and_preserves_cancelled_report`.

Earlier focused runs on 12 October (not additional final-suite totals):

| Command | Recorded result |
| --- | --- |
| `node --test tests/frontend/ai-assist.test.cjs` | 23 passed, 0 failures |
| `node --test --test-reporter=dot tests/frontend/*.test.cjs` | 80 passed, 0 failures; exit 0 |
| `.\.venv\Scripts\python.exe -m pytest tests/test_ai_assist.py tests/test_version.py -q` | 36 passed in 32.88s |
| `.\.venv\Scripts\python.exe -m pytest tests/test_bug.py tests/test_projects.py -k delete -q` | Two recorded runs: 9 passed, 162 deselected in 8.25s and 6.54s |

## Browser fixture assertions

These manually launched browser assertions are separate from Node/pytest counts and are not end-to-end automation.

| Test / fixture | Cases and result |
| --- | --- |
| `test_bug_details_dividers_preserve_metadata_rows` | **9/9 passed**: 1000/680/390px × optional fields hidden, both visible, or only Resolution visible |
| `test_destructive_buttons_preserve_focus_and_disabled_states` | **4/4 passed**: Bug/Project Delete × dark/light |
| `test_ai_native_input_browser_review_and_apply_consistency` | **12/12 passed**: New/Edit × Use/Use All × LF/CR/CRLF |

To repeat: run `node tests/frontend/native-input-server.cjs`, open
`http://127.0.0.1:8128/ui-style.test.html` and select **Run UI style regressions**;
use `http://127.0.0.1:8128/` for native input checks. Stop with Ctrl+C.
[UI style fixture](../tests/frontend/ui-style.test.html) and
[native input fixture](../tests/frontend/native-input.test.html) load real markup
without application handlers or database access. Their inline scripts passed syntax checks.

## Manual browser findings

- Final previews covered Login/Register, project display/editing, members/forms, Bug List,
  New/Edit Bug, read-only Details, AI cards and About in both themes.
- Keyboard row focus matched the hover background; links retained visible 2px
  outlines. Input focus used one turquoise border plus a soft glow. Validation
  focused empty required fields normally; error borders did not add a second outline.
- AI cards retained separate suggested values and accessible names. Pending review
  disabled AI Assist. Use All applied disposable values, cleared cards, enabled
  retry and displayed Create-specific guidance. Static fixtures did not persist data.
- Earlier disposable app flows verified Create/Save persistence after Use/Dismiss
  and Use All, preserved manual titles/dismissed fields, and cancelled unsaved mobile
  suggestions. These integrated observations predate the final palette review.
- Lifecycle QA/Developer population functions recreated hidden, disabled, selected
  empty prompts. Resolution used the same attributes and computed `display:none`.
  Closed fields showed their prompts. Opening did not assign a value; Escape/Tab
  preserved the empty value and moved focus. ArrowDown selected actual options.
- Delete default/hover/held-active, focus and disabled states were observed.
  The native confirmation appeared for a disposable report; user cancellation
  preserved it. Accepting the native dialog was not browser-verified.
- About retained its structure and `/version` value `1.0.0-dev`. Theme switching
  restored Details styles; the toggle stayed 38 × 38px. Persistence was not fully retested.
- Narrow inspection used confirmed 390 × 844 viewports/390px iframes. Inputs and
  AI cards had no observed internal overflow; actions wrapped. The existing
  horizontally scrollable 850px table remains. This is not complete mobile coverage.

## Accessibility and contrast

[WCAG 2.2 SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
requires 4.5:1 for normal text. Semantic values were **16px**, weight **700** in
rows/Details and **400** in selects/AI cards: none qualifies as large text.
Pass/fail used unrounded ratios; tables round only for readability. All final
semantic contexts below pass AA; not all meet normal-text AAA's 7:1 target.

| Dark severity / priority | Foreground | Normal row / Details worst | Hover / focus worst | Create / Edit / AI |
| --- | --- | --- | --- | --- |
| Blocker / Urgent | `#FF6B69` | 5.004689 | 4.659118 | 6.284337 |
| Major / High | `#F18F65` | 5.864062 | 5.459151 | 7.363443 |
| Moderate / Medium | `#E4C57D` | 8.329888 | 7.754714 | 10.459756 |
| Minor / Low | `#BFB7A3` | 6.963429 | 6.482608 | 8.743908 |

| Light severity / priority | Foreground | Normal row / Details worst | Hover / focus / AI | Create / Edit |
| --- | --- | --- | --- | --- |
| Blocker / Urgent | `#B4233E` | 6.163333 | 5.954188 | 6.460281 |
| Major / High | `#A6522E` | 5.179922 | 5.004147 | 5.429490 |
| Moderate / Medium | `#896814` | 4.942087 | 4.774384 | 5.180197 |
| Minor / Low | `#6B655A` | 5.512726 | 5.325658 | 5.778328 |

Exact minima: **4.659117570492354:1 dark**, **4.774383842619772:1 light**.
Composited Details gradients: dark `linear-gradient(145deg, #16294155, transparent 60%)` darkens its base;
light `linear-gradient(145deg, #ffffff88, transparent 60%)` lightens it. The base bounds the worst contrast.
Arrow gradients outside select text were excluded. Hover/active used test-only selector substitution
with transitions disabled; settled keyboard focus was also exercised directly.

No sampled enabled-text/input-boundary failure was found. Dark Bug Create hover text measured
**4.511480770118186:1**; input borders against fills were at least **3.347314860859643:1 dark**
and **3.9205388439265714:1 light**.
Disabled controls were treated as inactive, not counted as contrast passes.
See [SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
for non-text contrast; these measurements do not establish complete WCAG conformance.

### Additional recorded light-theme measurements

Recorded 13 October light control measurements:

| Element | Normal / focus | Hover | Pressed |
| --- | --- | --- | --- |
| AI Assist | 6.758337 | 6.033197 | 5.359835 |
| Login/Register | 5.926920 | 7.173049 | 4.805488 |
| Remove Member | 7.021561 default | 6.293909 | 5.669478 |

Other ratios: pressed opening control **4.805488266682599:1**; submission hover **5.166116424238643:1**;
Delete hover **6.343187155042352:1**; ordinary AI text **6.6037232541754785:1**;
placeholder text on white **6.1544009586240715:1**, and above 5:1 on page glow.
Control borders: **3.7403301957684305:1** against the Bug panel, **3.287539462037263:1** against the header.
Focus teal: **4.164823548156726:1** against the header, **4.738442064985758:1** against the Bug panel.
Checked page-glow endpoints retained more than 3:1 for these boundaries.
Decorative dividers are not essential control boundaries.

### Historical semantic measurements (superseded)

Superseded light measurements; column order: normal row/Details, hover/focus, input, AI card.

| Earlier foreground | Hover background | Recorded ratios in column order |
| --- | --- | --- |
| `#B4233E` | `#E3EFF3` | 6.163333 / 5.508772 / 6.460281 / 5.954188 |
| `#974127` | `#E3EFF3` | 6.460154 / 5.774070 / 6.771404 / 6.240937 |
| `#805709` | `#E3EFF3` | 6.098738 / 5.451037 / 6.392574 / 5.891785 |
| `#625B50` | `#E3EFF3` | 6.397590 / 5.718150 / 6.705825 / 6.180496 |
| `#B4233E` | `#EAF3F7` | 6.163333 / 5.740976 / 6.460281 / 5.954188 |
| `#A6522E` | `#EAF3F7` | 5.179922 / 4.824955 / 5.429490 / 5.004147 |
| `#896814` | `#EAF3F7` | 4.942087 / 4.603419 / 5.180197 / 4.774384 |
| `#6B655A` | `#EAF3F7` | 5.512726 / 5.134953 / 5.778328 / 5.325658 |

Proposed `#8A6A14` failed on `#EAF3F7` at **4.494253444600416:1**; `#896814` passed at
**4.603419157657993:1**. Final hover is `#EFF7FA`; current ratios are above.

## Defects, remediation and remaining risks

| Finding | Evidence / disposition |
| --- | --- |
| BUG-31: critical semantic contrast | Final dark/light measurements support remediation; no live status, resolution or Fix Version changed. User verification/closure remains pending. |
| Incomplete Assignee divider and missing explicit Delete focus outline | Native fixture assertions detected the original failures, then passed after correction. |
| Full-width Urgent backplate in external preview | Reproduced and corrected: `.ai-suggestion-value` background changed from `rgb(7, 13, 22)` to transparent while text remained `rgb(255, 23, 68)`. Final permanent styling has no backplates. |
| External preview specificity defects | Shared rules overrode action borders/card finishes; scoped fixes were rechecked in rendered previews. |
| Previously recorded narrow header clipping | Deferred; no comprehensive mobile redesign or retest closure claimed. |

No new application defect was confirmed. Standalone Chrome/other browser–OS combinations remain unverified;
native popup compositing was not reliably captured, so full Chrome hidden-option verification is not claimed.
Browser-controlled blue selection highlight remains accepted.
Screen readers, full zoom/reflow, complete [SC 2.4.11 focus-obscuration testing](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html),
broader mobile behavior and real-provider quality remain unverified.
Static success/error messages were examples, not API workflow evidence.

## Supporting evidence and historical preview checks

Local evidence: `final-frontend-verification.json`, `style.before-final-verification.css`,
`light-theme-browser-evidence.json`, `light-followup-browser-evidence.json`,
`resume-ui-browser-evidence.json`, `delete-native-states.json`, `light-theme-projects.png`, `light-refinements-actions.png`
and `urgent-bar-before.png` / `urgent-bar-after.png`. These artifacts are outside
the repository; interim JSON predates final colors. Temporary servers/tabs were closed.

Historical external-preview assertions are separate from permanent-theme results:
**48/48 checks per recorded run** covered New Bug, four Edit classification pairs,
unresolved/closed Details, Projects and a 390 × 844 preview; later **60/60 checks
per recorded run** covered Projects, New/Details/Edit, narrow Edit/About and
additional classification runs. They checked style reset/preservation, geometry,
transparent AI values and preview switching; pages without cards are not AI evidence.
External snippet `node --check` passed. Archival commands (artifact paths abbreviated):

| Command | Recorded result |
| --- | --- |
| `node …/ui-refinement-verify.cjs` | Passed syntax; original 10 definitions unchanged; 14 primary palettes, 3 destructive states and 4 card palettes met the checked 4.5:1 threshold |
| `node …/refined-theme-verify.cjs` | Passed syntax; first 14 definitions/generated CSS unchanged; 74 text/boundary/focus/gradient checks across 16 previews |
| `node …/resume-ui-preservation.cjs` | Passed source/About/version-loader and retained-work preservation checks |

One-off helpers are not a committed regression framework or current-theme coverage.
