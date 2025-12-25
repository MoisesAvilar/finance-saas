from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib import messages
from .models import DailyRecord, Maintenance, Transaction, Category
from vehicles.models import Vehicle
from .forms import (
    CategoryForm,
    DailyRecordForm,
    MaintenanceForm,
    StartShiftForm,
    EndShiftForm,
    TransactionForm,
)


class StartShiftView(LoginRequiredMixin, CreateView):
    model = DailyRecord
    form_class = StartShiftForm
    template_name = "operations/shift_start.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if DailyRecord.objects.filter(user=request.user, is_active=True).exists():
            messages.warning(
                request,
                "Você já tem um plantão em aberto! Encerre-o antes de iniciar outro.",
            )
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        hoje = timezone.now().date()

        if DailyRecord.objects.filter(user=self.request.user, date=hoje).exists():
            form.add_error(
                None, "Você já abriu um plantão hoje! Verifique seu histórico."
            )
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.date = hoje

        messages.success(self.request, "Jornada iniciada! Bom trabalho.")
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


class DailyRecordDetailView(LoginRequiredMixin, DetailView):
    model = DailyRecord
    template_name = "operations/dailyrecord_detail.html"
    context_object_name = "record"

    def get_queryset(self):
        # Garante que o usuário só veja os próprios registros
        return DailyRecord.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Busca as transações ordenadas por horário (mais recentes primeiro)
        context["transactions"] = self.object.transactions.all().order_by("-created_at")
        return context


class TransactionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "operations/transaction_form.html"
    success_message = "Transação atualizada e totais recalculados!"

    def get_queryset(self):
        # Garante que só edita transações dos seus próprios registros
        return Transaction.objects.filter(record__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["type"] = (
            self.object.type
        )  # Passa o tipo (INCOME/COST) para filtrar categorias
        return kwargs

    def get_success_url(self):
        return reverse_lazy("dailyrecord_detail", kwargs={"pk": self.object.record.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        self.recalculate_record_totals(self.object.record)
        return response

    def recalculate_record_totals(self, record):
        """Re-soma todas as transações e atualiza o Registro Diário."""
        incomes = (
            record.transactions.filter(type="INCOME").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        costs = (
            record.transactions.filter(type="COST").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        record.total_income = incomes
        record.total_cost = costs
        record.save()


class TransactionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Transaction
    template_name = "includes/confirm_delete.html"
    success_message = "Transação removida."

    def get_queryset(self):
        return Transaction.objects.filter(record__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("dailyrecord_detail", kwargs={"pk": self.object.record.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Excluir {self.object.get_type_display()}"
        context["cancel_url"] = reverse_lazy(
            "dailyrecord_detail", kwargs={"pk": self.object.record.pk}
        )
        return context

    def form_valid(self, form):
        record = self.object.record
        response = super().form_valid(form)

        # Recalcula APÓS deletar
        incomes = (
            record.transactions.filter(type="INCOME").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        costs = (
            record.transactions.filter(type="COST").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        record.total_income = incomes
        record.total_cost = costs
        record.save()

        return response


class AddFinanceView(LoginRequiredMixin, View):
    def post(self, request, type, *args, **kwargs):

        active_shift = DailyRecord.objects.filter(
            user=request.user, is_active=True
        ).first()
        if not active_shift:
            messages.error(request, "Nenhum plantão ativo encontrado.")
            return redirect("dashboard")

        try:
            category_id = request.POST.get("category")
            amount = float(request.POST.get("amount").replace(",", "."))
            description = request.POST.get("description")

            trans_type = "INCOME" if type == "income" else "COST"

            Transaction.objects.create(
                record=active_shift,
                category_id=category_id,
                type=trans_type,
                amount=amount,
                description=description,
            )

            self.update_record_totals(active_shift)

            messages.success(
                request, f"{'Receita' if type == 'income' else 'Despesa'} registrada!"
            )

        except Exception as e:
            messages.error(request, f"Erro ao registrar: {str(e)}")

        return redirect("dashboard")

    def update_record_totals(self, record):
        incomes = (
            record.transactions.filter(type="INCOME").aggregate(t=Sum("amount"))["t"]
            or 0
        )
        costs = (
            record.transactions.filter(type="COST").aggregate(t=Sum("amount"))["t"] or 0
        )

        record.total_income = incomes
        record.total_cost = costs
        record.save()
