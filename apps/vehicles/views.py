from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect
from .models import Vehicle
from .forms import VehicleForm


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ativos_count = self.object_list.filter(is_active=True).count()
        context["can_add_vehicle"] = ativos_count < 1
        return context


class VehicleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicle_list")
    success_message = "Veículo adicionado à sua frota com sucesso!"

    def dispatch(self, request, *args, **kwargs):
        user_vehicle_count = Vehicle.objects.filter(user=request.user).count()

        if not request.user.is_superuser and user_vehicle_count >= 1:
            messages.warning(
                request,
                "⛔ No plano Grátis você pode ter apenas 1 veículo. Faça o Upgrade para gerenciar uma frota!",
            )
            return redirect("vehicle_list")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class VehicleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicle_list")
    success_message = "Dados do veículo atualizados!"

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)


class VehicleDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Vehicle
    template_name = "generics/confirm_delete.html"
    success_url = reverse_lazy("vehicle_list")
    success_message = "Veículo removido com sucesso."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Veículo"
        context["cancel_url"] = reverse_lazy("vehicle_list")
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(VehicleDeleteView, self).delete(request, *args, **kwargs)
