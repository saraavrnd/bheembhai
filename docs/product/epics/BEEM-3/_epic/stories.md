# Stories — BEEM-3 (Project access, identity & run ownership)

Epic `BEEM-3` covers FR-001, FR-002, FR-003, FR-004, FR-005, and FR-006. It has been decomposed
into 9 stories below. `BEEM-17` is the regular-user signup prerequisite, and `BEEM-16` is the
bootstrap prerequisite that seeds the first platform admin; the remaining stories then build on
that identity and access foundation. `BEEM-21` (edit project) was added in a second `epic-review`
pass on 2026-07-19 — see `epic-review.md`.

---

## STORY: Register a local user account  (BEEM-17)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, mvp

### Story
As a **visitor**, I want **to register a local account with my email and password**, so that **I can activate my account and later sign in**.

### Acceptance Criteria
**Scenario: New user registration creates an account**
- Given an unauthenticated visitor submits a new email address and a valid password
- When they register
- Then a user record is created with that email address, a hashed password, and an unverified email state

**Scenario: Registration sends a verification email**
- Given registration succeeds
- When the account is created
- Then a verification email is sent to that email address

**Scenario: Duplicate email registration is rejected**
- Given an email address already exists
- When registration is attempted with that email address
- Then the request is rejected and no duplicate user is created

**Scenario: Invalid registration input is rejected**
- Given the email address or password is missing or invalid
- When registration is attempted
- Then the request is rejected with a clear validation error and no user is created

### Covered requirements
- FR-005

### Out of scope
Email verification activation, sign in, password reset, MFA, SSO, social login, invite-only or admin-only provisioning models, and bootstrap admin creation.

### Notes / dependencies
Depends on the email delivery boundary from the integrations epic. This story creates the prerequisite user account for the authentication flow in `BEEM-14`.

---

## STORY: Add browser signup page  (BEEM-18)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, frontend, mvp

### Story
As a **visitor**, I want **a browser signup page with email and password fields**, so that **I can create a local account from the web UI instead of using the API directly**.

### Acceptance Criteria
**Scenario: Signup page renders the form**
- Given a visitor opens the signup page
- When the page loads
- Then the email and password fields, a submit button, and a sign-up heading are visible

**Scenario: Successful signup creates an account and shows the next step**
- Given a visitor enters a new email address and a valid password
- When they submit the signup form
- Then the account is created, a verification email is sent, and the page shows a success state that directs them to verify their email

**Scenario: Duplicate email signup is rejected**
- Given an email address already exists
- When the visitor submits the signup form with that email address
- Then the request is rejected and the page shows a clear duplicate-email error

**Scenario: Invalid signup input is rejected**
- Given the email address or password is missing or invalid
- When the visitor submits the signup form
- Then the page shows validation errors and no account is created

### Covered requirements
- FR-005

### Out of scope
Sign in, email verification activation, password reset, MFA, SSO, social login, invite-only provisioning, and admin-only provisioning.

### Notes / dependencies
Depends on `BEEM-17`, which provides the registration API and verification-email flow. This story should reuse the existing browser UI patterns used by the verification and reset-password pages and remain a thin UI layer over the existing registration flow.

---

## STORY: Align authentication screens to approved mockups  (BEEM-19)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, frontend, mvp

### Story
As a **visitor**, I want **the signup, sign-in, reset password, and verify email screens to match the approved mockups**, so that **the account-access flow feels consistent and polished**.

### Acceptance Criteria
**Scenario: Signup screen matches the approved mockup**
- Given a visitor opens the signup page
- When the page loads
- Then the page renders the approved centered card layout from `signup-light.png`
- And the email, password, and confirm-password fields are visible in the same order as the mockup
- And the primary "Create account" button and sign-in link are visible
- And the trust-footer content remains visible below the form

**Scenario: Sign-in screen matches the approved mockup**
- Given a visitor opens the sign-in page
- When the page loads
- Then the page renders the approved centered card layout from `signin-unified.png`
- And the email and password fields are visible
- And the verify-email callout, forgot-password link, and contact-support link are visible
- And the primary "Sign in" button is visible

**Scenario: Reset password screen matches the approved mockup**
- Given a visitor opens the reset-password page with a valid token
- When the page loads
- Then the page renders the approved two-panel layout from `reset-password.png`
- And the new-password field, "Update password" button, and "Go home" button are visible
- And the token-loaded info panel is visible
- And the success panel remains available after a successful password update

**Scenario: Verify email screen matches the approved mockup**
- Given a visitor opens the verify-email page with a valid token
- When the page loads
- Then the page renders the approved verified layout from `verify-email-unified.png`
- And the verification-flow panel with the email-sent, link-clicked, and email-verified states is visible
- And the "Go home" button and "Resend email" action are visible
- And the page still auto-verifies when the token is present in the email-link fragment

**Scenario: Auth screens remain usable on a narrow viewport**
- Given a visitor opens any of the four auth screens on a 390px-wide viewport
- When the page loads
- Then the primary form controls and actions remain visible without horizontal scrolling

### Covered requirements
- FR-005

### Out of scope
Changing auth routes, backend logic, validation rules, token handling, email delivery, MFA, SSO, social login, or any new auth copy beyond the approved mockups.

### Notes / dependencies
Depends on the existing auth flow stories (`BEEM-18` for signup and `BEEM-14` for sign-in, reset password, and verify email). Use the approved mockups in `output/imagegen/beem-3-ui-mockups/` as the visual source of truth.

---

## STORY: Bootstrap initial platform admin  (BEEM-16)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, mvp

### Story
As a **platform operator**, I want **the system to bootstrap a first platform admin account from configured credentials**, so that **someone can sign in and administer projects before any regular users exist**.

### Acceptance Criteria
**Scenario: Bootstrap creates the first admin user**
- Given bootstrap credentials are provided through configuration
- When the system boots for the first time
- Then a user record is created with that email address, a hashed password, and `platform_role = admin`

**Scenario: Bootstrapped admin can sign in**
- Given the bootstrap admin account exists
- When the admin signs in with the configured email and password
- Then the sign-in succeeds and the user reaches the authenticated session

**Scenario: Bootstrap is idempotent**
- Given the bootstrap admin account already exists
- When bootstrap runs again with the same credentials
- Then no duplicate admin user is created

**Scenario: Missing bootstrap credentials are rejected**
- Given the bootstrap email or password is missing from configuration
- When the system starts
- Then bootstrap fails with a clear error and no admin user is created

### Covered requirements
- FR-005

### Out of scope
Project creation, workflow-policy assignment, project-role management, email verification flows for regular users, and password reset flows for the bootstrap admin.

### Notes / dependencies
This is the prerequisite seed for `BEEM-12`, `BEEM-13`, and `BEEM-15`. It should be available before any story that assumes an authenticated admin can create or govern projects.

---

## STORY: Create and list accessible projects  (BEEM-12)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, mvp

### Story
As a **platform admin** (`platform_role = PLATFORM_ADMIN`), I want **to create a project by name and let signed-in users see only the projects they can access**, so that **teams stay scoped to the right codebases and can attach whichever tools the project actually needs afterward**.

### Acceptance Criteria
**Scenario: Admin creates a project with just a name**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`
- When they create a project with a name
- Then the project is saved with that exact name and zero integration bindings

**Scenario: Missing name is rejected**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`
- When they create a project without a name
- Then the request is rejected and no project is created

**Scenario: Signed-in user sees accessible projects**
- Given a signed-in user has access to two projects and not a third
- When they open the project list
- Then only the two accessible projects are shown

**Scenario: Unauthorized project stays hidden**
- Given a signed-in user does not have access to a project
- When they open the project list
- Then that project does not appear in the list

### Covered requirements
- FR-001 (name-only creation — see Notes/dependencies on the PRD wording mismatch this creates)
- FR-002

### Out of scope
Linking any integration provider — GitHub, Jira, or any other code-versioning/project-management/
devops tool category. Project creation no longer requires or accepts a repository (or any other
tool) reference directly; attaching and validating tool bindings is `BHEEM-4`'s
(`ProjectIntegrationBinding`) deliverable, not this story's. Also out of scope: assigning
additional project roles beyond the initial project-manager mapping created here, workflow-policy
pairing, and any run execution features.

### Notes / dependencies
Depends on the authenticated-user baseline from FR-005 and the project access model used by later
approval stories. Depends on `BEEM-16` for the first platform admin account. Only `platform_role =
PLATFORM_ADMIN` may create a project — unlike `BEEM-13`/`BEEM-15`, `Membership.role =
PROJECT_MANAGER` is not sufficient here, since a project has no members yet at creation time. A
newly created project has zero memberships until `BEEM-15`'s role-assignment capability is used to
map its first `PROJECT_MANAGER` — whether project creation should auto-assign the creating admin as
`PROJECT_MANAGER` was not specified and is left to `story-design` to confirm rather than assumed
here.

**Rescoped in the 2026-07-19 `epic-review` pass (round 2):** `githubRepositoryRef`/
`jiraProjectKey` are no longer part of project creation. A project can exist with a name and no
tool bindings; GitHub, Jira, and any future integration category (code-versioning, project-
management, devops, …) are attached afterward through the generic `ProjectIntegrationBinding`
mechanism owned by `BHEEM-4` (Integration providers & secrets vaulting), which is sequenced
immediately after this epic. This story now has an explicit, stated dependency on `BHEEM-4` for a
project to have any tool actually wired up — see `epic-review.md` for the full rationale and
`ADR-008` for the locked technical decision (data-model.md/openapi.yaml already updated). This
rescoping also means PRD `FR-001`'s current wording ("...with a name and linked GitHub
repository") no longer matches this story; updating the PRD text is outside this skill's
authority and is flagged, not done here.

---

## STORY: Land on authenticated Setup Dashboard after login  (BEEM-23)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 2 · **Labels:** fa-1, frontend, mvp

### Story
As a **signed-in user**, I want **to be taken to an authenticated "Setup Dashboard" immediately
after I sign in, with a sidebar entry point to my projects**, so that **I land on a single home
base for the platform instead of the public marketing page**.

Reference: the attached mockup (the "Platform Overview" design) is the long-term target for this
dashboard. Today only Projects (and auth) are real — Users & Roles, Policies, Integrations, Audit
Logs, Workflows, and Activity Monitor are unbuilt stubs owned by other epics. This story
implements only the real subset; the rest is explicitly out of scope until those epics land.

### Acceptance Criteria
**Scenario: Successful sign-in redirects to the Setup Dashboard**
- Given a user submits valid sign-in credentials
- When the sign-in succeeds
- Then the browser is redirected to the Setup Dashboard instead of the public home page

**Scenario: Dashboard requires authentication**
- Given a visitor is not signed in
- When they request the dashboard URL directly
- Then they are redirected to the sign-in page and the dashboard content is not rendered

**Scenario: Dashboard shows a live Projects entry point**
- Given a signed-in user has access to N projects
- When they open the dashboard
- Then a "Projects" sidebar link and/or stat card is shown with a count of N, and selecting it
  navigates to the Projects page (`BEEM-22`)

**Scenario: Zero-projects state renders correctly**
- Given a signed-in user has access to zero projects
- When they open the dashboard
- Then the Projects entry shows a count of 0 without erroring

**Scenario: No dead links for unbuilt entities**
- Given any signed-in user opens the dashboard
- When the page renders
- Then no sidebar item, stat card, or panel is shown for entities that don't exist yet
  (Users & Roles, Policies, Integrations, Audit Logs, Workflows, Activity Monitor, Settings)

### Covered requirements
None directly — this story is the authenticated navigation shell that hosts the entry point to
`BEEM-22`'s Projects page. FR-001 and FR-002 remain owned by `BEEM-12` (API) and `BEEM-22` (page).

### Out of scope
The create-project control and project list itself (`BEEM-22`'s scope, its own page rather than
embedded here). The rich dashboard content shown in the mockup — stat cards for
Users/Integrations/Workflows/Policies/Audit Logs, the Workflows panel, Recent Activity feed, and
Platform Metrics — since none of that data exists yet; deferred until those epics (`BHEEM-4`
through `BHEEM-10`, `BEEM-15`) ship. Role-based hiding beyond auth: the Projects entry is visible
to every signed-in user (per FR-002), so no admin-only gating exists on this page itself.

### Notes / dependencies
Depends on `BEEM-14`/`BEEM-16` (sign-in flow) for the redirect target. `BEEM-22` depends on this
shell for its sidebar entry point — sequence this story before `BEEM-22`. When later epics
deliver Users & Roles, Policies, Integrations, Audit Logs, Workflows, or Activity Monitor, this
dashboard should be revisited to add their nav items/cards per the attached mockup.

---

## STORY: Add browser project create-and-list page  (BEEM-22)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, frontend, mvp

### Story
As a **signed-in user**, I want **a Projects page where I can see the projects I have access to,
and — if I'm a platform admin — create a new project by name**, so that **I can manage projects
without calling the API directly**.

Reached via the "Projects" entry point on the Setup Dashboard (`BEEM-23`).

### Acceptance Criteria
**Scenario: Signed-in user sees their accessible projects on the page**
- Given a signed-in user has access to two projects and not a third
- When they open the Projects page
- Then only the two accessible projects are listed by name, and the third project does not appear

**Scenario: Signed-in user with no accessible projects sees an empty state**
- Given a signed-in user has access to zero projects
- When they open the Projects page
- Then the page shows an empty-state message and no project rows

**Scenario: Platform admin creates a project through the page**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN` is on the Projects page
- When they submit the create-project form with a valid name
- Then the request succeeds, the new project appears in the list, and the form returns to its
  empty/ready state

**Scenario: Platform admin submits an empty name**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN` is on the Projects page
- When they submit the create-project form with a blank name
- Then the form shows an inline validation error and no project is created

**Scenario: Non-admin user does not see project creation controls**
- Given a signed-in user whose `platform_role` is not `PLATFORM_ADMIN`
- When they open the Projects page
- Then no create-project form or button is rendered, only the accessible-projects list

**Scenario: Duplicate project name is rejected with a clear error**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN` submits a project name that
  already exists
- When the creation request is sent
- Then the page shows an error indicating the name is already taken and no duplicate project is
  created

### Covered requirements
- FR-001 (name-only creation — browser expression of `BEEM-12`'s API)
- FR-002 (browser expression of `BEEM-12`'s API)

### Out of scope
The dashboard shell, sidebar, and post-login redirect (`BEEM-23`'s scope — this page is reached
via `BEEM-23`'s "Projects" nav entry). Also out of scope: integration-binding UI (`BHEEM-4`),
membership/role management UI (`BEEM-15`), editing project details (`BEEM-21`), and
workflow-policy pairing UI (`BEEM-13`). Backend behavior, validation rules, and authorization
logic are not touched — this story only adds the page that consumes `BEEM-12`'s existing
`GET`/`POST /api/v1/projects` endpoints.

### Notes / dependencies
Depends on `BEEM-12` (merged; provides `GET`/`POST /api/v1/projects` with admin-only create and
access-scoped list) and `BEEM-23` (dashboard shell whose "Projects" nav entry links to this
page — sequence `BEEM-23` first). Reuses the existing browser auth page patterns — card layout,
form structure, and `theme.css` — established in `app/web/templates/auth/*` and
`BEEM-18`/`BEEM-19`.

---

## STORY: Edit project details  (BEEM-21)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 2 · **Labels:** fa-1, mvp

### Story
As a **platform admin or project manager** (`platform_role = PLATFORM_ADMIN`, or `Membership.role
= PROJECT_MANAGER` for this project), I want **to edit a project's name**, so that **I can correct
or update project metadata as the team's needs change**.

### Acceptance Criteria
**Scenario: Admin or project manager edits the project name**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role =
  PROJECT_MANAGER` for this project
- When they submit an updated project name
- Then the project's name is updated and persisted

**Scenario: Ineligible user cannot edit the project**
- Given a signed-in user without `platform_role = PLATFORM_ADMIN` and without a `Membership.role =
  PROJECT_MANAGER` for this project
- When they attempt to edit the project
- Then the request is rejected and the project is unchanged

**Scenario: Invalid input is rejected**
- Given the submitted name is missing or invalid
- When the edit is submitted
- Then the request is rejected with a clear validation error and no change is persisted

### Covered requirements
- FR-001 (extends project lifecycle management to editing — no dedicated FR/NFR ID exists for
  "edit project"; see Requirement coverage check in `epic-review.md`)

### Out of scope
Editing integration bindings (already its own surface — `PUT /projects/{projectId}/integrations`,
owned by `BHEEM-4`), editing workflow-policy pairings (`BEEM-13`), editing project membership or
roles (`BEEM-15`), and deleting a project entirely (not in scope for any BEEM-3 story).

### Notes / dependencies
Depends on `BEEM-12` for the project to exist and on `BEEM-16` for the first platform admin
account. Uses the already-existing `PATCH /projects/{projectId}` endpoint, which predates this
story in the API contract. Added in the 2026-07-19 `epic-review` pass (round 2) — no story
previously exercised this endpoint.

---

## STORY: Pin workflow-policy pairings  (BEEM-13)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 5 · **Labels:** fa-1, mvp

### Story
As a **platform admin or project manager** (`platform_role = PLATFORM_ADMIN`, or `Membership.role = PROJECT_MANAGER` for this project), I want **to assign a version-pinned workflow-policy pairing to a project and let run users pick only approved pairings**, so that **runs cannot weaken governance**.

### Acceptance Criteria
**Scenario: Admin or project manager pins a workflow-policy pairing**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role = PROJECT_MANAGER` for this project
- When they assign a workflow version and a policy version to a project
- Then the project stores the exact versions that were selected

**Scenario: Pairing stays pinned after later edits**
- Given a project has an assigned workflow-policy pairing
- When the underlying workflow or policy definition is edited later
- Then the project still points to the originally assigned versions

**Scenario: Run user sees only approved pairings**
- Given a project has one approved pairing and one unapproved pairing
- When a run user opens the run creation flow
- Then only the approved pairing is available to select

**Scenario: Unapproved pairing is rejected**
- Given a run user tries to select a pairing that the admin did not approve for the project
- When they submit the run
- Then the request is rejected and the run is not created with that pairing

### Covered requirements
- FR-003
- FR-004

### Out of scope
Editing workflow definitions or policy definitions themselves, and the run-execution lifecycle after a pairing is selected.

### Notes / dependencies
Depends on the project access baseline and the versioned workflow/policy records from the workflow-definition epic. Depends on `BEEM-16` for the first platform admin account, and on `BEEM-12` for the project's `PROJECT_MANAGER` membership to exist before that actor can pin a pairing. "Run user" here means any authenticated project member picking a pairing when creating a run — it is not a distinct `Membership.role` value.

---

## STORY: Sign in, verify email, and reset password  (BEEM-14)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 5 · **Labels:** fa-1, mvp

### Story
As a **user**, I want **to sign in with email/password, verify my email, and reset my password**, so that **I can activate and recover my account securely**.

### Acceptance Criteria
**Scenario: Unverified user cannot sign in**
- Given a user account exists but the email address is not verified
- When the user signs in with the correct email and password
- Then the sign-in attempt is rejected and the user is prompted to verify their email

**Scenario: Verified user can sign in**
- Given a user account exists and the email address is verified
- When the user signs in with the correct email and password
- Then the sign-in succeeds and the user reaches the authenticated session

**Scenario: Verification link activates the account**
- Given a user has an unexpired email-verification link
- When they open the link
- Then the account becomes verified and the link cannot be reused

**Scenario: Password reset link is issued**
- Given a verified user has forgotten their password
- When they request a password reset for their email address
- Then a reset link is generated for that email address

**Scenario: Password reset sets a new password**
- Given a user has a valid password-reset link
- When they submit a new password that meets the policy
- Then the password is updated and the old password no longer works

**Scenario: Invalid or expired reset link is rejected**
- Given a password-reset link is invalid or expired
- When the user opens it
- Then the request is rejected and no password change occurs

### Covered requirements
- FR-005

### Out of scope
MFA, SSO, social login, and account recovery flows outside email verification and password reset.

### Notes / dependencies
Depends on the local user registration story and email delivery plumbing from the integrations epic.

---

## STORY: Manage project membership and roles  (BEEM-15)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 5 · **Labels:** fa-1, mvp

### Story
As a **platform admin or project manager** (`platform_role = PLATFORM_ADMIN`, or `Membership.role = PROJECT_MANAGER` for this project), I want **to add a member to the project with a role, change an existing member's role, remove a member's membership, or mark a membership inactive**, so that **the platform records who holds which role on the project — ready for later approval-eligibility checks — and stays accurate as the team changes**.

### Acceptance Criteria
**Scenario: Admin or project manager adds a new member to the project**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role = PROJECT_MANAGER` for this project, and the target user has no existing membership on this project
- When they assign a `Membership.role` (e.g. Reviewer) to that user via `POST /projects/{projectId}/members`
- Then a new membership record is created for that user with that role and `isActive = true`

**Scenario: Admin or project manager changes an existing member's role**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role = PROJECT_MANAGER` for this project, and the target user already has a membership record on this project
- When they submit a different `Membership.role` for that user via `POST /projects/{projectId}/members`
- Then the existing membership record is updated in place with the new role, and no duplicate membership record is created

**Scenario: Admin or project manager removes a member's membership**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role = PROJECT_MANAGER` for this project
- When they remove a project member's membership
- Then the membership record is deleted and that member no longer has access to the project

**Scenario: Admin or project manager marks a membership inactive**
- Given a signed-in user with `platform_role = PLATFORM_ADMIN`, or a `Membership.role = PROJECT_MANAGER` for this project
- When they mark a member's membership inactive
- Then the membership record is retained with its role intact, but the member no longer has active access to the project

### Covered requirements
- FR-006 (assignment half only — see Notes/dependencies). Removal and deactivation aren't tied to
  any existing FR/NFR ID — see Requirement coverage check in `epic-review.md`.

### Out of scope
Approval-eligibility enforcement (which member can approve a given gated step), approval decision storage, approval notifications, workflow routing after approval, and multi-reviewer quorum rules. These require a gated-step/workflow concept that doesn't exist yet in this epic and belong to a story in the human-approvals epic (`BHEEM-8`) once that concept is built. Also out of scope: reactivating a previously-deactivated membership, and whether removing/deactivating a project's *last* remaining `PROJECT_MANAGER` should be blocked — both left to `story-design` to confirm rather than assumed here.

### Notes / dependencies
Depends on project membership from `BEEM-12` and on `BEEM-16` for the first platform admin account. FR-006 ("role-based approval eligibility") is only partly covered here: this story covers *assigning* a role to a member; *honoring* that role during a gated-step approval (eligible/ineligible reviewer, non-member rejection, approval chooser) is out of scope and needs its own story in `BHEEM-8` (Human approvals & stage collaboration) — flagged for that epic's own `user-story`/`epic-review` pass, not resolved here. The assignable `Membership.role` value set is an extensible, platform-wide catalog (`ProjectRole`, see ADR-007) rather than a fixed enum, resolved in the prior `epic-review` pass. **Extended in the 2026-07-19 `epic-review` pass (round 2)** to cover membership removal and deactivation, which the API contract and prior stories didn't support at all (no `DELETE` endpoint, no `isActive` field on `Membership`) — flagged as an architecture item in `epic-review.md` for `tech-design` (amend mode), now resolved by `ADR-009`: `Membership.isActive`, `DELETE /projects/{projectId}/members/{userId}`, and membership changes now append to the `StateTransition` audit log. Reactivation behavior and the last-`PROJECT_MANAGER` safeguard remain open for this story's own `story-design` to confirm (see ADR-009's consequences).

**Upsert-vs-conflict ambiguity resolved (2026-07-19):** `epic-review.md` flagged that the acceptance criteria didn't distinguish "add a new member" from "change an existing member's role," even though `POST /projects/{projectId}/members` is contractually an upsert (`MembershipUpsertRequest`). Resolved by splitting the acceptance criteria above into explicit add-new-member and change-existing-role scenarios: a re-POST for a user who already has a membership updates that row's role in place rather than creating a duplicate or being rejected as a conflict. This does not touch the still-open reactivation/last-`PROJECT_MANAGER` questions noted above.

---
Coverage summary: FR-001, FR-002, FR-003, FR-004, FR-005, and FR-006 are all covered by at least
one story. `BEEM-21` (edit project) and the removal/deactivation scenarios in `BEEM-15` don't map
to a dedicated FR/NFR ID — see `epic-review.md`'s Requirement coverage check.
