from django.test import TestCase
from django.urls import reverse

from .models import Ouvrage, Author, Publisher, Categorie, History
from .forms import DateRangeForm, VenteForm

# Create your tests here.
class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class DetailPageTestCase(TestCase):

    # test that detail page returns a 200 if the item exists.
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

class VentePageTestCase(TestCase):
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