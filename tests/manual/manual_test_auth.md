# Manual Test — authentication Module

## Pre-conditions
- [ ] DB migrated (V001..V003)
- [ ] User module migrated (V010 from update_module_user.py)
- [ ] Redis running
- [ ] erp_users has test user (id 10000000001)

## Scenarios
| # | Scenario | Endpoint |
|---|----------|----------|
| 1 | Login (email) | POST /authentication/login/ |
| 2 | Login (username) | POST /authentication/login/ |
| 3 | Login (wrong password) | POST /authentication/login/ |
| 4 | Sign Up | POST /authentication/sign-up/ |
| 5 | Refresh | PATCH /authentication/refresh/ |
| 6 | Logout | DELETE /authentication/logout/ |
| 7 | Lock Screen | POST /authentication/lock-screen/ |
| 8 | Two-Step Verification | POST /authentication/two-step-verification/ |
| 9 | Two-Step Code | POST /authentication/two-step-code/ |
| 10 | Forgot Password | POST /authentication/forgot-password/ |
| 11 | Reset Password | POST /authentication/reset-password/ |

## Cookie Verification
- [ ] `token_type` cookie set
- [ ] `access_token` cookie HttpOnly
- [ ] `refresh_token` cookie HttpOnly
- [ ] Logout clears all 3 cookies

## JWT Verification
- [ ] `sub` is user id as string "10000000001"
- [ ] `exp` > `iat` > 0
- [ ] `nbf` >= `iat`

## Sign Up Verification
- [ ] Response has `username`
- [ ] Response `id` >= 10000000000 (11+ digits)
- [ ] Password is hashed (not in response)
