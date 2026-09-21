from django.urls import path

from . import views

app_name = "key"

urlpatterns = [
    path("", views.KeyListView.as_view(), name="list"),
    path("create/", views.KeyCreateView.as_view(), name="create"),
    path("<int:pk>/", views.KeyDetailView.as_view(), name="detail"),
    path("<int:pk>/revoke/", views.KeyRevokeView.as_view(), name="revoke"),
]
