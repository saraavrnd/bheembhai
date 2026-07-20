POST {{base_url}}/api/v1/auth/register
Content-Type: application/json
{
  "email": "{{new_user_email}}",
  "password": "{{new_user_password}}"
}
HTTP 201
[Asserts]
jsonpath "$.email" == "{{new_user_email}}"
jsonpath "$.platformRole" == "STANDARD"
jsonpath "$.emailVerifiedAt" == null


# Registering the same email again is rejected — no duplicate user is created.
POST {{base_url}}/api/v1/auth/register
Content-Type: application/json
{
  "email": "{{new_user_email}}",
  "password": "{{new_user_password}}"
}
HTTP 409


# Malformed email is rejected before it ever reaches the service layer.
POST {{base_url}}/api/v1/auth/register
Content-Type: application/json
{
  "email": "not-an-email",
  "password": "{{new_user_password}}"
}
HTTP 422
