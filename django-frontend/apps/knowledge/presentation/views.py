from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from ..infrastructure.knowledge_client import KnowledgeClient


def _client(request):
    return KnowledgeClient(token=request.session.get("access_token"))


class KnowledgeListView(View):
    template_name = "knowledge/list.html"

    def get(self, request):
        page = int(request.GET.get("page", 1))
        q = request.GET.get("q", "")
        data = _client(request).list_documents(page=page, q=q)
        return render(request, self.template_name, {
            "documents": data["items"], "total": data["total"], "page": page, "q": q,
        })


class KnowledgeDetailView(View):
    template_name = "knowledge/detail.html"

    def get(self, request, pk):
        return render(request, self.template_name, {"doc": _client(request).get_document(pk)})


class KnowledgeCreateView(View):
    template_name = "knowledge/form.html"

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        title = request.POST.get("title", "").strip()
        source = request.POST.get("source", "").strip()
        content = request.POST.get("content", "").strip()
        if not title or not content:
            return render(request, self.template_name, {"error": "Title and content required"}, status=422)
        _client(request).create_document(title=title, source=source, content=content)
        messages.success(request, "Document created.")
        return redirect("knowledge:list")


class KnowledgeDeleteView(View):
    def post(self, request, pk):
        _client(request).delete_document(pk)
        messages.success(request, "Document deleted.")
        return redirect("knowledge:list")
