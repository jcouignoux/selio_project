from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('vente', views.vente, name="vente"),
    path('uploadCSV', views.uploadCSV, name="uploadCSV"),
    path('login', views.connexion, name="login"),
    path('logout', views.deconnexion, name="logout"),
    path('', views.index, name="index"),
    path('<ouvrage_id>', views.detail, name="detail"),
]
