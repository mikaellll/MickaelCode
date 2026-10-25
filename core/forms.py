from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field: invisible to humans, filled by spam bots
    bot_field = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "style": "display:none",
            "tabindex": "-1",
            "autocomplete": "off",
            "aria-hidden": "true",
        }),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-1.5 font-lato text-[14px] text-white bg-black/40 border-2 border-white/10 rounded-[10px] outline-none transition-all duration-300 focus:border-cyan focus:bg-cyan/5 placeholder-gray-500 h-[42px]",
                "placeholder": "Votre nom",
                "required": True,
                "id": "contact-name",
                "maxlength": 100,
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3.5 py-1.5 font-lato text-[14px] text-white bg-black/40 border-2 border-white/10 rounded-[10px] outline-none transition-all duration-300 focus:border-cyan focus:bg-cyan/5 placeholder-gray-500 h-[42px]",
                "placeholder": "votre@email.com",
                "required": True,
                "id": "contact-email",
                "maxlength": 254,
            }),
            "subject": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-1.5 font-lato text-[14px] text-white bg-black/40 border-2 border-white/10 rounded-[10px] outline-none transition-all duration-300 focus:border-cyan focus:bg-cyan/5 placeholder-gray-500 h-[42px]",
                "placeholder": "Sujet de votre message",
                "required": True,
                "id": "contact-subject",
                "maxlength": 200,
            }),
            "message": forms.Textarea(attrs={
                "class": "w-full px-3.5 py-2 font-lato text-[14px] text-white bg-black/40 border-2 border-white/10 rounded-[10px] outline-none transition-all duration-300 focus:border-cyan focus:bg-cyan/5 placeholder-gray-500 resize-y h-[90px] min-h-[75px] max-h-[140px]",
                "rows": 3,
                "placeholder": "Votre message...",
                "required": True,
                "id": "contact-message",
                "maxlength": 5000,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].required = True

    def clean_bot_field(self):
        bot_val = self.cleaned_data.get("bot_field")
        if bot_val:
            raise forms.ValidationError("Activité suspecte détectée.")
        return bot_val

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if "\r" in name or "\n" in name:
            raise forms.ValidationError("Caractères non autorisés détectés.")
        if len(name) < 2:
            raise forms.ValidationError("Veuillez renseigner un nom valide (au moins 2 caractères).")
        return name

    def clean_subject(self):
        subject = self.cleaned_data.get("subject", "").strip()
        if "\r" in subject or "\n" in subject:
            raise forms.ValidationError("Caractères non autorisés détectés.")
        if not subject:
            raise forms.ValidationError("Veuillez préciser le sujet de votre message.")
        return subject

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 5:
            raise forms.ValidationError("Votre message est trop court (au moins 5 caractères).")
        return message

