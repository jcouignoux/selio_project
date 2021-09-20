from datetime import datetime
import operator
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
# from functools import reduce
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.forms import formset_factory

# from django.views.decorators.csrf import csrf_protect

from .models import Address, Ouvrage, Author, Publisher, Categorie, Contact, Booking, BookingDetail, History
from .forms import BookingForm, ConnexionForm, UserForm, VenteForm, ArrivageForm, ParagraphErrorList, DateRangeForm, DictForm, AddressForm
from .store import add_to_history
from .contacts import create_contact
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
    if request.method == 'POST':
        search = request.POST['search']
        ouvrages_list = Ouvrage.objects.filter(title__icontains=search).order_by('title')
        context = {}
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
    auteurs = " et ".join([auteur.name for auteur in ouvrage.auteurs.all()])
    auteurs_name = " ".join(auteurs)
    editeurs = " ".join([editeur.name for editeur in ouvrage.editeurs.all()])
    editeurs_name = " ".join(editeurs)
    categories = " ".join([categorie.name for categorie in ouvrage.categories.all()])
    categories_name = " ".join(categories)
    context = {
        'ouvrage_id': ouvrage.id,
        'ouvrage_title': ouvrage.title,
        'ouvrage_reference': ouvrage.reference,
        'auteurs_name': auteurs_name,
        'editeurs_name': editeurs_name,
        'categories_name': categories_name,
        'ouvrage_publication': ouvrage.publication,
        'ouvrage_price': ouvrage.price,
        'ouvrage_stock': ouvrage.stock,
        'ouvrage_picture': ouvrage.picture,
        'ouvrage_note': ouvrage.note,
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
        CForm_dsa = AddressForm(contact.default_shipping_address.__dict__)
        CForm_dia = AddressForm(contact.default_invoicing_address.__dict__)
        user = get_object_or_404(User, id=contact.user.id)
    
    errors= {}

    if request.method == 'POST':
        AddressFormSet = formset_factory(AddressForm)
        CFormSet = AddressFormSet(request.POST, error_class=ParagraphErrorList)
        if request.user.is_authenticated:
            test_user = True
        else:
            user = User.objects.filter(email=request.POST.get('email')).all()
            if len(user) >= 1 and not request.user.is_authenticated:
                test_user = False
                errors['email'] = "Cette Adresse Mail existe déjà, merci de vous connecter ou d'en utiliser une autre."
            else:
                test_user = True
        if 'basket' in request.session and CFormSet.is_valid() and test_user:
            dict = {}
            if len(CFormSet.forms) == 1:
                dict['dsa'] = CFormSet.forms[0].cleaned_data
                dict['dia'] = CFormSet.forms[0].cleaned_data
            else:
                dict['dsa'] = CFormSet.forms[0].cleaned_data
                dict['dia'] = CFormSet.forms[1].cleaned_data
            dict['email'] = request.POST.get('email')
            # Bug refresh page thanks
            basket = request.session['basket']
            try:
                with transaction.atomic():
                    if not request.user.is_authenticated:
                        contact = create_contact(dict)
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
            except IntegrityError:
                errors['internal'] = "Une erreur interne est apparue. Merci de recommencer votre requête."
            except Exception as e:
                errors['error'] = e
            return render(request, 'store/thanks.html', context)
        else:
            pass
    else:
        if not request.user.is_authenticated:
            if request.GET.get('check'):
                context['checked'] = request.GET.get('check')
                AddressFormSet = formset_factory(AddressForm, extra=2)
                CFormSet = AddressFormSet()
            else:
                AddressFormSet = formset_factory(AddressForm, extra=1)
                CFormSet = AddressFormSet()

        else:
            contact = Contact.objects.get(user=request.user)
            context['contact'] = contact
            CForm_dsa = AddressForm(contact.default_shipping_address.__dict__)
            CForm_dia = AddressForm(contact.default_invoicing_address.__dict__)
            user = get_object_or_404(User, id=contact.user.id)

    context['CFormSet'] = CFormSet
    context['errors'] = errors

    return render(request, 'store/basket.html', context)

@login_required
def booking(request):
    STATUS_LIST = ('W', 'K', 'P', 'S', 'C', 'D')        
    context = {}

    if request.method == 'POST':
        booking_list = Booking.objects.all().order_by('created_at')
        BForm = BookingForm(request.POST, error_class=ParagraphErrorList)   
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
            if BForm.is_valid():
                status = BForm.cleaned_data.get('status')
                # booking_list = Booking.objects.filter(status__contains=status).order_by('created_at')
                my_filter_qs = Q()
                for stat in status:
                    # my_filter_qs = my_filter_qs | Q(status__contains=[stat])
                    my_filter_qs = my_filter_qs | Q(status=stat)
                # booking_list = Booking.objects.in_bulk(status)
                booking_list = Booking.objects.filter(my_filter_qs).order_by('created_at')
                # booking_list = Booking.objects.filter(status__0=status).order_by('created_at')

    else:
        BForm = BookingForm()
        # booking_list = Booking.objects.filter(contacted=False).order_by('created_at')
        booking_list = Booking.objects.exclude(status='S').order_by('created_at')
        
    context['bookings_list_sel']=booking_list
    context['BForm']=BForm

    return render(request, 'store/booking.html', context)

@login_required
def booking_detail(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'booking': booking,
    }

    return render(request, 'store/booking_detail.html', context)

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
    CForm_dsa = AddressForm(contact.default_shipping_address.__dict__)
    CForm_dia = AddressForm(contact.default_invoicing_address.__dict__)
    user = get_object_or_404(User, id=contact.user.id)
    UForm = UserForm(user.__dict__)
    context = {
        'contact': contact,
        'CForm_dsa': CForm_dsa,
        'CForm_dia': CForm_dia,
        'UForm': UForm,
    }

    return render(request, 'store/contact_detail.html', context)


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

def connexion(request):
    if 'basket' in request.session:
        context = {
            'basket': request.session['basket']
        }
    else:
        context = {}

    if request.method == "POST":
        UForm = UserForm(data=request.POST, error_class=ParagraphErrorList)
        if UForm.is_valid():
            email = UForm.cleaned_data['email']
            user = User.objects.filter(email=email).exclude(username__startswith='selio').first()
            print(user.email)
            password = UForm.cleaned_data['password']
            # user = authenticate(request, username=user.username, password=password)
            if not user.is_staff:
                contact = Contact.objects.get(user=user)
                CForm_dsa = AddressForm(contact.default_shipping_address.__dict__)
                CForm_dia = AddressForm(contact.default_invoicing_address.__dict__)
            login(request, user)

            return render(request, 'store/index.html', context)
    else:
        UForm = UserForm()
    
    context['UForm'] = UForm    

    return render(request, 'store/login.html', context)

@login_required    
def deconnexion(request):
    logout(request)

    return render(request, 'store/index.html')

