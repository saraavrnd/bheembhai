# No session cookie exists yet at this point in the run (the shared cookie jar starts empty
# and no prior file has logged in) — protected endpoints must reject the request.

GET {{base_url}}/api/v1/me
HTTP 401


GET {{base_url}}/api/v1/projects
HTTP 401
