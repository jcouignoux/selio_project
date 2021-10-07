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
from django.utils.safestring import mark_safe

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
    #extra_field = Contact

    class Meta:
        model = Address
        # fields = '__all__'
        fields = ['gender', 'first_name', 'last_name', 'address', 'additional_address',
                  'postcode', 'city', 'phone', 'mobilephone']
# 
    # def __init__(self, *args, **kwargs):
    #     initial = kwargs.get('initial', None)
    #     updated_initial = {}
    #     if initial:
    #         user = initial.get('user', None)
    #         if user:
    #             contact = Contact.objects.filter(user=user).first()
    #             updated_initial['contact'] = getattr(contact, 'contact', None)
    #     kwargs.update(initial=updated_initial)
    #     super(AddressForm, self).__init__(*args, **kwargs)


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


class EmailWidget(Widget):

    def __init__(self, base_widget, data, *args, **kwargs):
        """Initialise widget and get base instance"""
        super(EmailWidget, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data

    def render(self, name, value, attrs=None, renderer=None):
        """Render base widget and add bootstrap spans"""
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            '<div class="input-group mb-3">'
            '  <div class="input-group-prepend">'
            '    <span class="input-group-text" id="basic-addon1">@</span>'
            '  </div>'
            '  <input type="email" name="email" class="form-control" placeholder="Votre email" aria-label="Username" aria-describedby="basic-addon1">'
            '</div>'
        ) % {'field': field, 'data': self.data})


class TextareaWidget(Widget):

    def __init__(self, base_widget, data, *args, **kwargs):
        """Initialise widget and get base instance"""
        super(TextareaWidget, self).__init__(*args, **kwargs)
        self.base_widget = base_widget(*args, **kwargs)
        self.data = data

    def render(self, name, value, attrs=None, renderer=None):
        """Render base widget and add bootstrap spans"""
        field = self.base_widget.render(name, value, attrs)
        return mark_safe((
            '<div class="input-group">'
            '  <div class="input-group-prepend">'
            '    <span class="input-group-text">Message</span>'
            '  </div>'
            '  <textarea name="message" rows="5" cols="20" class="form-control" placeholder="Votre message" aria-label="Message"></textarea>'
            '</div>'
        ) % {'field': field, 'data': self.data})


class MessageForm(Form):
    email = forms.EmailField(
        required = True,
        # widget = EmailInput(attrs={"required": True, "placeholder": "Votre email"})
        widget = EmailWidget(base_widget=EmailInput, data='$')
    )
    SUBJECTS = (
        ('commande', 'Suivi de Commande'),
        ('info', "Demande d'informations"),
        ('autre', 'Autre'),
    )
    subject = forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=SUBJECTS,
        initial=('commande', 'Suivi de Commande'),
    )
    message = forms.CharField (
        # widget = Textarea(attrs={"rows":5, "cols":20, "required": True, "placeholder": "Votre message"})
        required = True,
        widget = TextareaWidget(base_widget=Textarea, data='$')
    )
