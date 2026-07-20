POST {{base_url}}/api/v1/auth/email/verify
Content-Type: application/json
{
  "token": "not-a-real-token"
}
HTTP 400
