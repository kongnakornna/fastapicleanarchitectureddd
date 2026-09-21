from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from apps.shared.application.exceptions import NotFoundException, StandardException

from ..domain.forms import MODULE_CHOICES, RoleForm, UserForm
from ..domain.use_cases import (
    CreateRoleUseCase,
    CreateUserUseCase,
    DeleteRoleUseCase,
    DeleteUserUseCase,
    GetRoleUseCase,
    GetUserUseCase,
    ListRolesUseCase,
    ListUsersUseCase,
    UpdateRoleUseCase,
    UpdateUserUseCase,
)
from ..infrastructure.user_client import UserClient


def _client(request):
    return UserClient(token=request.session.get("access_token"))


# ═══════════════════════════════════════════════
# 👤 Users
# ═══════════════════════════════════════════════
class UserListView(View):
    template_name = "user/list.html"

    def get(self, request):
        page = int(request.GET.get("page", 1))
        q = request.GET.get("q", "")
        data = ListUsersUseCase(_client(request)).execute(page=page, q=q)
        return render(request, self.template_name, {
            "users": data["items"], "total": data["total"], "page": page, "q": q,
        })


class UserDetailView(View):
    template_name = "user/detail.html"

    def get(self, request, pk):
        try:
            user = GetUserUseCase(_client(request)).execute(pk)
        except Exception:
            raise NotFoundException()
        return render(request, self.template_name, {"user": user})


class UserCreateView(View):
    template_name = "user/form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": UserForm()})

    def post(self, request):
        form = UserForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=422)
        try:
            CreateUserUseCase(_client(request)).execute({
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "fullName": form.cleaned_data["full_name"],
                "phoneNumber": form.cleaned_data.get("phone_number", ""),
                "roleId": form.cleaned_data["role_id"],
                "password": form.cleaned_data.get("password") or "changeme123",
                "isActive": form.cleaned_data.get("is_active", True),
            })
        except StandardException as e:
            return render(request, self.template_name, {"form": form, "error": e.message})
        messages.success(request, "User created.")
        return redirect("user:list")


class UserEditView(View):
    template_name = "user/form.html"

    def get(self, request, pk):
        user = GetUserUseCase(_client(request)).execute(pk)
        form = UserForm(initial={
            "username": user.username, "email": user.email,
            "full_name": user.full_name, "phone_number": user.phone_number,
            "role_id": user.role_id, "is_active": user.is_active,
        })
        return render(request, self.template_name, {"form": form, "user_id": pk})

    def post(self, request, pk):
        form = UserForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "user_id": pk}, status=422)
        payload = {
            "username": form.cleaned_data["username"],
            "email": form.cleaned_data["email"],
            "fullName": form.cleaned_data["full_name"],
            "phoneNumber": form.cleaned_data.get("phone_number", ""),
            "roleId": form.cleaned_data["role_id"],
            "isActive": form.cleaned_data.get("is_active", True),
        }
        if form.cleaned_data.get("password"):
            payload["password"] = form.cleaned_data["password"]
        try:
            UpdateUserUseCase(_client(request)).execute(pk, payload)
        except StandardException as e:
            return render(request, self.template_name, {"form": form, "user_id": pk, "error": e.message})
        messages.success(request, "User updated.")
        return redirect("user:list")


class UserDeleteView(View):
    def post(self, request, pk):
        DeleteUserUseCase(_client(request)).execute(pk)
        messages.success(request, "User deleted.")
        return redirect("user:list")


class MeView(View):
    template_name = "user/me.html"

    def get(self, request):
        # FastAPI /auth/me
        from apps.shared.infrastructure.fastapi_client import fastapi
        try:
            data = fastapi.json("GET", "/auth/me", token=request.session.get("access_token"))
        except Exception:
            data = {"username": request.session.get("username", "")}
        return render(request, self.template_name, {"me": data})


# ═══════════════════════════════════════════════
# 🔐 Roles
# ═══════════════════════════════════════════════
class RoleListView(View):
    template_name = "user/roles/list.html"

    def get(self, request):
        roles = ListRolesUseCase(_client(request)).execute()
        return render(request, self.template_name, {"roles": roles})


class RoleCreateView(View):
    template_name = "user/roles/create.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RoleForm(), "modules": MODULE_CHOICES})

    def post(self, request):
        form = RoleForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form, "modules": MODULE_CHOICES,
            }, status=422)
        try:
            CreateRoleUseCase(_client(request)).execute({
                "name": form.cleaned_data["name"],
                "description": form.cleaned_data.get("description", ""),
                "permissions": form.cleaned_data.get("permissions", []),
            })
        except StandardException as e:
            return render(request, self.template_name, {
                "form": form, "modules": MODULE_CHOICES, "error": e.message,
            })
        return redirect("user:role-list")


class RoleDetailView(View):
    template_name = "user/roles/detail.html"

    def get(self, request, pk):
        role = GetRoleUseCase(_client(request)).execute(pk)
        return render(request, self.template_name, {"role": role, "role_id": pk})

    def post(self, request, pk):
        if request.POST.get("_method") == "DELETE":
            DeleteRoleUseCase(_client(request)).execute(pk)
            return redirect("user:role-list")
        return self.get(request, pk)


class RoleEditView(View):
    template_name = "user/roles/edit.html"

    def get(self, request, pk):
        role = GetRoleUseCase(_client(request)).execute(pk)
        form = RoleForm(initial={
            "name": role.name, "description": role.description,
            "permissions": role.permissions,
        })
        return render(request, self.template_name, {
            "form": form, "modules": MODULE_CHOICES, "role_id": pk,
        })

    def post(self, request, pk):
        form = RoleForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form, "modules": MODULE_CHOICES, "role_id": pk,
            }, status=422)
        try:
            UpdateRoleUseCase(_client(request)).execute(pk, {
                "name": form.cleaned_data["name"],
                "description": form.cleaned_data.get("description", ""),
                "permissions": form.cleaned_data.get("permissions", []),
            })
        except StandardException as e:
            return render(request, self.template_name, {
                "form": form, "modules": MODULE_CHOICES,
                "role_id": pk, "error": e.message,
            })
        return redirect("user:role-list")
