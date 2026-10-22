from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User


class UserSignUpForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Minimum 8 caractères", "id": "signup-password"}),
        validators=[validate_password]
    )
    password_confirm = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Retapez votre mot de passe", "id": "signup-password-confirm"})
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="J'accepte les Conditions Générales d'Utilisation et la Politique de Confidentialité.",
        widget=forms.CheckboxInput(attrs={"id": "signup-terms"})
    )
    newsletter_accepted = forms.BooleanField(
        required=False,
        initial=False,
        label="Je souhaite recevoir la newsletter technique et les offres de formations (facultatif).",
        widget=forms.CheckboxInput(attrs={"id": "signup-newsletter"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "terms_accepted", "newsletter_accepted"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur / pseudo", "id": "signup-username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "nom@exemple.com", "id": "signup-email"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom", "id": "signup-firstname"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom de famille", "id": "signup-lastname"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Un compte existe déjà avec cette adresse email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.email = self.cleaned_data["email"].lower().strip()
        if self.cleaned_data.get("newsletter_accepted"):
            user.newsletter_consent_date = timezone.now()
        if commit:
            user.save()
            # Also register in NewsletterSubscriber if consented
            if user.newsletter_accepted:
                from marketing.models import NewsletterSubscriber
                NewsletterSubscriber.objects.get_or_create(
                    email=user.email,
                    defaults={
                        "first_name": user.first_name,
                        "source": "registration_optin",
                        "consent_given": True,
                        "consent_timestamp": timezone.now(),
                    }
                )
        return user


class UserLoginForm(forms.Form):
    login = forms.CharField(
        label="Email ou Nom d'utilisateur",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre email ou pseudo", "id": "login-identifier"})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Votre mot de passe", "id": "login-password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        login_val = cleaned_data.get("login")
        password_val = cleaned_data.get("password")

        if login_val and password_val:
            user = authenticate(username=login_val, password=password_val)
            if not user:
                raise ValidationError("Identifiants invalides. Vérifiez votre email et mot de passe.")
            if not user.is_active:
                raise ValidationError("Ce compte est actuellement désactivé.")
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar", "bio", "phone", "newsletter_accepted"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "id": "profile-firstname"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "id": "profile-lastname"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "id": "profile-bio"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "id": "profile-phone"}),
            "newsletter_accepted": forms.CheckboxInput(attrs={"id": "profile-newsletter"}),
        }
