from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import DailyRecord, Maintenance, Transaction, Category
from vehicles.models import Vehicle
from .forms import (
    CategoryForm,
    DailyRecordForm,
    MaintenanceForm,
    StartShiftForm,
    EndShiftForm,
    QuickFinanceForm,
)


class StartShiftView(LoginRequiredMixin, CreateView):
    model = DailyRecord
    form_class = StartShiftForm
    template_name = "operations/shift_start.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if DailyRecord.objects.filter(user=request.user, is_active=True).exists():
            messages.warning(
                request,
                "Você já tem um plantão em aberto! Encerre-o antes de iniciar outro.",
            )
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.now().date()
        form.instance.is_active = True
        messages.success(self.request, "Plantão iniciado! Boa jornada.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class EndShiftView(LoginRequiredMixin, UpdateView):
    model = DailyRecord
    form_class = EndShiftForm
    template_name = "operations/shift_end.html"
    success_url = reverse_lazy("dailyrecord_list")

    def get_object(self):
        return get_object_or_404(DailyRecord, user=self.request.user, is_active=True)

    def form_valid(self, form):
        form.instance.is_active = False
        messages.success(self.request, "Plantão encerrado com sucesso. Bom descanso!")
        return super().form_valid(form)


class AddFinanceView(LoginRequiredMixin, View):
    def post(self, request, type):
        record = get_object_or_404(DailyRecord, user=request.user, is_active=True)

        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        description = request.POST.get("description")

        try:
            amount = float(amount)
            category = get_object_or_404(Category, id=category_id, user=request.user)
        except (ValueError, TypeError):
            messages.error(request, "Dados inválidos.")
            return redirect("home")

        Transaction.objects.create(
            record=record,
            type=type.upper(),
            category=category,
            amount=amount,
            description=description,
        )

        from decimal import Decimal

        if type == "income":
            record.total_income += Decimal(str(amount))
            messages.success(
                request, f"Ganho de R$ {amount} registrado em {category.name}."
            )
        elif type == "cost":
            record.total_cost += Decimal(str(amount))
            messages.success(
                request, f"Despesa de R$ {amount} registrada em {category.name}."
            )

        record.save()
        return redirect("home")


class DailyRecordListView(LoginRequiredMixin, ListView):
    model = DailyRecord
    template_name = "operations/dailyrecord_list.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user).order_by("-date")


class DailyRecordUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DailyRecord
    form_class = DailyRecordForm
    template_name = "operations/dailyrecord_form.html"
    success_url = reverse_lazy("dailyrecord_list")
    success_message = "Registro atualizado!"

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DailyRecordDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = DailyRecord
    template_name = "generics/confirm_delete.html"
    success_url = reverse_lazy("dailyrecord_list")
    success_message = "Registro removido."

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Registro"
        context["cancel_url"] = reverse_lazy("dailyrecord_list")
        return context


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = "operations/maintenance_list.html"
    context_object_name = "maintenances"
    paginate_by = 20

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)


class MaintenanceCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "operations/maintenance_form.html"
    success_url = reverse_lazy("maintenance_list")
    success_message = "Manutenção registrada com sucesso!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MaintenanceUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "operations/maintenance_form.html"
    success_url = reverse_lazy("maintenance_list")
    success_message = "Manutenção atualizada!"

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MaintenanceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Maintenance
    template_name = "generics/confirm_delete.html"
    success_url = reverse_lazy("maintenance_list")
    success_message = "Manutenção removida."

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Manutenção"
        context["cancel_url"] = reverse_lazy("maintenance_list")
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "operations/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "operations/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "Categoria criada com sucesso!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "operations/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "Categoria atualizada!"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Category
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("category_list")
    success_message = "Categoria removida."

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Categoria"
        context["cancel_url"] = reverse_lazy("category_list")
        return context


def get_last_km(request, vehicle_id):
    """Retorna o último KM registrado para o veículo ou o KM inicial do cadastro."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    last_record = (
        DailyRecord.objects.filter(
            user=request.user, vehicle_id=vehicle_id, end_km__isnull=False
        )
        .order_by("-date", "-created_at")
        .first()
    )

    if last_record:
        return JsonResponse(
            {
                "km": last_record.end_km,
                "source": "last_shift",
                "message": f"Último fechamento: {last_record.end_km} km",
            }
        )

    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)
    start_km = getattr(vehicle, "initial_km", getattr(vehicle, "odometer", 0))

    return JsonResponse(
        {
            "km": start_km,
            "source": "vehicle_register",
            "message": f"Primeira jornada! Sugerido KM do cadastro ({start_km} km)",
        }
    )
