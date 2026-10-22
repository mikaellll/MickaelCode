from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Votre nom ou entreprise",
                "required": True,
                "id": "contact-name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "nom@exemple.com",
                "required": True,
                "id": "contact-email"
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Objet de votre projet ou question",
                "id": "contact-subject"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Décrivez votre besoin, planning, budget ou questions...",
                "required": True,
                "id": "contact-message"
            }),
        }
