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
    """
    Un client est une personne inscrite au site dans le but d'effectuer une commande.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Contact", null=True)
    default_shipping_address = models.ForeignKey("Address",
                                                 related_name="default_shipping_address",
                                                 null=True,
                                                 verbose_name="Adresse de livraison par défaut",
                                                 on_delete=models.CASCADE
                                                 )
    default_invoicing_address = models.ForeignKey("Address",
                                                  related_name="default_invoicing_address",
                                                  null=True,
                                                  verbose_name="Adresse de facturation par défaut",
                                                  on_delete=models.CASCADE
                                                  )

    @property
    def __unicode__(self):
        return self.user.username + " (" + self.user.first_name + " " + self.user.last_name + ")"

    def addresses(self):
        return Address.objects.filter(contact_id=self.id)

    @property
    def bookings(self):
        return Booking.objects.filter(contact_id=self.id).order_by('-id')


class Address(models.Model):
    """
    Une adresse est liée à un client et pourra être utilisée pour la livraison ou la facturation d'une commande.
    """
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    MISTER = 'MR'
    MISS = 'MISS'
    MISSES = 'MRS'
    GENDER = (
        (MISTER, 'Monsieur'),
        (MISS, 'Mademoiselle'),
        (MISSES, 'Madame'),
    )
    gender = models.CharField(max_length=4, choices=GENDER, default=MISTER, verbose_name="Civilité")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    company = models.CharField(max_length=50, blank=True, verbose_name="Société")
    address = models.CharField(max_length=255, verbose_name="Adresse")
    additional_address = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    postcode = models.CharField(max_length=5, verbose_name="Code postal")
    city = models.CharField(max_length=50, verbose_name="Ville")
    phone = models.CharField(max_length=10, verbose_name="Téléphone")
    mobilephone = models.CharField(max_length=10, blank=True, verbose_name="Téléphone portable")

    class Meta:
        verbose_name = 'Adresse'
        verbose_name_plural = 'Adresses'

    def __unicode__(self):
        return self.first_name + " " + self.last_name + " (" + self.address + ", " + self.postcode + " " + self.city + ")"


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
    ## WAITING = 'W'
    ## KONTACTED = 'K'
    ## PAID = 'P'
    ## SHIPPED = 'S'
    ## CANCELED = 'C'
    ## DELETED = 'D'
    STATUS = [
        ('W', 'En attente de validation'),
        ('K', 'Contacté'),
        ('P', 'Payée'),
        ('S', 'Expédiée'),
        ('C', 'Annulée'),
        ('D', 'Annulé'),
    ]
    status = models.CharField(max_length=1, choices=STATUS, verbose_name="Statut de la commande", null=True)

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

    @property
    def bookingdetails(self):
        return BookingDetail.objects.filter(booking_id=self.id).order_by('-id')


class BookingDetail(models.Model):
    """
    Une ligne de commande référence un produit, la quantité commandée ainsi que les prix associés.
    Elle est liée à une commande.
    """
    booking = models.ForeignKey(Booking, verbose_name="Commande associée", on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.PROTECT)
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