from django.shortcuts import get_object_or_404

from .models import History, Ouvrage

def add_to_history(ouvrage_id, quantity, date):
    print('test')
    ouvrage = get_object_or_404(Ouvrage, id=ouvrage_id)
    history = History.objects.create(
        reference=ouvrage.reference,
        title=ouvrage.title,
        auteurs=ouvrage.auteurs.first(),
        editeurs=ouvrage.editeurs.first(),
        price=ouvrage.price,
        catPrice="SELIO",
        fournisseur="",
        payment="Chèque",
        quantity=quantity,
        date=date,
        comment="Vente Site"
    )
    ouvrage.stock -= 1
    if ouvrage.stock <= 0:
        # ouvrage.available = False
        pass
    ouvrage.save()
    return ouvrage