# The user registered in 04_auth_register_and_duplicate.hurl has no verified email yet
# (this suite has no way to retrieve a real verification email in a black-box run — see
# tests/regression/README.md), so login for that account must be rejected.
POST {{base_url}}/api/v1/auth/login
Content-Type: application/json
{
  "email": "{{new_user_email}}",
  "password": "{{new_user_password}}"
}
HTTP 403


# Wrong password for a real (admin) account.
POST {{base_url}}/api/v1/auth/login
Content-Type: application/json
{
  "email": "{{admin_email}}",
  "password": "definitely-the-wrong-password"
}
HTTP 401


# Unknown email entirely.
POST {{base_url}}/api/v1/auth/login
Content-Type: application/json
{
  "email": "no-such-user-{{run_id}}@example.com",
  "password": "WhateverPassword123!"
}
HTTP 401
