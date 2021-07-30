from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('history', views.history, name="history"),
    path('dataBase', views.dataBase, name="dataBase"),
    path('login', views.connexion, name="login"),
    path('logout', views.deconnexion, name="logout"),
    path('store', views.store, name="store"),
    path('propos', views.propos, name="propos"),
    path('', views.index, name="index"),
    path('<ouvrage_id>', views.detail, name="detail"),
]
