from django.shortcuts import get_object_or_404

from .models import Ouvrage


def update_basket(basket, ouvrage_to_mod, quantity):
    if quantity == '-':
        basket[ouvrage_to_mod] -= 1
    elif quantity == '+':
        basket[ouvrage_to_mod] += 1
    elif quantity == 'x':
        del basket[ouvrage_to_mod]
    ouvrages = []
    for ouvrage_id in basket.keys():
        ouvrage = get_object_or_404(Ouvrage, pk=ouvrage_id)
        ouvrage.qty = basket[ouvrage_id]
        ouvrages.append(ouvrage)
    
    return basket, ouvrages