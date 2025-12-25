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
            "model_name": "Modelo do Veículo",
            "plate": "Placa",
            "fuel_type": "Combustível Principal",
            "initial_km": "KM Atual (Hodômetro)",
            "is_active": "Veículo Ativo?",
        }
        widgets = {
            "model_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                    "placeholder": "Ex: Honda Fan 160",
                }
            ),
            "plate": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white uppercase",  # Classe uppercase ajuda visualmente
                    "placeholder": "ABC1D23",
                }
            ),
            "fuel_type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white"
                }
            ),
            "initial_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md text-slate-900 dark:text-white",
                    "placeholder": "0",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                }
            ),
        }

    def clean_initial_km(self):
        km = self.cleaned_data.get("initial_km")
        if km is not None and km < 0:
            raise forms.ValidationError("A quilometragem não pode ser negativa.")
        return km

    def clean_plate(self):
        plate = self.cleaned_data.get("plate")
        if plate:
            # Remove espaços e traços, e joga para maiúsculo
            return plate.upper().replace("-", "").strip()
        return plate

    def clean_model_name(self):
        name = self.cleaned_data.get("model_name")
        if len(name) < 3:
            raise forms.ValidationError("O nome do modelo deve ser mais descritivo.")
        return name
