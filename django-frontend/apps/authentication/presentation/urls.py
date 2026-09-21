from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("lock-screen/", views.LockScreenView.as_view(), name="lock-screen"),
    path("two-step-code/", views.TwoStepCodeView.as_view(), name="two-step-code"),
    path("two-step-verification/", views.TwoStepVerificationView.as_view(), name="two-step-verification"),
    path("logout-all/", views.LogoutAllView.as_view(), name="logout-all"),
]
