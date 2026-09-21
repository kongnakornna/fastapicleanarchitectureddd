from django import forms

MODULE_CHOICES = [
    "dashboard", "customer", "quotation", "purchase_order", "inventory",
    "payment", "document", "email", "batch", "iot", "wos", "job_card",
    "user", "role", "key", "knowledge", "notification",
]


class RoleForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    permissions = forms.MultipleChoiceField(
        required=False,
        choices=[(m, m) for m in MODULE_CHOICES],
        widget=forms.CheckboxSelectMultiple,
    )


class UserForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    full_name = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20, required=False)
    role_id = forms.IntegerField(widget=forms.HiddenInput, initial=2)
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        min_length=8,
        help_text="Leave blank to keep current password",
    )
    is_active = forms.BooleanField(required=False, initial=True)
