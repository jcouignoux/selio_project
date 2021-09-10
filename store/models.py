from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
#from jsonfield import JSONField
from datetime import datetime
from decimal import *


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
    note = models.CharField("Note", max_length=3000, blank=True, null=True)
    available = models.BooleanField("Disponible", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ouvrage"


class Booking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    WAITING = 'W'
    KONTACTED = 'K'
    PAID = 'P'
    SHIPPED = 'S'
    CANCELED = 'C'
    DELETED = 'D'
    STATUS = (
        (WAITING, 'En attente de validation'),
        (KONTACTED, 'Contacté'),
        (PAID, 'Payée'),
        (SHIPPED, 'Expédiée'),
        (CANCELED, 'Annulée'),
        (DELETED, 'Annulée'),
    )
    status = models.CharField(max_length=1, choices=STATUS, verbose_name="Statut de la commande", blank=True)

    def __str__(self):
        return self

    class Meta:
        verbose_name = "réservation"

    @property
    def total(self):
        total = 0
        booking_details = BookingDetail.objects.filter(booking_id=self.id)
        for booking_detail in booking_details:
            total += booking_detail.total()
        return round(total,2)

    def ouvrages_qty(self):
        qtys = 0
        booking_details = BookingDetail.objects.filter(booking_id=self.id)
        for booking_detail in booking_details:
            qtys += booking_detail.qty
        return qtys

class BookingDetail(models.Model):
    """
    Une ligne de commande référence un produit, la quantité commandée ainsi que les prix associés.
    Elle est liée à une commande.
    """
    booking = models.ForeignKey(Booking, verbose_name="Commande associée", on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    qty = models.IntegerField(verbose_name="Quantité")

    # def total_ht(self):
    #     return round(self.product_unit_price * float(self.qty), 2)

    # def total_vat(self):
    #     return round(self.product_unit_price * float(self.qty) * self.vat, 2)

    def total(self):
        return round(self.ouvrage.price * self.qty, 2)

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # La liaison OneToOne vers le modèle User

    def __str__(self):
        return "Profil de {0}".format(self.user.username)


class History(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField('Date', default=datetime.now)
    TYPE_CHOICES = [
        ('Vente', 'Vente'),
        ('Arrivage', 'Arrivage'),
    ]
    type = models.CharField('Type', choices=TYPE_CHOICES, max_length=10, default='')
    reference = models.BigIntegerField("Référence", blank=True, null=True)
    title = models.CharField("Titre", max_length=200)
    auteurs = models.CharField("Auteurs", max_length=400)
    editeurs = models.CharField("Editeur", max_length=200)
    price = models.DecimalField("Prix", max_digits=5, decimal_places=2, null=True)
    CAT_PRICE_CHOICES = [
        ('SELIO', 'SELIO'),
        ('Editeur', 'Editeur'),
        ('Dépôt', 'Dépôt'),
        ('Occasion', 'Occasion'),
    ]
    catPrice = models.CharField('CatPrice', choices=CAT_PRICE_CHOICES, max_length=10, default='SELIO')
    PAYMENT_CHOICES = [
        ('Espèces', 'Espèces'),
        ('Chèque', 'Chèque'),
        ('Carte', 'Carte'),
    ]
    payment = models.CharField('Payment', choices=PAYMENT_CHOICES, max_length=10, default='Espèces')
    fournisseur = models.CharField('Fournisseur', max_length=50, default='')
    quantity = models.IntegerField('Quantité', default=1)
    comment = models.CharField('Commentaire', max_length=10, blank=True, default='')