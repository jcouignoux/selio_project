from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('propos', views.propos, name="propos"),
    path('basket', views.basket, name="basket"),
    path('add_to_basket', views.add_to_basket, name="add_to_basket"),
    path('booking', views.booking, name="booking"),
    path('booking/<booking_id>', views.booking_detail, name="booking_detail"),
    path('contacts', views.contact, name="contact"),
    path('contact/<contact_id>', views.contact_detail, name="contact_detail"),
    path('profil/<contact_id>', views.profil, name="profil"),
    path('profil/user/<user_id>', views.user_detail, name="user_detail"),
    path('history', views.history, name="history"),
    path('dataBase', views.dataBase, name="dataBase"),
    path('histBase', views.histBase, name="histBase"),
    path('login', views.connexion, name="login"),
    path('logout', views.deconnexion, name="logout"),
    path('test', views.test, name="test"),
    path('<select_type>/<select_id>', views.store, name="store"),
    path('<ouvrage_id>', views.detail, name="detail"),
]
