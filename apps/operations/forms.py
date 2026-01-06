from django import forms
from django.utils import timezone
from .models import DailyRecord, Maintenance, Category
from vehicles.models import Vehicle
from .models import Transaction


# --- MIXIN DE VALIDAÇÃO (Reutilizável) ---
class ValidationMixin:
    """Mixin para adicionar validações comuns a todos os forms."""

    def clean_amount_field(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            raise forms.ValidationError("O valor não pode ser negativo.")
        return value

    def clean_km_field(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            raise forms.ValidationError("A quilometragem não pode ser negativa.")
        return value

    def clean_future_date(self, field_name):
        date = self.cleaned_data.get(field_name)
        if date and date > timezone.now().date():
            raise forms.ValidationError("A data não pode ser no futuro.")
        return date


# --- FORMS DE PLANTÃO ---


class StartShiftForm(ValidationMixin, forms.ModelForm):
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

    def clean_start_km(self):
        return self.clean_km_field("start_km")


class EndShiftForm(ValidationMixin, forms.ModelForm):
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

    def clean_end_km(self):
        end_km = self.clean_km_field("end_km")
        start_km = self.instance.start_km

        # Validação extra: KM Final < KM Inicial
        if end_km is not None and start_km is not None and end_km < start_km:
            raise forms.ValidationError(
                f"O KM final não pode ser menor que o inicial ({start_km})."
            )

        # Alerta de erro de digitação (ex: andou 5000km num dia)
        if end_km and start_km and (end_km - start_km) > 1000:
            raise forms.ValidationError(
                "Você rodou mais de 1000km em um único plantão? Verifique se digitou corretamente."
            )

        return end_km


class QuickFinanceForm(forms.Form):
    # Não herda de ValidationMixin pois é form manual, mas aplicamos a lógica
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
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                "placeholder": "Opcional",
            }
        ),
    )

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return amount


# --- FORMS DE REGISTRO E MANUTENÇÃO ---


class DailyRecordForm(ValidationMixin, forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = ["date", "vehicle", "start_km", "end_km", "total_income", "total_cost"]
        labels = {
            "date": "Data do Plantão",
            "vehicle": "Veículo Utilizado",
            "start_km": "KM Inicial",
            "end_km": "KM Final (Opcional)",
            "total_income": "Faturamento (R$)",
            "total_cost": "Custos (R$)",
        }
        widgets = {
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                },
            ),
            "vehicle": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "start_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "end_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                    "placeholder": "Vazio se ativo",
                }
            ),
            "total_income": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
            "total_cost": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )
        self.fields["end_km"].required = False

    def clean_date(self):
        return self.clean_future_date("date")

    def clean_start_km(self):
        return self.clean_km_field("start_km")

    def clean_total_income(self):
        return self.clean_amount_field("total_income")

    def clean_total_cost(self):
        return self.clean_amount_field("total_cost")

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_km")
        end = cleaned_data.get("end_km")

        if start is not None and end is not None:
            if end < start:
                self.add_error("end_km", "O KM final não pode ser menor que o inicial.")
            if (end - start) > 1500:  # Validação de insanidade
                self.add_error(
                    "end_km",
                    "A distância percorrida parece muito alta (>1500km). Verifique os valores.",
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_active = instance.end_km is None
        if commit:
            instance.save()
        return instance


class MaintenanceForm(ValidationMixin, forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ["date", "vehicle", "type", "cost", "odometer", "description"]
        labels = {
            "date": "Data do Serviço",
            "vehicle": "Veículo",
            "type": "Tipo",
            "cost": "Custo (R$)",
            "odometer": "KM no Momento",
            "description": "Detalhes",
        }
        widgets = {
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                },
            ),
            "vehicle": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "type": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "cost": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
            "odometer": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            user=user, is_active=True
        )
        if not self.instance.pk:
            self.fields["date"].initial = timezone.now().date()

    def clean_date(self):
        return self.clean_future_date("date")

    def clean_cost(self):
        cost = self.cleaned_data.get("cost")
        if cost is not None and cost <= 0:
            raise forms.ValidationError("O custo deve ser maior que zero.")
        return cost

    def clean_odometer(self):
        return self.clean_km_field("odometer")

    def clean(self):
        cleaned_data = super().clean()
        type_ = cleaned_data.get("type")
        description = cleaned_data.get("description")

        if type_ == "OTHER" and not description:
            self.add_error(
                "description", "Por favor, descreva o serviço para o tipo 'Outros'."
            )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type", "color"]
        labels = {
            "name": "Nome",
            "type": "Tipo",
            "color": "Cor",
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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 2:
            raise forms.ValidationError("O nome deve ter pelo menos 2 caracteres.")
        return name


class TransactionForm(ValidationMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "category",
            "amount",
            "description",
            "is_full_tank",
            "actual_km",
            "liters",
            "next_due_km",
        ]
        labels = {
            "category": "Categoria",
            "amount": "Valor (R$)",
            "description": "Descrição",
            "is_full_tank": "Encheu o tanque?",
            "actual_km": "KM no Momento",
            "liters": "Litros",
            "next_due_km": "Próxima Troca (Km)",
        }
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
            "is_full_tank": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                }
            ),
            "actual_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                    "placeholder": "Ex: 50150",
                }
            ),
            "liters": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md",
                }
            ),
            "next_due_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-md"
                }
            ),
        }

    def __init__(self, user, type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra categorias pelo tipo correto (Receita ou Despesa) e pelo usuário
        self.fields["category"].queryset = Category.objects.filter(user=user, type=type)

    def clean_amount(self):
        return self.clean_amount_field("amount")
