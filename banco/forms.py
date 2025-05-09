from django import forms
from django.core.exceptions import ValidationError
from .models import Utilizador
import re

class RegistoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Utilizador
        fields = ['nome', 'email', 'password', 'data_nascimento', 'nif']

    def clean_nif(self):
        nif = self.cleaned_data['nif']
        if not re.fullmatch(r'\d{9}', nif):
            raise ValidationError("O NIF deve conter exatamente 9 dígitos.")
        return nif
