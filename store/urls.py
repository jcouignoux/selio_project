from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('history', views.history, name="history"),
    path('dataBase', views.dataBase, name="dataBase"),
    path('histBase', views.histBase, name="histBase"),
    path('login', views.connexion, name="login"),
    path('logout', views.deconnexion, name="logout"),
    path('propos', views.propos, name="propos"),
    path('add_to_basket', views.add_to_basket, name="add_to_basket"),
    path('basket', views.basket, name="basket"),
    path('booking', views.booking, name="booking"),
    path('booking/<booking_id>', views.booking_detail, name="booking_detail"),
    # path('contacts', views.ContactListView.as_view(), name="contact"),
    path('contact/<contact_id>', views.contact_detail, name="contact_detail"),
    path('contacts', views.contact, name="contact"),
    path('<ouvrage_id>', views.detail, name="detail"),
    path('<select_type>/<select_id>', views.store, name="store"),
    path('', views.index, name="index"),
]
