from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError

from .models import Ouvrage, Author, Publisher, Categorie, Contact, Booking, History
from .forms import ConnexionForm, VenteForm, ArrivageForm, ParagraphErrorList, DateRangeForm
from .store import xlsx

# Create your views here.
def index(request):
    return render(request, 'store/index.html')

def propos(request):
    return render(request, 'store/propos.html')

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
        'paginate': True
    }
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
        'ouvrage_note': ouvrage.note
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

    return render(request, 'store/detail.html', context)

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

    context = {
        'form': form,
        'histories': histories
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


        
def deconnexion(request):
    logout(request)

    return render(request, 'store/index.html')