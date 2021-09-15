from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Booking, Contact, Ouvrage, Author, Publisher, Categorie, History, Address
from .forms import UserForm, AddressForm
from .urls import urlpatterns

# Create your tests here.
class PagesTestCase(TestCase):

    # test that detail page returns a 200 if the item exists.
    def test_index_page(self):
        response = self.client.get(reverse('store:index'))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_returns_200(self):
        impossible = Ouvrage.objects.create(title="Transmission Impossible")
        ouvrage_id = Ouvrage.objects.get(title='Transmission Impossible').id
        response = self.client.get(reverse('store:detail', args=(ouvrage_id,)))
        self.assertEqual(response.status_code, 200)

    def test_history_page_returns_302(self):
        impossible = History.objects.create(title="Transmission Impossible")
        histories = History.objects.all()
        response = self.client.get(reverse('store:history'), {
            'histories': histories,
        })
        self.assertEqual(response.status_code, 302)


class VenteTestCase(TestCase):
    # ...
    # test that a new booking is made
    def test_new_vente_is_registered(self):
        author = Author.objects.create(name='Couignoux', forname='Julien')
        publisher = Publisher.objects.create(name='JCEdition')
        impossible = Ouvrage.objects.create(
                        reference='12345678',
                        title='Transmission Impossible',
                        price=10,
                    )
        impossible.auteurs.add(Author.objects.get(name='Couignoux')),
        impossible.editeurs.add(Publisher.objects.get(name='JCEdition')),
        ouvrage_id = Ouvrage.objects.get(title='Transmission Impossible').id
        old_book_stock = Ouvrage.objects.get(id=ouvrage_id).stock
        response = self.client.post(reverse('store:detail', args=(ouvrage_id,)), {
            'catPrice': 'SELIO',
            'payment': 'Espèces',
            'fournisseur': '',
            'quantity': 1,
            'date': '2021-07-26',
            'comment': 'test'
        })
        new_book_stock = Ouvrage.objects.get(id=ouvrage_id).stock # count bookings after
        self.assertEqual(new_book_stock, old_book_stock - 1) # make sure 1 booking was added


class BookingTestCase(TestCase):
    # ...
    # test that a new basket is made
    def setUp(self):
        impossible = Ouvrage.objects.create(title="Transmission Impossible")
        self.ouvrage = Ouvrage.objects.get(title="Transmission Impossible")
        self.quantity = 1
        user = User.objects.create(username='John_Doe', password='Passwd', email='john.doe@gmail.com')
        self.user = User.objects.get(email='john.doe@gmail.com')
        contact = Contact.objects.create(user=user)
        self.contact = Contact.objects.get(user=user)
        address = Address.objects.create(
            contact=contact,
            first_name='John',
            last_name='Doe',
            address='123 Maple Street',
            postcode='17101',
            city='Anytown',
            phone='0123456789',
        )
        self.address = Address.objects.get(first_name='John')

    def test_new_basket_is_registered(self):
        ouvrage_id = str(self.ouvrage.id)
        quantity = 1
        basket = {}
        response = self.client.post(reverse('store:add_to_basket'), {
            'basket': basket,
            'ouvrage_id': ouvrage_id,
        }) # make sure 1 ouvrage with quantity was added
        new_basket = self.client.session['basket']
        self.assertEqual(new_basket, {ouvrage_id: quantity})

#    def test_booking_is_registered(self):
#        CForm = AddressForm(self.address.__dict__)
#        ouvrage_id = str(self.ouvrage.id)
#        session = self.client.session
#        self.client.login(username=self.user.username, password=self.user.password)
#        session['basket'] = {ouvrage_id: self.quantity}
#        session.save()
#        email = self.user.email
#        old_booking = Booking.objects.count()
#        response = self.client.post(reverse('store:basket'), {
#            'CForm': CForm,
#            'email': email,
#        }) # make sure 1 ouvrage with quantity was added
#        print(response)
#        new_booking = Booking.objects.count()
#        self.assertEqual(new_booking, old_booking + 1)