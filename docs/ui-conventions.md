# UI Conventions

**Status:** Approved · **Date:** 2026-07-10

The MVP UI is server-rendered and uses Bootstrap plus the EduAdmin theme shell. The goal is
consistency and clarity, not a heavyweight frontend application.

## Framework and component structure

- Stack: server-rendered Jinja2 templates, Bootstrap 5.3.8, minimal vanilla JavaScript.
- Theme shell: `EduAdmin` Bootstrap 5, using the non-RTL `bs5/main-mini-sidebar` variant as the
  default authenticated layout.
- Component location: templates grouped by feature, with shared fragments for navigation, tables,
  forms, alerts, approval panels, and the shell chrome.
- Naming: feature-first names for templates and partials, such as `projects/index.html`,
  `runs/detail.html`, and `_approval_panel.html`.

### Template tree

- `templates/layouts/app.html` - authenticated shell, sidebar, top bar, page wrapper
- `templates/layouts/auth.html` - login, verify-email, reset-password shell
- `templates/layouts/error.html` - 404/500 and generic error pages
- `templates/partials/sidebar.html` - project navigation and global sections
- `templates/partials/topbar.html` - notifications, user menu, search, and quick actions
- `templates/partials/cards.html` - reusable summary cards and KPI tiles
- `templates/partials/tables.html` - reusable table headers, row actions, empty states
- `templates/partials/forms.html` - inputs, selects, validation messages, help text
- `templates/partials/timeline.html` - transition history and approval history
- `templates/projects/*.html` - project list, detail, setup, integrations, members
- `templates/runs/*.html` - run list, detail, step detail, execution history
- `templates/approvals/*.html` - approval queue and decision flows
- `templates/config/*.html` - workflow and policy configuration views
- `templates/auth/*.html` - login, verification, password reset, invite flow if needed

## Theme adoption

Use the EduAdmin shell as the starting point for authenticated screens:

- Header, sidebar, and page content layout come from the mini-sidebar shell.
- Dashboard pages reuse the card, table, badge, and timeline patterns already present in the theme.
- Auth pages reuse the theme's centered card layout.
- Notification and approval actions should stay inside Bootstrap modals or inline panels; no custom
  SPA surface is needed.
- Keep the shell behavior lightweight. Prefer Bootstrap 5 JavaScript and minimal custom JS over
  carrying the theme's legacy jQuery interaction layer forward unchanged.

### Asset plan

Copy only the assets that the shell actually needs:

- `bs5/main-mini-sidebar/css/style.css`
- `bs5/main-mini-sidebar/css/vendors_css.css`
- `bs5/main-mini-sidebar/css/skin_color.css`
- `bs5/main-mini-sidebar/css/custom.css` as the BheemBhai override layer
- `bs5/main-mini-sidebar/js/template.js` only if we decide to preserve the legacy sidebar behavior
- `bs5/main-mini-sidebar/images/` and the shared `bs5/images/` logo assets
- One icon family only, preferably the icon set already referenced by the shell

Do not copy the demo pages, charts, mailbox, ecommerce, or app-specific examples unless a specific
story needs them. Keep the first import set small so the BheemBhai branding and templates remain
easy to understand.

## Scaffold responsibility

`project-scaffold` is the step that should make these UI conventions real in the repository.

- Create the template tree described above.
- Copy the approved shell assets into the app's static/theme location.
- Set up the base layout files so feature templates can extend them immediately.
- Verify that the copied theme assets are present and referenced correctly before the scaffold is
  considered complete.

That means a fresh scaffold should already have the theme shell available for story work, even if
the individual BheemBhai screens have not been implemented yet.

### Page mapping

| BheemBhai screen | Theme pattern to reuse |
|------------------|------------------------|
| Dashboard home | `index.html` shell, KPI cards, activity panels |
| Projects list / detail | table + card patterns from `tables_data.html` and `box_cards.html` |
| Runs list / detail | table + timeline patterns from `tables_data.html` and `ui_timeline.html` |
| Approvals queue | card, badge, modal, and alert patterns |
| Workflow / policy forms | `forms_general.html` and related form patterns |
| Integration setup | form groups, validation states, and alerts |
| Login / reset / verify | `auth_login.html` and the related auth pages |
| Error pages | `error_404.html` and `error_500.html` |

## Design tokens

The theme supplies the actual visual palette. App code should use semantic CSS variables and
Bootstrap utility classes rather than hardcoded one-off colors.

### Spacing scale

- 4px
- 8px
- 12px
- 16px
- 24px
- 32px

### Color roles

| Role | Value | Use |
|------|-------|-----|
| primary | `var(--bb-primary)` | primary actions, links, active states |
| surface | `var(--bb-surface)` | page background, cards, panels |
| text | `var(--bb-text)` | primary body text |
| muted | `var(--bb-muted)` | helper text, secondary labels |
| error | `var(--bb-danger)` | validation and failure states |
| success | `var(--bb-success)` | completed states and positive status |

### Typography

- Use the theme's body font for all content.
- Use the theme's display or heading font for page titles only if the theme provides one.
- Base text size: 16px.
- Heading scale: Bootstrap headings, with page titles using a distinct top-level size and consistent
  vertical rhythm.

## State and data-loading pattern

- State: local to the page or form by default. There is no global frontend store in the MVP.
- Data loading: full-page server rendering for the primary path, with small fetch-based refreshes
  only for incremental run-status updates and approval actions.
- API client: a thin wrapper around `fetch` for JSON endpoints, used only where progressive
  enhancement is needed.

## Required UI states

- Loading: show a spinner or skeleton when a page depends on async data.
- Error: show a visible, user-readable error panel with the next action.
- Empty: show a distinct empty state for no projects, no runs, or no approvals.
- Success: the normal rendered state.

## Accessibility

- Semantic HTML first.
- Every form control gets a label.
- Keyboard access must work for navigation, tables, filters, and approval actions.
- Visible focus states are required.
- Color contrast must remain WCAG AA compliant.

## Responsive

- Breakpoints: Bootstrap defaults.
- Approach: mobile-first layouts with stacked cards and forms on small screens, then tables and
  side-by-side detail panes on larger screens.

## Patterns

- Tables for run lists and audit history.
- Cards for project summary and status panels.
- Badges for state and result status.
- Inline alerts for errors and approval notices.
- A dedicated approval panel on run detail pages.
- A timeline-style event list for the transition log.
- A compact sidebar nav with project, run, approval, workflow, integration, audit, and admin
  sections.
- Top-right user menu for profile, settings, and logout.

## Asset policy

- Prefer a minimal copied asset set from the theme rather than importing the entire demo bundle.
- Start with theme CSS, icons, and only the JavaScript that is needed for the shell and menus.
- Standardize on one icon set for BheemBhai screens. Do not mix multiple icon families on the same
  page unless a theme component depends on it.
- Keep custom overrides in one BheemBhai theme layer so branding stays centralized.
- If the legacy theme interactions are kept, isolate the jQuery dependency in the shell layer and
  do not let it leak into page-specific story code.
