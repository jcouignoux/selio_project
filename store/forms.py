from django import forms
from django.db.models.fields import CharField
from django.forms import ModelForm, BaseFormSet
from django.contrib.auth.forms import AuthenticationForm
from django.forms.forms import Form
from django.forms.utils import ErrorList
from django.forms.widgets import CheckboxInput, EmailInput, PasswordInput, SelectMultiple, TextInput, NumberInput, Textarea, CheckboxSelectMultiple, Widget
from django.contrib.auth.models import User
from bootstrap_datepicker_plus import DatePickerInput
from django.forms import formset_factory, modelformset_factory

from .models import History, Booking, Contact, Address


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


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': EmailInput(attrs={'placeholder':'Email'}),
            'password': PasswordInput(attrs={'placeholder':'Mot de Passe'}),
        }


# class ContactForm(forms.Form):
#     contacts = Contact.objects.all()
#     CHOICE = list(Contact.objects.all())
#     contact = forms.ChoiceField(
#         required=False,
#         widget=forms.Select,
#         choices=CHOICE,
#     )
class ContactForm(forms.Form):
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
    )

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['gender', 'first_name', 'last_name', 'address', 'additional_address',
                  'postcode', 'city', 'phone', 'mobilephone']



AddressFormSet = modelformset_factory(Address, form=AddressForm, extra=0, max_num=2)
#class AddressFormSet(BaseFormSet):
#    class Meta:
#        model = Address
#        extra = 0
#        max_num = 2
#        fields = ['gender', 'first_name', 'last_name', 'address', 'additional_address',
#                  'postcode', 'city', 'phone', 'mobilephone']
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.queryset = Address.objects.filter(contact=Contact)
#

class BookingForm(forms.Form):
    WAITING = 'W'
    KONTACTED = 'K'
    PAID = 'P'
    SHIPPED = 'S'
    CANCELED = 'C'
    STATUS = (
        (WAITING, 'En attente de validation'),
        (KONTACTED, 'Contacté'),
        (PAID, 'Payée'),
        (SHIPPED, 'Expédiée'),
        (CANCELED, 'Annulée'),
    )
    status = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=STATUS,
    )


class DateRangeForm(Form):
    start_date = forms.DateField(
        widget = DatePickerInput(format='%Y-%m-%d', attrs={"placeholder": "Date début"})
    )
    end_date = forms.DateField(
        widget = DatePickerInput(format='%Y-%m-%d', attrs={"placeholder": "Date fin"})
    )


class DictForm(Form):
    dict = forms.model_to_dict


class MessageForm(Form):
    email = forms.EmailField(
        widget = EmailInput(attrs={"required": True, "placeholder": "Votre email"})
    )
    message = forms.CharField (
        widget = Textarea(attrs={"rows":5, "cols":20, "required": True, "placeholder": "Votre message"})
    )