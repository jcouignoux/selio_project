from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Author(models.Model):
    name = models.CharField('Nom', max_length=50)
    forname = models.CharField('Prénom', max_length=50, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "auteur"


class Publisher(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    marge = models.DecimalField("Marge", max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "éditeur"


class Categorie(models.Model):
    name = models.CharField('Nom', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "catégorie"


class Contact(models.Model):
    name = models.CharField(max_length=200)
    forname = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    adresse = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Ouvrage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.BigIntegerField("Référence", blank=True, null=True)
    title = models.CharField("Titre", max_length=200)
    auteurs = models.ManyToManyField(Author, related_name='ouvrages')
    editeurs = models.ManyToManyField(Publisher, related_name='ouvrages')
    categories = models.ManyToManyField(Categorie, related_name='ouvrages')
    publication = models.IntegerField("Parution", blank=True, null=True)
    price = models.DecimalField("Prix", max_digits=5, decimal_places=2, null=True)
    stock = models.IntegerField("Stock", default=0)
    picture = models.ImageField(upload_to='couv/', blank=True, null=True)
    note = models.CharField("Note", max_length=1000, blank=True, null=True)
    available = models.BooleanField("Disponible", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ouvrage"


class Booking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    ouvrages = models.ManyToManyField(Ouvrage)

    def __str__(self):
        return self.contact.name

    class Meta:
        verbose_name = "réservation"


class Profil(models.Model):
    # username = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # La liaison OneToOne vers le modèle User

    def __str__(self):
        return "Profil de {0}".format(self.user.username)
        # return self.username

class Vente(models.Model):

    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, null=True)
    CAT_PRICE_CHOICES = [
        ('SELIO', 'SELIO'),
        ('Editeur', 'Editeur'),
        ('Dépôt', 'Dépôt'),
        ('Occasion', 'Occasion'),
    ]
    catPrice = models.CharField('catPrice', choices=CAT_PRICE_CHOICES, max_length=10, default='SELIO')
    PAYMENT_CHOICES = [
        ('Espèces', 'Espèces'),
        ('Chèque', 'Chèque'),
        ('Carte', 'Carte'),
    ]
    payment = models.CharField('payment', choices=PAYMENT_CHOICES, max_length=10, default='Espèces')
    quantity = models.IntegerField(default=1)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.id

class History(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.BigIntegerField("Référence", blank=True, null=True)
    title = models.CharField("Titre", max_length=200)
    auteurs = models.CharField("Auteurs", max_length=400)
    editeurs = models.CharField("Editeur", max_length=200)
    price = models.DecimalField("Prix", max_digits=5, decimal_places=2, null=True)
    catPrice = models.CharField('CatPrix', max_length=10)
    payment = models.CharField('Paiement', max_length=10)
    quantity = models.IntegerField('Quantité')
    date = models.DateField('Date')
    comment = models.CharField('Commentaire', max_length=10)