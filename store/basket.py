from django.shortcuts import get_object_or_404

from .models import Ouvrage


def update_basket(request, ouvrage_to_mod):
    if request.GET.get('quantity') == '-':
        request.session['basket'][ouvrage_to_mod] -= 1
    elif request.GET.get('quantity') == '+':
        request.session['basket'][ouvrage_to_mod] += 1
    elif request.GET.get('quantity') == 'x':
        del request.session['basket'][ouvrage_to_mod]
    request.session.modified = True
    ouvrages = []
    for ouvrage_id in request.session['basket'].keys():
        ouvrage = get_object_or_404(Ouvrage, pk=ouvrage_id)
        ouvrage.qty = request.session['basket'][ouvrage_id]
        ouvrages.append(ouvrage)
    
    return ouvrages