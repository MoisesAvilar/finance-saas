from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import CustomUser


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    success_message = "Conta criada com sucesso! Faça login para começar."

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao criar conta. Verifique os dados abaixo.")
        return super().form_invalid(form)


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = "registration/login.html"
    success_message = "Bem-vindo de volta!"

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha inválidos.")
        return super().form_invalid(form)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "registration/profile_form.html"
    success_url = reverse_lazy("profile_update")
    success_message = "Dados do perfil atualizados com sucesso!"

    def get_object(self):
        return self.request.user


class CustomPasswordChangeView(
    LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView
):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("profile_update")
    success_message = "Sua senha foi alterada com sucesso."
