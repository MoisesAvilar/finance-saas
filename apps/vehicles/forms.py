from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "model_name",
            "plate",
            "fuel_type",
            "initial_km",
            "is_active",
        ]
        labels = {
            "model_name": "Modelo",
            "plate": "Placa",
            "fuel_type": "Combustível",
            "initial_km": "KM Atual",
            "is_active": "Veículo Ativo?",
        }
        widgets = {
            "fuel_type": forms.Select(
                attrs={
                    "class": "w-full bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md py-2 px-3"
                }
            ),
        }
