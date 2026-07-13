# Test Plan - BEEM-17: Register a local user account

## Scenario to test mapping

| Acceptance scenario | Test coverage |
|---------------------|---------------|
| New user registration creates an account | [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_creates_standard_user_and_sends_verification_email` and [tests/integration/auth/test_register.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/integration/auth/test_register.py) `test_register_endpoint_creates_user_and_returns_user_shape` |
| Registration sends a verification email | [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_creates_standard_user_and_sends_verification_email` |
| Duplicate email registration is rejected | [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_rejects_duplicate_email_without_creating_duplicate_user` |
| Invalid registration input is rejected | [tests/integration/auth/test_register.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/integration/auth/test_register.py) `test_register_endpoint_rejects_invalid_input` |

## Notes

- The unit tests exercise `AuthService.register_user(...)` against a real in-memory SQLite repository and a fake email sender.
- The integration test uses a real temporary SQLite database and verifies the API response plus persisted `users` row.
