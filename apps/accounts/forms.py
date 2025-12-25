from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


# --- MIXIN DE FORMATAÇÃO ---
class UserFormattingMixin:
    """Mixin para padronizar nomes (Title Case) e validar e-mails."""

    def clean_first_name(self):
        name = self.cleaned_data.get("first_name")
        if name:
            if len(name) < 2:
                raise forms.ValidationError("O nome deve ter pelo menos 2 letras.")
            return name.title().strip()  # Ex: "joão" -> "João"
        return name

    def clean_last_name(self):
        name = self.cleaned_data.get("last_name")
        if name:
            if len(name) < 2:
                raise forms.ValidationError("O sobrenome deve ter pelo menos 2 letras.")
            return name.title().strip()  # Ex: "silva" -> "Silva"
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Verifica se já existe outro usuário com esse e-mail
            # Exclui o próprio usuário da busca (caso seja uma edição)
            qs = CustomUser.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "Este e-mail já está em uso por outro usuário."
                )
            return email.lower().strip()  # Sempre minúsculo
        return email


# --- FORMS DE REGISTRO / ADMIN ---


class CustomUserCreationForm(UserFormattingMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors text-slate-900 dark:text-white placeholder-slate-400'
            field.widget.attrs['placeholder'] = field.label


class CustomUserChangeForm(UserFormattingMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")


# --- FORM DE PERFIL (USADO PELO USUÁRIO) ---


class UserUpdateForm(UserFormattingMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                    "placeholder": "Seu primeiro nome",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                    "placeholder": "Seu sobrenome",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
        }
