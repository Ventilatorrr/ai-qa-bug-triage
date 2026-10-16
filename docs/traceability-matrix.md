# Requirement Traceability Matrix (RTM)

One authoritative overall assessment per acceptance criterion in [requirements](requirements.md).
TC definitions and precise selectors are in the [catalogue](test-cases.md); execution
provenance is in [test-execution](test-execution.md). Assessed on 16 October 2026
against `27c46ac` plus the deterministic coverage additions, with user-reported
M01–M05 results for `1.0.0-dev`. AC-019.2 additionally incorporates the reviewed
16 October live evaluations at `aa6977b` / `061fcef` plus recorded local changes.

**88 Covered / 0 Partial / 0 Not Covered / 88 total.**

- **Covered:** every required behavior has sufficient combined evidence at suitable layers.
- **Partial:** meaningful evidence exists, but a stated requirement remains unverified.
- **Not Covered:** no meaningful verification exists.
- Coverage is distinct from a test result or increment/release completion. Mocked AI tests do not establish real-model factual quality.

| REQ | AC | TC IDs | Test Type | Overall Coverage |
| --- | --- | --- | --- | --- |
| REQ-001 | AC-001.1 — Successful Registration | [TC-217](test-cases.md#tc-217), [TC-329](test-cases.md#tc-329) | API; Playwright | Covered |
| REQ-001 | AC-001.2 — Duplicate Email | [TC-218](test-cases.md#tc-218) | API | Covered |
| REQ-001 | AC-001.3 — Invalid Email | [TC-219](test-cases.md#tc-219) | API | Covered |
| REQ-001 | AC-001.4 — Invalid Password | [TC-220](test-cases.md#tc-220), [TC-221](test-cases.md#tc-221), [TC-222](test-cases.md#tc-222), [TC-223](test-cases.md#tc-223) | API | Covered |
| REQ-001 | AC-001.5 — Password Security | [TC-225](test-cases.md#tc-225) | Database | Covered |
| REQ-002 | AC-002.1 — Successful Login | [TC-169](test-cases.md#tc-169), [TC-177](test-cases.md#tc-177), [TC-329](test-cases.md#tc-329) | API; Playwright | Covered |
| REQ-002 | AC-002.2 — Invalid Credentials | [TC-178](test-cases.md#tc-178), [TC-179](test-cases.md#tc-179), [TC-330](test-cases.md#tc-330) | API; Playwright | Covered |
| REQ-003 | AC-003.1 — Authenticated Access | [TC-180](test-cases.md#tc-180), [TC-329](test-cases.md#tc-329) | API; Playwright | Covered |
| REQ-003 | AC-003.2 — Unauthenticated Access | [TC-181](test-cases.md#tc-181), [TC-329](test-cases.md#tc-329) | API; Playwright | Covered |
| REQ-003 | AC-003.3 — Invalid Authentication | [TC-171](test-cases.md#tc-171), [TC-172](test-cases.md#tc-172), [TC-182](test-cases.md#tc-182) | API | Covered |
| REQ-004 | AC-004.1 — Successful Logout | [TC-329](test-cases.md#tc-329) | Playwright | Covered |
| REQ-004 | AC-004.2 — Protected Access After Logout | [TC-329](test-cases.md#tc-329) | Playwright | Covered |
| REQ-005 | AC-005.1 — Successful Project Creation | [TC-184](test-cases.md#tc-184), [TC-188](test-cases.md#tc-188), [TC-322](test-cases.md#tc-322), [TC-339](test-cases.md#tc-339) | API; Frontend JS; Playwright | Covered |
| REQ-005 | AC-005.2 — Invalid Project Name | [TC-185](test-cases.md#tc-185), [TC-186](test-cases.md#tc-186), [TC-187](test-cases.md#tc-187), [TC-309](test-cases.md#tc-309), [TC-310](test-cases.md#tc-310), [TC-311](test-cases.md#tc-311), [TC-312](test-cases.md#tc-312), [TC-313](test-cases.md#tc-313), [TC-320](test-cases.md#tc-320), [TC-321](test-cases.md#tc-321), [TC-339](test-cases.md#tc-339) | API; Frontend JS; Playwright | Covered |
| REQ-005 | AC-005.3 — Unauthenticated User | [TC-189](test-cases.md#tc-189) | API | Covered |
| REQ-006 | AC-006.1 — View Project List | [TC-190](test-cases.md#tc-190) | API | Covered |
| REQ-006 | AC-006.2 — Project List Authorization | [TC-191](test-cases.md#tc-191) | API | Covered |
| REQ-006 | AC-006.3 — Open Project | [TC-192](test-cases.md#tc-192) | API | Covered |
| REQ-006 | AC-006.4 — Unauthorized Project Access | [TC-193](test-cases.md#tc-193), [TC-331](test-cases.md#tc-331) | API; Playwright | Covered |
| REQ-007 | AC-007.1 — Successful Project Name Editing | [TC-194](test-cases.md#tc-194), [TC-197](test-cases.md#tc-197), [TC-324](test-cases.md#tc-324), [TC-339](test-cases.md#tc-339) | API; Frontend JS; Playwright | Covered |
| REQ-007 | AC-007.2 — Unauthorized Project Name Editing | [TC-198](test-cases.md#tc-198) | API | Covered |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | [TC-195](test-cases.md#tc-195), [TC-196](test-cases.md#tc-196), [TC-314](test-cases.md#tc-314), [TC-315](test-cases.md#tc-315), [TC-316](test-cases.md#tc-316), [TC-317](test-cases.md#tc-317), [TC-318](test-cases.md#tc-318), [TC-319](test-cases.md#tc-319), [TC-320](test-cases.md#tc-320), [TC-323](test-cases.md#tc-323) | API; Frontend JS | Covered |
| REQ-008 | AC-008.1 — Successful Project Deletion | [TC-199](test-cases.md#tc-199), [TC-200](test-cases.md#tc-200), [TC-339](test-cases.md#tc-339) | API; Playwright | Covered |
| REQ-008 | AC-008.2 — Unauthorized Project Deletion | [TC-201](test-cases.md#tc-201) | API | Covered |
| REQ-009 | AC-009.1 — Add Member | [TC-202](test-cases.md#tc-202), [TC-203](test-cases.md#tc-203), [TC-331](test-cases.md#tc-331) | API; Playwright | Covered |
| REQ-009 | AC-009.2 — Remove Member | [TC-204](test-cases.md#tc-204), [TC-205](test-cases.md#tc-205), [TC-206](test-cases.md#tc-206), [TC-331](test-cases.md#tc-331) | API; Playwright | Covered |
| REQ-009 | AC-009.3 — Invalid Member | [TC-207](test-cases.md#tc-207) | API | Covered |
| REQ-009 | AC-009.4 — Duplicate Member | [TC-208](test-cases.md#tc-208) | API | Covered |
| REQ-009 | AC-009.5 — View Project Members | [TC-209](test-cases.md#tc-209), [TC-331](test-cases.md#tc-331) | API; Playwright | Covered |
| REQ-010 | AC-010.1 — Project Owner Role | [TC-211](test-cases.md#tc-211) | API | Covered |
| REQ-010 | AC-010.2 — QA Analyst Role | [TC-212](test-cases.md#tc-212) | API | Covered |
| REQ-010 | AC-010.3 — Developer Role | [TC-213](test-cases.md#tc-213) | API | Covered |
| REQ-010 | AC-010.4 — Unauthorized Project Member Management | [TC-214](test-cases.md#tc-214) | API | Covered |
| REQ-010 | AC-010.5 — Unauthorized Project Actions | [TC-215](test-cases.md#tc-215), [TC-216](test-cases.md#tc-216) | API | Covered |
| REQ-011 | AC-011.1 — Successful Bug Creation | [TC-066](test-cases.md#tc-066), [TC-132](test-cases.md#tc-132), [TC-133](test-cases.md#tc-133), [TC-138](test-cases.md#tc-138), [TC-335](test-cases.md#tc-335) | API; Playwright | Covered |
| REQ-011 | AC-011.2 — Missing Bug Title | [TC-067](test-cases.md#tc-067) | API | Covered |
| REQ-011 | AC-011.3 — Unauthorized Bug Creation | [TC-068](test-cases.md#tc-068) | API | Covered |
| REQ-011 | AC-011.4 — Optional Bug Information | [TC-069](test-cases.md#tc-069), [TC-160](test-cases.md#tc-160), [TC-161](test-cases.md#tc-161), [TC-338](test-cases.md#tc-338) | API; Playwright | Covered |
| REQ-012 | AC-012.1 — View Bug List | [TC-070](test-cases.md#tc-070), [TC-271](test-cases.md#tc-271), [TC-343](test-cases.md#tc-343) | API; Frontend JS; Manual | Covered |
| REQ-012 | AC-012.2 — Open Bug Report | [TC-071](test-cases.md#tc-071), [TC-135](test-cases.md#tc-135), [TC-262](test-cases.md#tc-262), [TC-264](test-cases.md#tc-264), [TC-266](test-cases.md#tc-266), [TC-267](test-cases.md#tc-267), [TC-333](test-cases.md#tc-333), [TC-341](test-cases.md#tc-341), [TC-343](test-cases.md#tc-343), [TC-344](test-cases.md#tc-344) | API; Browser fixture; Frontend JS; Manual; Playwright | Covered |
| REQ-012 | AC-012.3 — Unauthorized Bug Access | [TC-072](test-cases.md#tc-072), [TC-073](test-cases.md#tc-073), [TC-332](test-cases.md#tc-332) | API; Playwright | Covered |
| REQ-012 | AC-012.4 — Sort Bug Reports | [TC-074](test-cases.md#tc-074), [TC-270](test-cases.md#tc-270), [TC-273](test-cases.md#tc-273), [TC-274](test-cases.md#tc-274), [TC-275](test-cases.md#tc-275), [TC-276](test-cases.md#tc-276), [TC-277](test-cases.md#tc-277), [TC-278](test-cases.md#tc-278), [TC-279](test-cases.md#tc-279), [TC-280](test-cases.md#tc-280), [TC-281](test-cases.md#tc-281), [TC-282](test-cases.md#tc-282), [TC-333](test-cases.md#tc-333), [TC-348](test-cases.md#tc-348), [TC-349](test-cases.md#tc-349), [TC-350](test-cases.md#tc-350) | API; Frontend JS; Playwright | Covered |
| REQ-012 | AC-012.5 — Paginate Bug Reports | [TC-275](test-cases.md#tc-275), [TC-333](test-cases.md#tc-333), [TC-334](test-cases.md#tc-334), [TC-345](test-cases.md#tc-345) | Frontend JS; Manual; Playwright | Covered |
| REQ-012 | AC-012.6 — Remember Bug Page Size | [TC-268](test-cases.md#tc-268), [TC-269](test-cases.md#tc-269), [TC-333](test-cases.md#tc-333), [TC-334](test-cases.md#tc-334) | Frontend JS; Playwright | Covered |
| REQ-013 | AC-013.1 — Edit Bug Report | [TC-075](test-cases.md#tc-075), [TC-134](test-cases.md#tc-134), [TC-335](test-cases.md#tc-335) | API; Playwright | Covered |
| REQ-013 | AC-013.2 — Optional Bug Information | [TC-077](test-cases.md#tc-077), [TC-162](test-cases.md#tc-162), [TC-163](test-cases.md#tc-163), [TC-164](test-cases.md#tc-164), [TC-167](test-cases.md#tc-167), [TC-338](test-cases.md#tc-338) | API; Playwright | Covered |
| REQ-013 | AC-013.3 — Unauthorized Bug Editing | [TC-078](test-cases.md#tc-078) | API | Covered |
| REQ-014 | AC-014.1 — Successful Bug Deletion | [TC-079](test-cases.md#tc-079), [TC-263](test-cases.md#tc-263), [TC-335](test-cases.md#tc-335) | API; Frontend JS; Playwright | Covered |
| REQ-014 | AC-014.2 — Unauthorized Bug Deletion | [TC-080](test-cases.md#tc-080), [TC-081](test-cases.md#tc-081), [TC-332](test-cases.md#tc-332) | API; Playwright | Covered |
| REQ-015 | AC-015.1 — Assign and Unassign Bugs | [TC-082](test-cases.md#tc-082), [TC-083](test-cases.md#tc-083), [TC-084](test-cases.md#tc-084), [TC-086](test-cases.md#tc-086), [TC-205](test-cases.md#tc-205), [TC-335](test-cases.md#tc-335) | API; Playwright | Covered |
| REQ-015 | AC-015.2 — Invalid Assignment | [TC-085](test-cases.md#tc-085) | API | Covered |
| REQ-015 | AC-015.3 — Unauthorized Bug Assignment | [TC-086](test-cases.md#tc-086) | API | Covered |
| REQ-015 | AC-015.4 — Change Bug Assignee | [TC-087](test-cases.md#tc-087) | API | Covered |
| REQ-016 | AC-016.1 — Set Bug Severity | [TC-088](test-cases.md#tc-088) | API | Covered |
| REQ-016 | AC-016.2 — Set Bug Priority | [TC-089](test-cases.md#tc-089) | API | Covered |
| REQ-016 | AC-016.3 — Update Bug Classification | [TC-090](test-cases.md#tc-090) | API | Covered |
| REQ-016 | AC-016.4 — Unauthorized Bug Classification | [TC-091](test-cases.md#tc-091) | API | Covered |
| REQ-017 | AC-017.1 — Bug Status | [TC-094](test-cases.md#tc-094), [TC-305](test-cases.md#tc-305), [TC-346](test-cases.md#tc-346) | API; Frontend JS; Manual | Covered |
| REQ-017 | AC-017.2 — Triage to Open | [TC-095](test-cases.md#tc-095), [TC-096](test-cases.md#tc-096), [TC-097](test-cases.md#tc-097), [TC-098](test-cases.md#tc-098), [TC-099](test-cases.md#tc-099), [TC-306](test-cases.md#tc-306), [TC-336](test-cases.md#tc-336) | API; Frontend JS; Playwright | Covered |
| REQ-017 | AC-017.3 — Open to Development | [TC-100](test-cases.md#tc-100), [TC-101](test-cases.md#tc-101), [TC-102](test-cases.md#tc-102), [TC-103](test-cases.md#tc-103), [TC-307](test-cases.md#tc-307), [TC-336](test-cases.md#tc-336) | API; Frontend JS; Playwright | Covered |
| REQ-017 | AC-017.4 — Development to Testing | [TC-104](test-cases.md#tc-104), [TC-105](test-cases.md#tc-105), [TC-106](test-cases.md#tc-106), [TC-107](test-cases.md#tc-107), [TC-308](test-cases.md#tc-308), [TC-336](test-cases.md#tc-336) | API; Frontend JS; Playwright | Covered |
| REQ-017 | AC-017.5 — Testing Outcome | [TC-108](test-cases.md#tc-108), [TC-109](test-cases.md#tc-109), [TC-110](test-cases.md#tc-110), [TC-111](test-cases.md#tc-111), [TC-112](test-cases.md#tc-112), [TC-113](test-cases.md#tc-113), [TC-114](test-cases.md#tc-114), [TC-115](test-cases.md#tc-115), [TC-155](test-cases.md#tc-155), [TC-156](test-cases.md#tc-156), [TC-157](test-cases.md#tc-157), [TC-158](test-cases.md#tc-158), [TC-159](test-cases.md#tc-159), [TC-168](test-cases.md#tc-168), [TC-286](test-cases.md#tc-286), [TC-287](test-cases.md#tc-287), [TC-288](test-cases.md#tc-288), [TC-336](test-cases.md#tc-336), [TC-337](test-cases.md#tc-337), [TC-338](test-cases.md#tc-338) | API; Frontend JS; Playwright | Covered |
| REQ-017 | AC-017.6 — Close Without Fixing | [TC-116](test-cases.md#tc-116), [TC-117](test-cases.md#tc-117), [TC-118](test-cases.md#tc-118), [TC-119](test-cases.md#tc-119), [TC-120](test-cases.md#tc-120), [TC-166](test-cases.md#tc-166), [TC-308](test-cases.md#tc-308), [TC-338](test-cases.md#tc-338) | API; Frontend JS; Playwright | Covered |
| REQ-017 | AC-017.7 — Closed Bugs | [TC-121](test-cases.md#tc-121), [TC-122](test-cases.md#tc-122), [TC-123](test-cases.md#tc-123), [TC-124](test-cases.md#tc-124), [TC-125](test-cases.md#tc-125), [TC-165](test-cases.md#tc-165), [TC-336](test-cases.md#tc-336) | API; Playwright | Covered |
| REQ-017 | AC-017.8 — Invalid Status Transitions | [TC-126](test-cases.md#tc-126), [TC-127](test-cases.md#tc-127), [TC-128](test-cases.md#tc-128), [TC-129](test-cases.md#tc-129), [TC-130](test-cases.md#tc-130) | API | Covered |
| REQ-017 | AC-017.9 — Status Update Timestamp | [TC-131](test-cases.md#tc-131) | API | Covered |
| REQ-018 | AC-018.1 — Access AI Triage | [TC-001](test-cases.md#tc-001), [TC-002](test-cases.md#tc-002), [TC-003](test-cases.md#tc-003), [TC-004](test-cases.md#tc-004), [TC-005](test-cases.md#tc-005), [TC-006](test-cases.md#tc-006), [TC-007](test-cases.md#tc-007) | API | Covered |
| REQ-018 | AC-018.2 — Explicit Request | [TC-232](test-cases.md#tc-232), [TC-325](test-cases.md#tc-325) | Frontend JS; Playwright | Covered |
| REQ-018 | AC-018.3 — Use Current Form Information | [TC-008](test-cases.md#tc-008), [TC-009](test-cases.md#tc-009), [TC-010](test-cases.md#tc-010), [TC-011](test-cases.md#tc-011), [TC-231](test-cases.md#tc-231), [TC-325](test-cases.md#tc-325) | API; Frontend JS; Playwright | Covered |
| REQ-018 | AC-018.4 — Request Outcome | [TC-053](test-cases.md#tc-053), [TC-056](test-cases.md#tc-056), [TC-062](test-cases.md#tc-062), [TC-327](test-cases.md#tc-327), [TC-328](test-cases.md#tc-328) | API; Playwright | Covered |
| REQ-019 | AC-019.1 — Supported Suggestion Fields | [TC-018](test-cases.md#tc-018), [TC-040](test-cases.md#tc-040), [TC-041](test-cases.md#tc-041), [TC-053](test-cases.md#tc-053) | API; Python unit | Covered |
| REQ-019 | AC-019.2 — Use Bug and Project Context | [TC-012](test-cases.md#tc-012), [TC-013](test-cases.md#tc-013), [TC-014](test-cases.md#tc-014), [TC-015](test-cases.md#tc-015), [TC-016](test-cases.md#tc-016), [TC-017](test-cases.md#tc-017), [TC-021](test-cases.md#tc-021), [TC-024](test-cases.md#tc-024), [TC-053](test-cases.md#tc-053), [TC-136](test-cases.md#tc-136), [TC-351](test-cases.md#tc-351), [TC-352](test-cases.md#tc-352), [TC-353](test-cases.md#tc-353), [TC-354](test-cases.md#tc-354), [TC-355](test-cases.md#tc-355), [TC-356](test-cases.md#tc-356) | API; Python unit; Real-model evaluation / assisted review | Covered |
| REQ-019 | AC-019.3 — Validate Suggested Values | [TC-019](test-cases.md#tc-019), [TC-020](test-cases.md#tc-020), [TC-030](test-cases.md#tc-030), [TC-032](test-cases.md#tc-032), [TC-034](test-cases.md#tc-034), [TC-037](test-cases.md#tc-037), [TC-042](test-cases.md#tc-042), [TC-044](test-cases.md#tc-044), [TC-045](test-cases.md#tc-045), [TC-046](test-cases.md#tc-046), [TC-047](test-cases.md#tc-047), [TC-048](test-cases.md#tc-048), [TC-051](test-cases.md#tc-051), [TC-053](test-cases.md#tc-053), [TC-057](test-cases.md#tc-057), [TC-058](test-cases.md#tc-058) | API; Python unit | Covered |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | [TC-022](test-cases.md#tc-022), [TC-025](test-cases.md#tc-025), [TC-027](test-cases.md#tc-027), [TC-028](test-cases.md#tc-028), [TC-029](test-cases.md#tc-029), [TC-033](test-cases.md#tc-033), [TC-035](test-cases.md#tc-035), [TC-036](test-cases.md#tc-036), [TC-039](test-cases.md#tc-039), [TC-043](test-cases.md#tc-043), [TC-049](test-cases.md#tc-049), [TC-050](test-cases.md#tc-050), [TC-053](test-cases.md#tc-053), [TC-056](test-cases.md#tc-056), [TC-062](test-cases.md#tc-062), [TC-230](test-cases.md#tc-230), [TC-328](test-cases.md#tc-328) | API; Frontend JS; Playwright; Python unit | Covered |
| REQ-020 | AC-020.1 — Review Suggestions | [TC-235](test-cases.md#tc-235), [TC-237](test-cases.md#tc-237), [TC-325](test-cases.md#tc-325) | Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | [TC-229](test-cases.md#tc-229), [TC-238](test-cases.md#tc-238), [TC-251](test-cases.md#tc-251), [TC-325](test-cases.md#tc-325), [TC-340](test-cases.md#tc-340) | Browser fixture; Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.3 — Dismiss an Individual Suggestion | [TC-239](test-cases.md#tc-239), [TC-325](test-cases.md#tc-325) | Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | [TC-229](test-cases.md#tc-229), [TC-240](test-cases.md#tc-240), [TC-325](test-cases.md#tc-325), [TC-340](test-cases.md#tc-340) | Browser fixture; Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.5 — Dismiss All Pending Suggestions | [TC-241](test-cases.md#tc-241), [TC-326](test-cases.md#tc-326) | Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.6 — Repeat AI Assist Requests | [TC-242](test-cases.md#tc-242) | Frontend JS | Covered |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | [TC-250](test-cases.md#tc-250), [TC-293](test-cases.md#tc-293), [TC-295](test-cases.md#tc-295), [TC-302](test-cases.md#tc-302), [TC-325](test-cases.md#tc-325), [TC-326](test-cases.md#tc-326) | Frontend JS; Playwright | Covered |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | [TC-245](test-cases.md#tc-245), [TC-246](test-cases.md#tc-246), [TC-247](test-cases.md#tc-247), [TC-248](test-cases.md#tc-248), [TC-249](test-cases.md#tc-249), [TC-291](test-cases.md#tc-291), [TC-292](test-cases.md#tc-292), [TC-296](test-cases.md#tc-296), [TC-297](test-cases.md#tc-297), [TC-298](test-cases.md#tc-298), [TC-299](test-cases.md#tc-299), [TC-300](test-cases.md#tc-300), [TC-301](test-cases.md#tc-301), [TC-303](test-cases.md#tc-303), [TC-304](test-cases.md#tc-304), [TC-326](test-cases.md#tc-326), [TC-347](test-cases.md#tc-347) | Frontend JS; Manual; Playwright | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | [TC-235](test-cases.md#tc-235), [TC-236](test-cases.md#tc-236), [TC-238](test-cases.md#tc-238), [TC-240](test-cases.md#tc-240), [TC-250](test-cases.md#tc-250) | Frontend JS | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | [TC-001](test-cases.md#tc-001), [TC-002](test-cases.md#tc-002), [TC-003](test-cases.md#tc-003), [TC-004](test-cases.md#tc-004), [TC-005](test-cases.md#tc-005), [TC-006](test-cases.md#tc-006), [TC-007](test-cases.md#tc-007), [TC-059](test-cases.md#tc-059), [TC-060](test-cases.md#tc-060), [TC-332](test-cases.md#tc-332) | API; Playwright | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | [TC-012](test-cases.md#tc-012), [TC-013](test-cases.md#tc-013), [TC-014](test-cases.md#tc-014), [TC-017](test-cases.md#tc-017), [TC-023](test-cases.md#tc-023), [TC-024](test-cases.md#tc-024), [TC-053](test-cases.md#tc-053), [TC-057](test-cases.md#tc-057), [TC-136](test-cases.md#tc-136), [TC-252](test-cases.md#tc-252), [TC-253](test-cases.md#tc-253), [TC-254](test-cases.md#tc-254), [TC-255](test-cases.md#tc-255), [TC-256](test-cases.md#tc-256), [TC-257](test-cases.md#tc-257), [TC-258](test-cases.md#tc-258) | API; Frontend JS; Python unit | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | [TC-021](test-cases.md#tc-021), [TC-032](test-cases.md#tc-032), [TC-036](test-cases.md#tc-036), [TC-038](test-cases.md#tc-038), [TC-041](test-cases.md#tc-041), [TC-042](test-cases.md#tc-042), [TC-044](test-cases.md#tc-044), [TC-046](test-cases.md#tc-046), [TC-049](test-cases.md#tc-049), [TC-053](test-cases.md#tc-053), [TC-054](test-cases.md#tc-054), [TC-061](test-cases.md#tc-061), [TC-235](test-cases.md#tc-235), [TC-250](test-cases.md#tc-250) | API; Frontend JS; Python unit | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | [TC-008](test-cases.md#tc-008), [TC-027](test-cases.md#tc-027), [TC-028](test-cases.md#tc-028), [TC-029](test-cases.md#tc-029), [TC-031](test-cases.md#tc-031), [TC-036](test-cases.md#tc-036), [TC-052](test-cases.md#tc-052), [TC-055](test-cases.md#tc-055), [TC-062](test-cases.md#tc-062), [TC-063](test-cases.md#tc-063), [TC-232](test-cases.md#tc-232), [TC-233](test-cases.md#tc-233), [TC-244](test-cases.md#tc-244), [TC-246](test-cases.md#tc-246), [TC-247](test-cases.md#tc-247), [TC-327](test-cases.md#tc-327) | API; Frontend JS; Playwright; Python unit | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | [TC-056](test-cases.md#tc-056), [TC-230](test-cases.md#tc-230), [TC-243](test-cases.md#tc-243), [TC-244](test-cases.md#tc-244), [TC-289](test-cases.md#tc-289), [TC-290](test-cases.md#tc-290), [TC-327](test-cases.md#tc-327), [TC-328](test-cases.md#tc-328) | API; Frontend JS; Playwright | Covered |

## Coverage closure and limitations

- **AC-019.2 — Use Bug and Project Context:** deterministic context/prompt tests and [TC-351–TC-356](test-cases.md#ac-0192-opt-in-evaluation) collectively verify current-form primacy, grounded rewriting, relevant historical proposals and abstention from unsupported facts. The [final review](test-execution.md#ac-0192-final-evaluation-review) records 30 live evaluations (12 original, 12 historical clarification, six formatting correction), assessed against the unchanged [rubric](ai-testing-strategy.md). Final EVAL-D returns all five supported historical values with field-only formatting. Closure is user-directed, based on Codex-assisted review; raw assessment templates remain unchanged. The final configuration has one six-case run; this representative evidence does not establish zero hallucinations, independent human scoring or broad model reliability. No stated AC gap remains in this assessment.

Manual contributions remain user-reported; existing JavaScript assertions supply
M05’s manually unreproduced race case. The member-display and complete sorting-rank
gaps are closed by current automated execution. See the [execution record](test-execution.md)
for exact results, provenance and limitations.

Broader cross-browser/accessibility and release criteria belong to the
[QA strategy](qa-strategy.md) and [Definition of Done](definition-of-done.md);
they do not impose duplicate verification on every AC.
