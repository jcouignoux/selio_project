import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.db.transaction import commit
from django.shortcuts import render
from django.db import transaction

from .models import Contact, Address
from .forms import ContactForm


def create_contact(email, CForm_dsa, CForm_dia):
    with transaction.atomic():
        dsa = CForm_dsa.save(commit=False)
        dia = CForm_dia.save(commit=False)
        username = dsa.first_name + '_' + dsa.last_name + '_'
        test_user = User.objects.filter(username__startswith=username).order_by('-username').first()
        if test_user == None:
            username = username + '1'
        else:
            suffix = int(test_user.username.split("_")[-1])
            username = username + str(suffix + 1)
        user = User(
                    username=username,
                    email=email,
                    # password=dict['password'],
                    password = "default2021"
        )
        group = Group.objects.get(name='contacts')
        user.save()
        contact = Contact(
                            user=user,
        )
        contact.save()
        dsa.contact = contact
        dsa.save()
        dia.contact = contact
        dia.save()

    return contact

def connect_contact(request, contact):
    username = contact.user.username
    password = contact.user.password
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)

    return render(request, 'store/basket.html')


def update_contact(contact, CForm_dsa, CForm_dia):
    dsa = CForm_dsa.save()
    dia = CForm_dia.save()

    return contact