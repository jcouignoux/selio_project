from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.utils import ErrorList
from django.forms.widgets import PasswordInput, TextInput, RadioSelect, NumberInput
from django.contrib.auth.models import User

from .models import Vente, Profil


class ParagraphErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self: return ''
        return '<div class="errorList">%s</div>' % ''.join(['<p class="small error">%s</p>' % e for e in self])


class ConnexionForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        widget = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'UserName'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Password'})
        }


class VenteForm(ModelForm):
    class Meta:
        model = Vente
        fields = ["catPrice", "payment", "quantity"]
        widget = {
            'catPrice': RadioSelect(attrs={'class': 'form-control'}),
            'payment': RadioSelect(attrs={'class': 'form-control'}),
            'quantity': NumberInput(attrs={'class': 'form-control'})
        }