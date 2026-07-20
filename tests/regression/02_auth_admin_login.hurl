# The admin account is bootstrapped by run.sh (via `beembhai-admin bootstrap-admin --verified`)
# before this suite runs, so it is already email-verified and can log in directly.

POST {{base_url}}/api/v1/auth/login
Content-Type: application/json
{
  "email": "{{admin_email}}",
  "password": "{{admin_password}}"
}
HTTP 200
[Asserts]
jsonpath "$.user.email" == "{{admin_email}}"
jsonpath "$.user.platformRole" == "PLATFORM_ADMIN"
jsonpath "$.user.emailVerifiedAt" isString


# The session cookie set above (shared via the run.sh cookie jar) now authenticates this request.
GET {{base_url}}/api/v1/me
HTTP 200
[Asserts]
jsonpath "$.user.email" == "{{admin_email}}"
jsonpath "$.user.platformRole" == "PLATFORM_ADMIN"
jsonpath "$.memberships" count == 0
