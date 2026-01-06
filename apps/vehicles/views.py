from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.contrib import messages
from django.shortcuts import redirect
from .models import Vehicle
from .forms import VehicleForm
from django.db.models import Sum, Max, Min
from operations.models import Transaction, Maintenance


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


class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object
        is_pro = self.request.user.is_pro

        fuel_transactions = Transaction.objects.filter(
            record__vehicle=vehicle, category__is_fuel=True, liters__gt=0
        ).order_by("actual_km")

        fuel_history = []
        last_full_tank = None

        pending_liters = 0
        pending_cost = 0

        for trans in fuel_transactions:
            item = {
                "date": trans.created_at,
                "km": trans.actual_km,
                "liters": trans.liters,
                "cost": trans.amount,
                "is_full": trans.is_full_tank,
                "avg": None,
                "cost_per_km": None,
            }

            if last_full_tank and trans.is_full_tank:
                km_driven = trans.actual_km - last_full_tank.actual_km
                total_liters_cycle = pending_liters + trans.liters
                total_cost_cycle = pending_cost + trans.amount

                if km_driven > 0 and total_liters_cycle > 0:
                    item["avg"] = km_driven / float(total_liters_cycle)
                    item["cost_per_km"] = float(total_cost_cycle) / km_driven

                pending_liters = 0
                pending_cost = 0
                last_full_tank = trans

            elif trans.is_full_tank:
                last_full_tank = trans
                pending_liters = 0
                pending_cost = 0

            else:
                pending_liters += trans.liters
                pending_cost += trans.amount
            fuel_history.insert(0, item)

        context["fuel_history"] = fuel_history
        maintenances = Maintenance.objects.filter(vehicle=vehicle).order_by("-date")
        context["maintenances"] = maintenances

        maint_stats = {}
        for m in maintenances:
            if m.get_type_display() not in maint_stats:
                maint_stats[m.get_type_display()] = 0
            maint_stats[m.get_type_display()] += m.cost

        context["maint_stats"] = maint_stats
        context["is_pro"] = is_pro

        return context
