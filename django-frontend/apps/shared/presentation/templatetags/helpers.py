from django import template

register = template.Library()


@register.filter
def split(value: str, sep: str = ",") -> list[str]:
    """'a,b,c' | split:','  → ['a','b','c']"""
    return value.split(sep)


@register.filter
def add_class(field, css_class: str):
    """Append CSS class to a Django form field widget."""
    return field.as_widget(attrs={"class": f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()})


@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    """Replace query params keeping existing ones."""
    q = context["request"].GET.copy()
    for k, v in kwargs.items():
        q[k] = v
    return q.urlencode()
