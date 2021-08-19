from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('history', views.history, name="history"),
    path('dataBase', views.dataBase, name="dataBase"),
    path('histBase', views.histBase, name="histBase"),
    path('login', views.connexion, name="login"),
    path('logout', views.deconnexion, name="logout"),
    path('store', views.store, name="store"),
    path('propos', views.propos, name="propos"),
    path('', views.index, name="index"),
    path('add_to_basket', views.add_to_basket, name="add_to_basket"),
    path('basket', views.basket, name="basket"),
    path('<ouvrage_id>', views.detail, name="detail"),
]
