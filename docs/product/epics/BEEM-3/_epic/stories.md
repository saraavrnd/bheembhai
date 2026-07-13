# Stories — BEEM-3 (Project access, identity & run ownership)

Epic `BEEM-3` covers FR-001, FR-002, FR-003, FR-004, FR-005, and FR-006. It has been decomposed
into 7 stories below. `BEEM-17` is the regular-user signup prerequisite, and `BEEM-16` is the
bootstrap prerequisite that seeds the first platform admin; the remaining stories then build on
that identity and access foundation.

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
As an **admin**, I want **to create a project with a linked GitHub repository and let signed-in users see only the projects they can access**, so that **teams stay scoped to the right codebases**.

### Acceptance Criteria
**Scenario: Admin creates a project with a linked repository**
- Given an admin user is signed in
- When they create a project with a name and a GitHub repository identifier
- Then the project is saved with that exact name and repository reference

**Scenario: Missing repository is rejected**
- Given an admin user is signed in
- When they create a project without a GitHub repository identifier
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
- FR-001
- FR-002

### Out of scope
Assigning project roles, workflow-policy pairing, repository reachability validation, and any run execution features.

### Notes / dependencies
Depends on the authenticated-user baseline from FR-005 and the project access model used by later approval stories.

---

## STORY: Pin workflow-policy pairings  (BEEM-13)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 5 · **Labels:** fa-1, mvp

### Story
As an **admin**, I want **to assign a version-pinned workflow-policy pairing to a project and let run users pick only approved pairings**, so that **runs cannot weaken governance**.

### Acceptance Criteria
**Scenario: Admin pins a workflow-policy pairing**
- Given an admin is signed in
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
Depends on the project access baseline and the versioned workflow/policy records from the workflow-definition epic.

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

## STORY: Assign project roles for approvals  (BEEM-15)
**Epic:** BEEM-3 · **Release:** MVP · **Estimate:** 3 · **Labels:** fa-1, mvp

### Story
As a **project admin**, I want **to assign project roles and have approvals honor those roles**, so that **only authorized reviewers can approve gated steps**.

### Acceptance Criteria
**Scenario: Admin assigns an approval role to a project member**
- Given a project admin is signed in
- When they assign the Reviewer role to a project member
- Then the member is stored as eligible to approve steps that require the Reviewer role

**Scenario: Eligible reviewer can approve**
- Given a project member has the required approval role for a gated step
- When they approve the step
- Then the approval action is accepted

**Scenario: Ineligible project member cannot approve**
- Given a project member does not have the required approval role for a gated step
- When they try to approve the step
- Then the approval is rejected and the step remains pending

**Scenario: Non-member cannot approve**
- Given a user is not a member of the project
- When they try to approve a gated step for that project
- Then the approval is rejected

**Scenario: Approval chooser shows only eligible reviewers**
- Given a gated step requires the Reviewer role
- When the approval request is presented
- Then only project members with the Reviewer role are shown as eligible approvers

### Covered requirements
- FR-006

### Out of scope
Approval decision storage, approval notifications, workflow routing after approval, and multi-reviewer quorum rules.

### Notes / dependencies
Depends on project membership from the access story and on the approval-gate workflow from the orchestration epic.

---
Coverage summary: FR-001, FR-002, FR-003, FR-004, FR-005, and FR-006 are all covered by at least one story.
