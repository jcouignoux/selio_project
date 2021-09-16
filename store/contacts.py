import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render

from .models import Contact, Address


def create_contact(dict):
    username = dict['dsa']['first_name'] + '_' + dict['dsa']['last_name'] + '_'
    test_user = User.objects.filter(username__startswith=username).order_by('-username').first()
    print(test_user)
    if test_user:
        print(test_user.username.split("_")[2])
        username_temp = test_user.username.split("_")
        username = "_".join((username_temp[0], username_temp[1], str(int(username_temp[2]) + 1)))
    else:
        username = dict['dsa']['first_name'] + '_' + dict['dsa']['last_name'] + '_1'
    user = User.objects.create(
                username=username,
                email=dict['dsa']['email'],
                # password=dict['password'],
                password = "default2021"
    )
    group = Group.objects.get(name='contacts')
    user.groups.add(group)
    user.save()
    contact = Contact.objects.create(
                        user=user,
    )
    for type in ('dsa', 'dia'):
        default_address = Address.objects.create(
            contact=contact,
            gender=dict[type]['gender'],
            first_name=dict[type]['first_name'],
            last_name=dict[type]['last_name'],
            address=dict[type]['address'],
            additional_address=dict[type]['additional_address'],
            postcode=dict[type]['postcode'],
            city=dict[type]['city'],
            phone=dict[type]['phone'],
            mobilephone=dict[type]['mobilephone'],
        )
        if type == 'dsa':
            contact.default_shipping_address = default_address
        elif type == 'dia':
            contact.default_invoicing_address = default_address
        contact.save()

    return contact

def connect_contact(request, contact):
    username = contact.user.username
    password = contact.user.password
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)

    return render(request, 'store/basket.html')