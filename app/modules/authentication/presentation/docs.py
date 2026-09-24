from __future__ import annotations

from http import HTTPStatus

from app.modules.authentication.presentation.schemas import (
    ForgotPasswordResponse,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordResponse,
    SignUpResponse,
    TwoStepCodeResponse,
    TwoStepVerificationResponse,
)
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse

# ============================================================================
# MODULE DOCS
# ============================================================================
router_docs = {
    "prefix": "/api/v1/authentication",
    "tags": ["Authentication"],
    "responses": {
        400: {"model": StandardResponse, "description": "Bad Request"},
        401: {"model": StandardResponse, "description": "Unauthorized"},
        403: {"model": StandardResponse, "description": "Forbidden"},
        405: {"model": StandardResponse, "description": "Method Not Allowed"},
        422: {"model": StandardResponse, "description": "Form Validation Error"},
        500: {"model": StandardResponse, "description": "Internal Server Error"},
        502: {"model": StandardResponse, "description": "Bad Gateway"},
        504: {"model": StandardResponse, "description": "Gateway Timeout"},
    },
}


# ============================================================================
# LOGIN DOCS
# ============================================================================
login_docs = {
    "summary": "Endpoint to login a user.",
    "description": (
        "Authenticate a user and initiate a login session. "
        "Authentication tokens are returned via HttpOnly cookies."
    ),
    "response_description": (
        "Successful authentication. Access/refresh tokens are set in cookies and "
        "the JSON body returns tokens + user info."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LoginResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful login response (cookies + tokens + user info)",
            "model": LoginResponse,
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to set `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": "access_token=<token>; HttpOnly; Path=/; SameSite=lax",
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Login Success": {
                            "summary": "Login response with tokens and user info",
                            "value": {
                                "message": ResponseMessages.LOGIN_SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
                                "info": {
                                    "first_name": "System",
                                    "last_name": "Admin",
                                    "preferred_name": "Admin",
                                    "gender": "other",
                                    "birthdate": "1990-01-01",
                                    "email": "admin@example.com",
                                    "phone": None,
                                    "role": "admin",
                                    "created_at": "2026-09-19T08:57:37.641459Z",
                                },
                            },
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# SIGN UP DOCS
# ============================================================================
sign_up_docs = {
    "summary": "Endpoint to sign up a new user.",
    "description": (
        "Create a new user account. Public endpoint — no authentication is required."
    ),
    "response_description": "Successful sign up.",
    "status_code": HTTPStatus.CREATED,
    "response_model": SignUpResponse,
    "include_in_schema": True,
    "responses": {
        201: {
            "description": "User created successfully",
            "model": SignUpResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Sign Up Success": {
                            "summary": "User signed up successfully",
                            "value": {"message": ResponseMessages.CREATED.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# REFRESH DOCS
# ============================================================================
refresh_docs = {
    "summary": "Endpoint to refresh authentication tokens.",
    "description": (
        "Validates the `refresh_token` from HttpOnly cookies using `refresh_tokens` "
        "security dependency, then rotates and sets new `token_type`, `access_token`, "
        "and `refresh_token` cookies."
    ),
    "response_description": (
        "Successful token refresh. New access/refresh tokens and token type are set "
        "in cookies, and the JSON body returns a refresh confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": RefreshResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful refresh response",
            "model": RefreshResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Refresh Success": {
                            "summary": "Refresh token generated successfully",
                            "value": {
                                "message": ResponseMessages.REFRESH_SUCCESS.value
                            },
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOGOUT DOCS
# ============================================================================
logout_docs = {
    "summary": "Endpoint to logout a user.",
    "description": (
        "Invalidates the authenticated session and removes authentication cookies. "
        "The endpoint requires a valid authenticated user."
    ),
    "response_description": (
        "Successful logout. Authentication cookies are removed and the JSON body "
        "returns a logout confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LogoutResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful logout response",
            "model": LogoutResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Logout Success": {
                            "summary": "User logged out successfully",
                            "value": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# FORGOT PASSWORD DOCS
# ============================================================================
forgot_password_docs = {
    "summary": "Endpoint to request password reset.",
    "description": (
        "Send a password reset code to the user's email address. "
        "Always returns success to avoid revealing whether the email exists."
    ),
    "response_description": "Reset code sent (if email exists).",
    "status_code": HTTPStatus.OK,
    "response_model": ForgotPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Forgot password request processed",
            "model": ForgotPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Forgot Password Success": {
                            "summary": "Reset code sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# RESET PASSWORD DOCS
# ============================================================================
reset_password_docs = {
    "summary": "Endpoint to reset password with code.",
    "description": "Validate the reset code and set a new password for the user.",
    "response_description": "Password reset successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": ResetPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Password reset successfully",
            "model": ResetPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Reset Password Success": {
                            "summary": "Password reset successfully",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOCK SCREEN DOCS
# ============================================================================
lock_screen_docs = {
    "summary": "Endpoint to unlock the screen.",
    "description": (
        "Validate the user's password to unlock a locked screen. "
        "Requires a valid authenticated session."
    ),
    "response_description": "Screen unlocked successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": LockScreenResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Screen unlocked successfully",
            "model": LockScreenResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Lock Screen Success": {
                            "summary": "Screen unlocked",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP VERIFICATION DOCS
# ============================================================================
two_step_verification_docs = {
    "summary": "Endpoint to initiate two-step verification.",
    "description": (
        "Send an OTP code to the specified phone number for two-step verification."
    ),
    "response_description": "OTP sent successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepVerificationResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP sent successfully",
            "model": TwoStepVerificationResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Verification Success": {
                            "summary": "OTP sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP CODE DOCS
# ============================================================================
two_step_code_docs = {
    "summary": "Endpoint to verify two-step code.",
    "description": "Validate the OTP code and issue authentication tokens.",
    "response_description": "OTP verified successfully, tokens issued.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepCodeResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP verified successfully",
            "model": TwoStepCodeResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Code Success": {
                            "summary": "OTP verified, tokens issued",
                            "value": {
                                "message": ResponseMessages.SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
                            },
                        }
                    }
                }
            },
        },
    },
}
