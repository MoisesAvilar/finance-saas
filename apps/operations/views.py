from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import DailyRecord, Maintenance
from .forms import DailyRecordForm, MaintenanceForm


class DailyRecordListView(LoginRequiredMixin, ListView):
    model = DailyRecord
    template_name = "operations/dailyrecord_list.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user).order_by("-date")


class DailyRecordCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DailyRecord
    form_class = DailyRecordForm
    template_name = "operations/dailyrecord_form.html"
    success_url = reverse_lazy("dailyrecord_list")
    success_message = "Registro diário salvo com sucesso!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


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
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("dailyrecord_list")
    success_message = "Registro removido."

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Registro Diário"
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
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("maintenance_list")
    success_message = "Manutenção removida."

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir Manutenção"
        context["cancel_url"] = reverse_lazy("maintenance_list")
        return context
