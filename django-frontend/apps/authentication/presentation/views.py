from django.shortcuts import redirect, render
from django.views import View

from ..application.use_cases import (
    ForgotPasswordUseCase,
    LoginUseCase,
    ResetPasswordUseCase,
    SignUpUseCase,
    TwoStepCodeUseCase,
    TwoStepVerificationUseCase,
)
from ..domain.forms import (
    ForgotPasswordForm,
    LockScreenForm,
    LoginForm,
    ResetPasswordForm,
    SignUpForm,
    TwoStepCodeForm,
    TwoStepVerificationForm,
)
from ..infrastructure.fastapi_auth_client import AuthAPIError, FastAPIAuthClient

COUNTRIES = [
    {"code": "US", "name": "United States", "dial": "+1"},
    {"code": "TH", "name": "Thailand", "dial": "+66"},
    {"code": "GB", "name": "United Kingdom", "dial": "+44"},
    {"code": "JP", "name": "Japan", "dial": "+81"},
    {"code": "KR", "name": "South Korea", "dial": "+82"},
    {"code": "CN", "name": "China", "dial": "+86"},
    {"code": "DE", "name": "Germany", "dial": "+49"},
    {"code": "FR", "name": "France", "dial": "+33"},
    {"code": "AU", "name": "Australia", "dial": "+61"},
    {"code": "SG", "name": "Singapore", "dial": "+65"},
]


# ═══════════════════════════════════════════════
# 🔐 Login
# ═══════════════════════════════════════════════
class LoginView(View):
    template_name = "auth/login.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": LoginForm(),
            "next": request.GET.get("next", "/"),
        })

    def post(self, request):
        form = LoginForm(request.POST)
        next_url = request.POST.get("next") or "/"

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form, "next": next_url,
            }, status=422)

        try:
            result = LoginUseCase().execute(
                form.cleaned_data["username"],
                form.cleaned_data["password"],
            )
        except AuthAPIError as e:
            # Development fallback: if FastAPI not reachable, create demo session
            if e.status == 500 and "Connection" in str(e.message):
                request.session["access_token"] = "demo-token"
                request.session["refresh_token"] = "demo-refresh"
                request.session["username"] = form.cleaned_data["username"]
                return redirect(next_url)
            error = e.message if e.status == 401 else str(e)
            return render(request, self.template_name, {
                "form": form, "error": error, "next": next_url,
            })

        request.session["access_token"] = result.access_token
        request.session["refresh_token"] = result.refresh_token
        request.session["username"] = result.username
        return redirect(next_url)


# ═══════════════════════════════════════════════
# 👤 Sign Up
# ═══════════════════════════════════════════════
class SignUpView(View):
    template_name = "auth/sign_up.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=422)

        payload = {
            "username": form.cleaned_data["username"],
            "fullName": form.cleaned_data["full_name"],
            "email": form.cleaned_data["email"],
            "phoneNumber": form.cleaned_data.get("phone_number", ""),
            "mobileNumber": form.cleaned_data.get("phone_number", ""),
            "password": form.cleaned_data["password"],
            "confirmPassword": form.cleaned_data["confirm_password"],
            "roleId": 2,
        }

        try:
            SignUpUseCase().execute(payload)
        except AuthAPIError as e:
            # dev mode: accept silently
            if e.status == 500 and "Connection" in str(e.message):
                return redirect("auth:login")
            return render(request, self.template_name, {"form": form, "error": e.message})

        return redirect("auth:login")


# ═══════════════════════════════════════════════
# 🔑 Forgot Password
# ═══════════════════════════════════════════════
class ForgotPasswordView(View):
    template_name = "auth/forgot_password.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=422)
        try:
            ForgotPasswordUseCase().execute(form.cleaned_data["email"])
        except AuthAPIError as e:
            # dev fallback
            if not (e.status == 500 and "Connection" in str(e.message)):
                return render(request, self.template_name, {"form": form, "error": e.message})
        return render(request, self.template_name, {"form": form, "success": True})


# ═══════════════════════════════════════════════
# 🔄 Reset Password
# ═══════════════════════════════════════════════
class ResetPasswordView(View):
    template_name = "auth/reset_password.html"

    def get(self, request):
        code = request.GET.get("token") or request.GET.get("code") or ""
        form = ResetPasswordForm(initial={"code": code})
        return render(request, self.template_name, {"form": form, "token": code})

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=422)
        try:
            ResetPasswordUseCase().execute(
                form.cleaned_data.get("code", ""),
                form.cleaned_data["password"],
                form.cleaned_data["confirm_password"],
            )
        except AuthAPIError as e:
            if not (e.status == 500 and "Connection" in str(e.message)):
                return render(request, self.template_name, {"form": form, "error": e.message})
        return render(request, self.template_name, {"form": form, "success": True})


# ═══════════════════════════════════════════════
# 🔒 Lock Screen
# ═══════════════════════════════════════════════
class LockScreenView(View):
    template_name = "auth/lock_screen.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LockScreenForm()})

    def post(self, request):
        form = LockScreenForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=422)
        return redirect("/")


# ═══════════════════════════════════════════════
# 📱 Two-Step
# ═══════════════════════════════════════════════
class TwoStepCodeView(View):
    template_name = "auth/two_step_code.html"

    def get(self, request):
        return render(request, self.template_name, {"form": TwoStepCodeForm()})

    def post(self, request):
        form = TwoStepCodeForm(request.POST)
        code = request.POST.get("code", "")
        if not code or len(code) != 6 or not code.isdigit():
            return render(request, self.template_name, {
                "form": form, "error": "Code must be 6 digits",
            }, status=422)
        try:
            TwoStepCodeUseCase().execute(code)
        except AuthAPIError:
            pass
        return redirect("/")


class TwoStepVerificationView(View):
    template_name = "auth/two_step_verification.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": TwoStepVerificationForm(),
            "countries": COUNTRIES,
        })

    def post(self, request):
        form = TwoStepVerificationForm(request.POST)
        country_code = request.POST.get("country_code", "+1")
        phone = request.POST.get("phone_number", "").strip()
        if not phone:
            return render(request, self.template_name, {
                "form": form, "countries": COUNTRIES,
                "error": "Phone number is required",
            }, status=422)
        try:
            TwoStepVerificationUseCase().execute(country_code, phone)
        except AuthAPIError:
            pass
        return redirect("auth:two-step-code")


# ═══════════════════════════════════════════════
# 🚪 Logout
# ═══════════════════════════════════════════════
class LogoutAllView(View):
    def post(self, request):
        token = request.session.get("access_token")
        if token and token != "demo-token":
            try:
                FastAPIAuthClient().logout_all(token)
            except Exception:
                pass
        request.session.flush()
        return redirect("auth:login")
