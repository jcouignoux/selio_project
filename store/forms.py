from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.forms import Form
from django.forms.utils import ErrorList
from django.forms.widgets import PasswordInput, TextInput, RadioSelect, NumberInput
from django.contrib.auth.models import User
from bootstrap_datepicker_plus import DatePickerInput

from .models import Profil, History


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
        model = History
        fields = ["catPrice", "payment", "quantity", "date", "comment"]
        widgets = {
            'date': DatePickerInput(format='%Y-%m-%d', attrs={'class': 'form-control'})
        }


class ArrivageForm(ModelForm):
    class Meta:
        model = History
        fields = ["fournisseur", "quantity", "date", "comment"]
        widgets = {
            'date': DatePickerInput(format='%Y-%m-%d', attrs={'class': 'form-control'})
        }

class DateRangeForm(Form):
    start_date = forms.DateField(
        widget = DatePickerInput(format='%Y-%m-%d', attrs={"placeholder": "Date début"})
    )
    end_date = forms.DateField(
        widget = DatePickerInput(format='%Y-%m-%d', attrs={"placeholder": "Date fin"})
    )

class DictForm(Form):
    dict = forms.model_to_dict