# The admin session from 02_auth_admin_login.hurl is still active here — none of the
# intervening requests touched it (failed logins don't clear an existing session).

POST {{base_url}}/api/v1/auth/logout
HTTP 204


GET {{base_url}}/api/v1/me
HTTP 401
