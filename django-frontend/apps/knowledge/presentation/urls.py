from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("", views.KnowledgeListView.as_view(), name="list"),
    path("create/", views.KnowledgeCreateView.as_view(), name="create"),
    path("<int:pk>/", views.KnowledgeDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.KnowledgeDeleteView.as_view(), name="delete"),
]
