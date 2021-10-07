from datetime import datetime
from django import forms
from django.conf import settings
from django.http.response import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, ListView
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User
from django.forms import formset_factory


from .models import Address, Ouvrage, Author, Publisher, Categorie, Contact, Booking, BookingDetail, History
from .forms import BookingForm, ConnexionForm, UserForm, VenteForm, ArrivageForm, ParagraphErrorList, DateRangeForm, DictForm, AddressForm, MessageForm, ContactForm
from .store import add_to_history, send_email
from .contacts import create_contact, update_contact
from .xlsx import xlsx, exportXLSX
from .basket import update_basket


# Create your views here.
def index(request):
    if 'basket' in request.session:
        context = {
            'basket': request.session['basket']
        }
    else:
        context = {
            'basket': ''
        }

    author = Author.objects.filter(name='SERAC').first()
    ouvrages = Ouvrage.objects.filter(auteurs__name=author).all()
    context['ouvrages'] = ouvrages
    
    return render(request, 'store/index.html', context)

def propos(request):
    if 'basket' in request.session:
        context = {
            'basket': request.session['basket']
        }
    else:
        context = {}
    
    return render(request, 'store/propos.html', context)

def store(request, select_type, select_id):
    context = {}
    if request.method == 'POST':
        search = request.POST['search']
        ouvrages_list = Ouvrage.objects.filter(title__icontains=search).order_by('title')
        context['search'] = search
    else:
        if select_type != 'All':
            if select_type == 'categories':
                ouvrages_list = Ouvrage.objects.filter(categories__id=select_id)
                context = {
                    'type_filter':  'Catégorie',
                    'sel_id': get_object_or_404(Categorie, pk=select_id),
                }
            elif select_type == 'authors':
                ouvrages_list = Ouvrage.objects.filter(auteurs__id=select_id)
                context = {
                    'type_filter':  'Auteur',
                    'sel_id': get_object_or_404(Author, pk=select_id),
                }
            elif select_type == 'publishers':
                ouvrages_list = Ouvrage.objects.filter(editeurs__id=select_id)
                context = {
                    'type_filter':  'Editeur',
                    'sel_id': get_object_or_404(Publisher, pk=select_id),
                }
        else:
            ouvrages_list = Ouvrage.objects.filter(available=True).order_by('title')
            context = {}
    paginator = Paginator(ouvrages_list, 12)
    page = request.GET.get('page')
    try: 
        ouvrages = paginator.page(page)
    except PageNotAnInteger:
        ouvrages = paginator.page(1)
    except EmptyPage:
        ouvrages = paginator.page(paginator.num_pages)
    context['ouvrages'] = ouvrages
    context['paginate'] = True
    if 'basket' in request.session:
        context['basket'] = request.session['basket']

    return render(request, 'store/store.html', context)

def detail(request, ouvrage_id):
    ouvrage = get_object_or_404(Ouvrage, pk=ouvrage_id)
    context = {
        'ouvrage': ouvrage,
    }
    if request.method == 'POST':
        VForm = VenteForm(request.POST, error_class=ParagraphErrorList)
        AForm = ArrivageForm(request.POST, error_class=ParagraphErrorList)
        if VForm.is_valid() or AForm.is_valid():
            if VForm.is_valid():
                catPrice = VForm.cleaned_data['catPrice']
                payment = VForm.cleaned_data['payment']
                fournisseur = ''
                quantity = VForm.cleaned_data['quantity']
                date = VForm.cleaned_data['date']
                comment = VForm.cleaned_data['comment']
            if AForm.is_valid():
                catPrice = ''
                payment = ''
                fournisseur = AForm.cleaned_data['fournisseur']
                quantity = AForm.cleaned_data['quantity']
                date = AForm.cleaned_data['date']
                comment = AForm.cleaned_data['comment']
            try:
                with transaction.atomic():
                    ouvrage = get_object_or_404(Ouvrage, id=ouvrage.id)
                    history = History.objects.create(
                        reference=ouvrage.reference,
                        title=ouvrage.title,
                        auteurs=ouvrage.auteurs.first(),
                        editeurs=ouvrage.editeurs.first(),
                        price=ouvrage.price,
                        catPrice=catPrice,
                        fournisseur=fournisseur,
                        payment=payment,
                        quantity=quantity,
                        date=date,
                        comment=comment
                    )
                    ouvrage.stock -= 1
                    if ouvrage.stock <= 0:
                        # ouvrage.available = False
                        pass
                    ouvrage.save()
                    context = {
                        'ouvrage_title': ouvrage.title
                    }
                    # return render(request, 'store/store.html', context)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
            except IntegrityError:
                VForm.errors['internal'] = "Une erreur interne est apparue. Merci de recommencer votre requête."

    else:
        VForm = VenteForm()
        AForm = ArrivageForm()

    context['Vform'] = VForm
    context['Verrors'] = VForm.errors.items()
    context['Aform'] = AForm
    context['Aerrors'] = AForm.errors.items()
    if 'basket' in request.session:
        context['basket'] = request.session['basket']

    return render(request, 'store/detail.html', context)


def add_to_basket(request):
        
    if request.method == 'POST':
        ouvrage_id = request.POST.get('ouvrage_id')
        if request.POST.get('quantity'):
            quantity = int(request.POST.get('quantity'))
        else:
            quantity = 1
        request.session.set_expiry(3600)
        # print(request.session.get_expire_at_browser_close())
        # print(request.session.get_expiry_age())
        if 'basket' not in request.session:
            basket = {}
        else:
            basket = request.session['basket']
        if ouvrage_id in basket:
            basket[ouvrage_id] = basket[ouvrage_id] + quantity
        else:
            basket[ouvrage_id] = quantity
        
        request.session['basket'] = basket

        return redirect(reverse('store:store', kwargs={'select_type':'All', 'select_id':'All'}))


def basket(request):
    if 'basket' in request.session:
        ouvrage_to_mod = request.GET.get('ouvrage_to_mod')
        if request.GET.get('quantity') == '-':
            request.session['basket'][ouvrage_to_mod] -= 1
        elif request.GET.get('quantity') == '+':
            request.session['basket'][ouvrage_to_mod] += 1
        elif request.GET.get('quantity') == 'x':
            del request.session['basket'][ouvrage_to_mod]
        request.session.modified = True
        ouvrages = []
        for ouvrage_id in request.session['basket'].keys():
            ouvrage = get_object_or_404(Ouvrage, pk=ouvrage_id)
            ouvrage.qty = request.session['basket'][ouvrage_id]
            ouvrages.append(ouvrage)
        
        context = {
            'basket': request.session['basket'],
            'ouvrages': ouvrages
        }
    else:
        context = {}

    if request.user.is_authenticated:
        contact = Contact.objects.get(user=request.user)
        context['contact'] = contact
        user = get_object_or_404(User, id=contact.user.id)

    context['errors'] = []

    if request.method == 'POST':
        if request.user.is_authenticated:
            CForm_dsa = AddressForm(request.POST, initial=contact.default_shipping_address.__dict__, error_class=ParagraphErrorList, prefix="CForm_dsa")
            CForm_dia = AddressForm(request.POST, initial=contact.default_invoicing_address.__dict__, error_class=ParagraphErrorList, prefix="CForm_dia")
        else:
            CForm_dsa = AddressForm(request.POST, error_class=ParagraphErrorList, prefix="CForm_dsa")
            CForm_dia = AddressForm(request.POST, error_class=ParagraphErrorList, prefix="CForm_dia")

        if request.POST.get('order') == "commander":
            dict = {}

            if not 'basket' in request.session:
                context['errors'].append("Votre panier est vide.")
                context['CForm_dsa'] = AddressForm(instance=contact.default_shipping_address, prefix="CForm_dsa" )
                context['CForm_dia'] = AddressForm(instance=contact.default_invoicing_address, prefix="CForm_dia" )
                return render(request, 'store/basket.html', context)

            if not request.user.is_authenticated:
                user = User.objects.filter(email=request.POST.get('email')).all()
                if len(user) >= 1 and not request.user.is_authenticated:
                    test_user = False
                    context['errors'].append("Cette Adresse Mail existe déjà, merci de vous connecter ou d'en utiliser une autre.")
                    context['CForm_dsa'] = CForm_dsa
                    context['CForm_dia'] = CForm_dia
                    return render(request, 'store/basket.html', context)
                else:
                    test_user = True
                    email = request.POST.get('email')
                    if CForm_dsa.is_valid():
                        if not CForm_dia.is_valid():
                            CForm_dia = CForm_dsa
                        contact = create_contact(email, CForm_dsa, CForm_dia)
                    else:
                        return render(request, 'store/basket.html', context)
            else:
                test_user = True

            if 'basket' in request.session and test_user:
                # Bug refresh page thanks
                basket = request.session['basket']
                #try:
                with transaction.atomic():
                    booking = Booking()
                    booking.contact=contact
                    booking.status='W'
                    booking.save()
                    for ouvrage in ouvrages:
                        booking_detail = BookingDetail()
                        booking_detail.booking = booking
                        booking_detail.ouvrage = ouvrage
                        booking_detail.qty = ouvrage.qty
                        booking_detail.save()
                    del request.session['basket']
                    context = {
                        'booking': booking,
                        'dict': dict,
                    }
                    content = {
                        'subject': 'Commande ' + str(booking.id),
                        'message': booking,
                        'html': 'email_vente.html',
                        'email_contact': '',
                    }
                    response = str(send_email(contact.user.email, content))
                #except IntegrityError:
                #    errors['internal'] = "Une erreur interne est apparue. Merci de recommencer votre requête."
                #except Exception as e:
                #    errors['error'] = e
                return render(request, 'store/thanks.html', context)
            else:
                context['errors'].append("Une erreur est survenue.")
    else:
        if not request.user.is_authenticated:
            if request.GET.get('check'):
                context['checked'] = request.GET.get('check')
 
            CForm_dsa = AddressForm(prefix="CForm_dsa")
            CForm_dia = AddressForm(prefix="CForm_dia")

        else:
            CForm_dsa = AddressForm(instance=contact.default_shipping_address, prefix="CForm_dsa")
            CForm_dia = AddressForm(instance=contact.default_invoicing_address, prefix="CForm_dia")

    context['CForm_dsa'] = CForm_dsa
    context['CForm_dia'] = CForm_dia


    return render(request, 'store/basket.html', context)

@login_required
def booking(request):
    STATUS_LIST = ('W', 'K', 'P', 'S', 'C', 'D')        
    context = {}

    if request.method == 'POST':
        booking_list = Booking.objects.all().order_by('created_at')
        BForm = BookingForm(request.POST, error_class=ParagraphErrorList)
        CForm = ContactForm(request.POST, error_class=ParagraphErrorList)
        action = request.POST.get('action')
        if action == 'X':
            booking_detail_id = request.POST.get('booking_detail_id')
            booking_detail = get_object_or_404(BookingDetail, id=booking_detail_id)
            booking_detail.delete()
        if action in STATUS_LIST:
            booking_id = request.POST.get('booking_id')
            booking = get_object_or_404(Booking, id=booking_id)
            if action == booking.status:
                booking.status = STATUS_LIST[STATUS_LIST.index(action) - 1]
            else:
                booking.status = action
            booking.save()
            if action == 'S':
                booking_details = BookingDetail.objects.filter(booking_id=booking.id)
                for booking in booking_details:
                    ouvrage_id = booking.ouvrage.id
                    quantity = booking.qty
                    date = str(datetime.now().strftime('%Y-%m-%d'))
                    add_to_history(ouvrage_id, quantity, date)
            if action == "D":
                booking.delete()
        else:
            if BForm.is_valid() or CForm.is_valid():
                my_filter_cs = Q()
                if CForm.is_valid():
                    if CForm.data.get('contact') != "":
                        contact = CForm.cleaned_data.get('contact')
                        my_filter_c = Q(contact=contact)
                    else:
                        my_filter_c = Q()
                    if BForm.is_valid():
                        status = BForm.cleaned_data.get('status')
                        my_filter_s = Q()
                        for stat in status:
                            my_filter_s = my_filter_s | Q(status=stat)
                    my_filter_cs = my_filter_c & my_filter_s
                booking_list = Booking.objects.filter(my_filter_cs).order_by('created_at')

    else:
        BForm = BookingForm()
        CForm = ContactForm()
        booking_list = Booking.objects.exclude(status='S').order_by('created_at')
        
    context['bookings_list_sel']=booking_list
    context['BForm']=BForm
    context['CForm']=CForm

    return render(request, 'store/booking.html', context)

@login_required
def booking_detail(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'booking': booking,
    }

    return render(request, 'store/booking_detail.html', context)


@login_required
def contact(request):

    if request.method == "POST":
        if request.POST.get('action') == 'Delete':
            contact_id = request.POST.get('contact_id')
            contact = get_object_or_404(Contact, id=contact_id)
            contact.delete()
        
    contacts_list = Contact.objects.order_by('user')
    context = {
        'contacts_list': contacts_list,
    }

    return render(request, 'store/contact.html', context)

@login_required
def contact_detail(request, contact_id):

    contact = get_object_or_404(Contact, id=contact_id)
    CForm_dsa = AddressForm(instance=contact.default_shipping_address)
    CForm_dia = AddressForm(instance=contact.default_invoicing_address)
    context = {
        'contact': contact,
        'CForm_dsa': CForm_dsa,
        'CForm_dia': CForm_dia,
    }

    return render(request, 'store/contact_detail.html', context)

@login_required
def user_detail(request, user_id):

    user = get_object_or_404(User, id=user_id)
    contact = get_object_or_404(Contact, user=user)
    UForm = UserForm(instance=user)
    context = {
        'contact': contact,
        'UForm': UForm,
    }
    
    return render(request, 'store/user_detail.html', context)


@login_required
def profil(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    user = get_object_or_404(User, id=contact.user.id)
    context = {}

    if request.method == "POST":
        UForm = UserForm(data=request.POST, instance=user, error_class=ParagraphErrorList)
        CForm_dsa = AddressForm(request.POST, error_class=ParagraphErrorList,instance=contact.default_shipping_address, prefix="CForm_dsa")
        CForm_dia = AddressForm(request.POST, error_class=ParagraphErrorList,instance=contact.default_invoicing_address, prefix="CForm_dia")
        if request.POST.get('update') == 'password':
            if UForm.is_valid() and UForm.has_changed():
                context['pwd_messages'] = []
                context['pwd_errors'] = []
                password = request.POST.get('new_password')
                control_password = request.POST.get('control_password')
                if control_password == password:
                    # response = user.set_password(password)
                    response = True
                    if response:
                        context['pwd_messages'].append("Votre mot de passe a été modifié.")
                else:
                    context['pwd_errors'].append("Vos mots de passe ne correspondent pas.")
            CForm_dsa = AddressForm(instance=contact.default_shipping_address, prefix="CForm_dsa")
            CForm_dia = AddressForm(instance=contact.default_invoicing_address, prefix="CForm_dia")
        else:
            UForm = UserForm(instance=user)

        if request.POST.get('update') == 'address':
            context['adr_messages'] = []
            context['adr_errors'] = []
            if CForm_dsa.is_valid():
                CForm_dsa.save()
                contact.default_shipping_address.refresh_from_db()
                response = True
                if response:
                    context['adr_messages'].append("Votre adresse a été modifiée.")
                else:
                    context['adr_errors'].append("erreur.")
            if CForm_dia.is_valid():
                CForm_dia.save()
                contact.default_invoicing_address.refresh_from_db()
                response = True
                if response:
                    context['adr_messages'].append("Votre adresse a été modifiée.")
                else:
                    context['adr_errors'].append("erreur.")
            
            CForm_dsa = AddressForm(instance=contact.default_shipping_address, prefix="CForm_dsa")
            CForm_dia = AddressForm(instance=contact.default_invoicing_address, prefix="CForm_dia")
            UForm = UserForm(instance=user)

        # return redirect(request.META.get('HTTP_REFERER'), context)
    else:
        CForm_dsa = AddressForm(instance=contact.default_shipping_address, prefix="CForm_dsa")
        CForm_dia = AddressForm(instance=contact.default_invoicing_address, prefix="CForm_dia")
        UForm = UserForm(instance=user)

    context['contact'] = contact
    context['CForm_dsa'] = CForm_dsa
    context['CForm_dia'] = CForm_dia
    context['UForm'] = UForm

    return render(request, 'store/profil.html', context)


@login_required
def history(request):
    if request.method == "POST":
        form = DateRangeForm(request.POST)
        start_date = form.data['start_date']
        end_date = form.data['end_date']
        histories = History.objects.filter(date__range=(start_date, end_date))
    else:
        form = DateRangeForm()
        histories = History.objects.all()
        start_date = 'old'
        end_date = 'new'

    context = {
        'form': form,
        'histories': histories,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'store/history.html', context)
 

@login_required
def dataBase(request):
    if request.method == "POST":
        file = request.FILES['xls']
        xls=xlsx()
        xls.importXLSX(file)
    else:
        pass

    return render(request, 'store/db.html')


@login_required
def histBase(request):
    if request.method == "POST":
        histSelect=request.POST.get('dateRange')
        if 'old' not in histSelect:
            start_date = histSelect.split(',')[0]
            end_date = histSelect.split(',')[0]
        else:
            histDict = History.objects.all()
        name = 'Comptes.xlsx'
        title = ('Date', 'Ref', 'Titre', 'Auteurs', 'Editeur', 'Prix', 'Cat. Prix', 'Paiement', 'Fournisseur', "Quantité", 'Commentaire')
        file = exportXLSX(histDict, title, name)
        return file
    else:
        pass

    return render(request, 'store/history.html')


def contact_us(request):

    if request.method == "POST":
        MForm = MessageForm(request.POST, error_class=ParagraphErrorList)
        if MForm.is_valid():
            email_contact = MForm.cleaned_data['email']
            message = MForm.cleaned_data['message']
            content = {}
            content['subject'] = 'message'
            content['message'] = message
            content['html'] = 'email_message.html'
            content['email_contact'] = email_contact
            response = send_email('selio4pro@gmail.com', content)
            
            return redirect(reverse('store:propos'))
    else:
        MForm = MessageForm()

    context = {
        'MForm': MForm,
    }

    return render(request, 'store/message.html', context)


def connexion(request):
    if 'basket' in request.session:
        context = {
            'basket': request.session['basket']
        }
    else:
        context = {}

    if request.method == "POST":
        context['errors'] = []
        UForm = UserForm(data=request.POST, error_class=ParagraphErrorList)
        if UForm.is_valid():
            email = UForm.cleaned_data['email']
            user = User.objects.filter(email=email).exclude(username__startswith='selio').first()
            password = UForm.cleaned_data['password']
            # user = authenticate(request, username=user.username, password=password)
            if user:
                if not user.is_staff:
                    print('test')
                    contact = Contact.objects.get(user=user)
                    CForm_dsa = AddressForm(contact.default_shipping_address.__dict__)
                    CForm_dia = AddressForm(contact.default_invoicing_address.__dict__)
                    context = {
                        'contact': contact,
                    }
                login(request, user)

                return render(request, 'store/index.html', context)
            else:
                context['errors'].append("Identifiant ou mot de passe incorrect.")
    else:
        UForm = UserForm()
    
    context['UForm'] = UForm    

    return render(request, 'store/login.html', context)


@login_required    
def deconnexion(request):
    if 'basket' in request.session:
        del request.session['basket']
    logout(request)

    return render(request, 'store/index.html')


def test(request):
    cont = Contact.objects.filter(id=25).first()
    print(cont)
    context = {}
    
    if request.method == "POST":
        CForm_dsa = AddressForm(request.POST, error_class=ParagraphErrorList,instance=cont.default_shipping_address, prefix="CForm_dsa")
        CForm_dia = AddressForm(request.POST, error_class=ParagraphErrorList,instance=cont.default_invoicing_address, prefix="CForm_dia")
        if CForm_dsa.is_valid():
            if not CForm_dia.is_valid():
                CForm_dia = CForm_dsa
            cont = update_contact(cont, CForm_dsa, CForm_dia)
            context['cont'] = cont

    else:
        if request.GET.get('check'):
            context['checked'] = request.GET.get('check')
        CForm_dsa = AddressForm(instance=cont.default_shipping_address, prefix="CForm_dsa")
        CForm_dia = AddressForm(instance=cont.default_invoicing_address, prefix="CForm_dia")

    context['CForm_dsa'] = CForm_dsa
    context['CForm_dia'] = CForm_dia
    context['cont'] = cont

    return render(request, 'store/test.html', context)

