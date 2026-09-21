from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    # 👤 Users
    path("users/", views.UserListView.as_view(), name="list"),
    path("users/create/", views.UserCreateView.as_view(), name="create"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="detail"),
    path("users/<int:pk>/edit/", views.UserEditView.as_view(), name="edit"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="delete"),
    path("me/", views.MeView.as_view(), name="me"),

    # 🔐 Roles
    path("roles/", views.RoleListView.as_view(), name="role-list"),
    path("roles/create/", views.RoleCreateView.as_view(), name="role-create"),
    path("roles/<int:pk>/", views.RoleDetailView.as_view(), name="role-detail"),
    path("roles/<int:pk>/edit/", views.RoleEditView.as_view(), name="role-edit"),
]
