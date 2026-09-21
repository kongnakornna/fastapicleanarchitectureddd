from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Sample home dashboard (uses app_layout)."""
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_settings_page"] = self.request.path.startswith("/settings")
        return ctx
