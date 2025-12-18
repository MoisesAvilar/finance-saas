from django import forms
from .models import DailyRecord, Maintenance
from vehicles.models import Vehicle


class DailyRecordForm(forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = ["date", "vehicle", "start_km", "end_km", "total_income", "total_cost"]
        labels = {
            "date": "Data do Plantão",
            "vehicle": "Veículo Utilizado",
            "start_km": "KM Inicial",
            "end_km": "KM Final",
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
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
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

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_km")
        end = cleaned_data.get("end_km")

        if start and end and end < start:
            self.add_error("end_km", "O KM final não pode ser menor que o inicial.")


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ["date", "vehicle", "type", "cost", "odometer", "description"]
        labels = {
            "date": "Data do Serviço",
            "vehicle": "Veículo",
            "type": "Tipo de Serviço",
            "cost": "Valor Total (R$)",
            "odometer": "KM no momento (Odômetro)",
            "description": "Local/Detalhes (Opcional)",
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
            "type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
            "cost": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                }
            ),
            "odometer": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )
