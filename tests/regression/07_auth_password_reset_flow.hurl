# Password-reset request always returns 204 whether or not the email exists, so the endpoint
# never reveals which emails are registered (no user enumeration).

POST {{base_url}}/api/v1/auth/password-reset/request
Content-Type: application/json
{
  "email": "no-such-user-{{run_id}}@example.com"
}
HTTP 204


POST {{base_url}}/api/v1/auth/password-reset/request
Content-Type: application/json
{
  "email": "{{new_user_email}}"
}
HTTP 204


# Confirming with a token that was never issued is rejected.
POST {{base_url}}/api/v1/auth/password-reset/confirm
Content-Type: application/json
{
  "token": "not-a-real-token",
  "newPassword": "SomeNewPassword123!"
}
HTTP 400
