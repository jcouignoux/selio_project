from django.conf import settings
from django.http.response import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError

from .models import Ouvrage, Author, Publisher, Categorie, Contact, Booking, History
from .forms import ConnexionForm, VenteForm, ArrivageForm, ParagraphErrorList, DateRangeForm, DictForm, ContactForm
from .store import exportXLSX, xlsx


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

def store(request):
    if request.method == 'POST':
        search = request.POST['search']
        print(search)
        ouvrages_list = Ouvrage.objects.filter(title__icontains=search).order_by('title')
    else:    
        ouvrages_list = Ouvrage.objects.filter(available=True).order_by('title')
    paginator = Paginator(ouvrages_list, 12)
    page = request.GET.get('page')
    try: 
        ouvrages = paginator.page(page)
    except PageNotAnInteger:
        ouvrages = paginator.page(1)
    except EmptyPage:
        ouvrages = paginator.page(paginator.num_pages)
    context = {
        'ouvrages': ouvrages,
        'paginate': True,
    }
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
                    return render(request, 'store/store.html', context)
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
    
    # print(request.session['basket'])

    return render(request, 'store/detail.html', context)

def add_to_basket(request):
        
    if request.method == 'POST':
        ouvrage_id = request.POST.get('ouvrage_id')
        if request.POST.get('quantity'):
            quantity = request.POST.get('quantity')
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
        
        # request.session.flush()
        request.session['basket'] = basket
    
        return redirect(reverse('store:detail', kwargs={'ouvrage_id': ouvrage_id}))

def basket(request):
    # request.session.flush()
    # basket = {}
    if 'basket' in request.session:
        print('test')
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

    if request.method == 'POST':
        CForm = ContactForm(request.POST, error_class=ParagraphErrorList)
        if CForm.is_valid():
            name = CForm.cleaned_data['name']
            forname = CForm.cleaned_data['forname']
            email = CForm.cleaned_data['email']
            adresse = CForm.cleaned_data['adresse']
            # try:
            with transaction.atomic():
                contact = Contact.objects.filter(email=email)
                if not contact.exists():
                    contact = Contact.objects.create(
                        email=email,
                        name=name,
                        forname=forname,
                        adresse=adresse
                    )
                else:
                    contact = contact.first()
                booking = Booking()
                booking.contact=contact
                booking.save()
                for ouvrage in ouvrages:
                    booking.ouvrages.add(ouvrage)
                booking.save()
                request.session.flush()
                context = {
                    'booking': booking
                }
            # except IntegrityError:
            #     CForm.errors['internal'] = "Une erreur interne est apparue. Merci de recommencer votre requête."
        return render(request, 'store/thanks.html', context)
    else:
        CForm = ContactForm()

    context['Cform'] = CForm
    context['Cerrors'] = CForm.errors.items()

    return render(request, 'store/basket.html', context)

def booking(request):

    return render(request, 'store/booking.html')

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
            # histDict = dict(History.objects.filter(date__range=(start_date, end_date)))
        else:
            # histDict = dict(History.objects.all().__dict__)
            histDict = History.objects.all()
        name = 'Comptes.xlsx'
        title = ('Date', 'Ref', 'Titre', 'Auteurs', 'Editeur', 'Prix', 'Cat. Prix', 'Paiement', 'Fournisseur', "Quantité", 'commentaire')
        file = exportXLSX(histDict, title, name)
        return file
    else:
        pass

    return render(request, 'store/history.html')

def connexion(request):
    if request.method == "POST":
        form = ConnexionForm(data=request.POST, error_class=ParagraphErrorList)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return render(request, 'store/index.html')
            else:
                print('ok')
                context = {'form': form}
                return render(request, 'store/login.html', context)
        else:
            context = {'form': form}
            return render(request, 'store/login.html', context)
    else:
        form = ConnexionForm()
        context = {'form': form}
        return render(request, 'store/login.html', context)

@login_required    
def deconnexion(request):
    logout(request)

    return render(request, 'store/index.html')