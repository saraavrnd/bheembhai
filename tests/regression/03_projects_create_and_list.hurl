# Runs as the admin session established in 02_auth_admin_login.hurl.

POST {{base_url}}/api/v1/projects
Content-Type: application/json
{
  "name": "Regression Suite Project {{run_id}}"
}
HTTP 201
[Captures]
project_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Regression Suite Project {{run_id}}"
jsonpath "$.activeWorkflowVersionId" == null
jsonpath "$.activePolicyVersionId" == null


GET {{base_url}}/api/v1/projects
HTTP 200
[Asserts]
jsonpath "$.items[?(@.id=='{{project_id}}')].id" == "{{project_id}}"
jsonpath "$.items[?(@.id=='{{project_id}}')].name" == "Regression Suite Project {{run_id}}"


# Blank/whitespace-only name is rejected (422) and creates nothing — see BEEM-12 code-review.md.
POST {{base_url}}/api/v1/projects
Content-Type: application/json
{
  "name": "   "
}
HTTP 422


# Name exceeding the projects.name column's 255-char limit is rejected (422).
POST {{base_url}}/api/v1/projects
Content-Type: application/json
{
  "name": "{{oversized_project_name}}"
}
HTTP 422
