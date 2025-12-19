from django import forms
from django.utils import timezone
from .models import DailyRecord, Maintenance, Category
from vehicles.models import Vehicle


class StartShiftForm(forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = ["vehicle", "start_km"]
        labels = {
            "vehicle": "Veículo",
            "start_km": "KM Inicial (Painel)",
        }
        widgets = {
            "vehicle": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "start_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                    "placeholder": "Ex: 15000",
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )


class EndShiftForm(forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = ["end_km"]
        labels = {"end_km": "KM Final (Painel)"}
        widgets = {
            "end_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        end_km = cleaned_data.get("end_km")
        start_km = self.instance.start_km

        if end_km and start_km and end_km < start_km:
            self.add_error(
                "end_km", f"O KM final não pode ser menor que o inicial ({start_km})."
            )


class QuickFinanceForm(forms.Form):
    amount = forms.DecimalField(
        label="Valor (R$)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                "placeholder": "0.00",
            }
        ),
    )


class DailyRecordForm(forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = ["date", "vehicle", "start_km", "end_km", "total_income", "total_cost"]
        labels = {
            "date": "Data do Plantão",
            "vehicle": "Veículo Utilizado",
            "start_km": "KM Inicial",
            "end_km": "KM Final (Opcional se estiver rodando)",
            "total_income": "Faturamento Total (R$)",
            "total_cost": "Custos Totais (R$)",
        }
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                }
            ),
            "vehicle": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
            "start_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
            "end_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                    "placeholder": "Deixe vazio se ainda estiver trabalhando",
                }
            ),
            "total_income": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                }
            ),
            "total_cost": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )
        self.fields["end_km"].required = False

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_km")
        end = cleaned_data.get("end_km")

        if start and end and end < start:
            self.add_error("end_km", "O KM final não pode ser menor que o inicial.")

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.end_km is not None:
            instance.is_active = False
        else:
            instance.is_active = True

        if commit:
            instance.save()
        return instance


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ["date", "vehicle", "type", "cost", "odometer", "description"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type", "color"]
        labels = {
            "name": "Nome da Categoria",
            "type": "Tipo",
            "color": "Cor de Identificação",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "h-10 w-full px-1 py-1 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
        }
