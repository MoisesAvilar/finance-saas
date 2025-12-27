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

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        count = self.get_queryset().count()

        if user.is_pro:
            can_add = True
        else:
            can_add = count < 1

        context["can_add_vehicle"] = can_add
        context["vehicle_count"] = count
        return context


class VehicleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicle_list")
    success_message = "Veículo cadastrado com sucesso!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_pro:
            count = Vehicle.objects.filter(user=request.user).count()
            if count >= 1:
                messages.warning(
                    request,
                    "🔒 Limite atingido! No plano Grátis você pode ter apenas 1 veículo ativo.",
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
