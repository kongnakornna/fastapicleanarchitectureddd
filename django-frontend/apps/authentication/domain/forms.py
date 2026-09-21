from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
            "autocomplete": "username",
            "required": True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "autocomplete": "current-password",
            "required": True,
        }),
    )


class SignUpForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Full name", "required": True,
    }))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Username", "required": True,
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control", "placeholder": "your@email.com", "required": True,
    }))
    phone_number = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Phone number",
    }))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "Password",
        "autocomplete": "new-password", "required": True,
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "Confirm password",
        "autocomplete": "new-password", "required": True,
    }))
    agree_terms = forms.BooleanField(required=True)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") and cleaned.get("confirm_password"):
            if cleaned["password"] != cleaned["confirm_password"]:
                raise forms.ValidationError("Passwords do not match")
        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control", "placeholder": "your@email.com", "required": True,
    }))


class ResetPasswordForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput(), required=False)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "New password",
        "autocomplete": "new-password", "required": True,
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "Confirm password",
        "autocomplete": "new-password", "required": True,
    }))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned


class LockScreenForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "Password",
        "autocomplete": "current-password", "required": True,
    }))


class TwoStepCodeForm(forms.Form):
    code = forms.CharField(min_length=6, max_length=6, required=False)


class TwoStepVerificationForm(forms.Form):
    country_code = forms.CharField(max_length=5, initial="+1", widget=forms.HiddenInput())
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Phone number",
    }))
