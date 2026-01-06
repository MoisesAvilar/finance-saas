import json
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
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
    paginate_by = 30

    def get_queryset(self):
        qs = DailyRecord.objects.filter(user=self.request.user).order_by("-date")

        if not self.request.user.is_pro:
            limit_date = timezone.now().date() - timedelta(days=30)
            qs = qs.filter(date__gte=limit_date)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_pro:
            limit_date = timezone.now().date() - timedelta(days=30)
            hidden_count = DailyRecord.objects.filter(
                user=self.request.user, date__lt=limit_date
            ).count()

            context["hidden_records_count"] = hidden_count
            context["days_limit"] = 30

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pega as categorias disponíveis no form
        form = context["form"]
        categories = form.fields["category"].queryset

        # Cria um "Mapa" para o JavaScript ler
        # Ex: { "1": {"is_fuel": true}, "5": {"is_maint": true} }
        cat_map = {
            c.id: {
                "is_fuel": c.is_fuel,
                "is_maint": c.is_maintenance,
                "name": c.name.lower(),
            }
            for c in categories
        }

        # Envia como JSON seguro para o HTML
        context["category_map"] = json.dumps(cat_map)
        return context


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
            amount_str = request.POST.get("amount", "0").replace(",", ".")
            amount = float(amount_str) if amount_str else 0.0

            description = request.POST.get("description")

            liters = request.POST.get("liters")
            next_due_km = request.POST.get("next_due_km")
            actual_km = request.POST.get("actual_km")
            is_full_tank = request.POST.get("is_full_tank") == "on"

            if liters and liters.strip():
                liters = float(liters.replace(",", "."))
            else:
                liters = None

            if next_due_km and next_due_km.strip():
                next_due_km = int(next_due_km)
            else:
                next_due_km = None

            if actual_km and actual_km.strip():
                actual_km = int(actual_km)
            else:
                actual_km = None

            trans_type = "INCOME" if type == "income" else "COST"

            transaction = Transaction.objects.create(
                record=active_shift,
                category_id=category_id,
                type=trans_type,
                amount=amount,
                description=description,
                liters=liters,
                next_due_km=next_due_km,
                actual_km=actual_km,
                is_full_tank=is_full_tank,
            )

            category = Category.objects.get(id=category_id)

            if trans_type == "COST" and category.is_maintenance:
                final_odometer = (
                    actual_km
                    if actual_km
                    else (active_shift.end_km or active_shift.start_km)
                )

                Maintenance.objects.create(
                    user=request.user,
                    vehicle=active_shift.vehicle,
                    date=active_shift.date,
                    cost=amount,
                    odometer=final_odometer,
                    type="OTHER",
                    description=f"Via Dashboard: {description}"
                    if description
                    else "Registro rápido via Dashboard",
                    transaction=transaction,
                )
                messages.info(
                    request, "Registro copiado para o Histórico de Manutenção."
                )

            messages.success(
                request, f"{'Receita' if type == 'income' else 'Despesa'} registrada!"
            )

        except Exception as e:
            messages.error(request, f"Erro ao registrar: {str(e)}")

        return redirect("dashboard")
