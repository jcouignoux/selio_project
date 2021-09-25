from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User

from .models import History, Ouvrage, Booking

def add_to_history(ouvrage_id, quantity, date):
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

def send_email(address, content):
    subject = content['subject']
    # message = content['message']
    from_email = "no-reply@selio4.org"
    to = [address, ]
    bcc = [User.objects.get(username='jcouignoux').email, ]
    # attachments = ['attachments', ]
    auth_user = User.objects.get(username='jcouignoux').email
    auth_password = User.objects.get(username='jcouignoux').password
    
    html = content['html']
    # html_content = render_to_string('store/email.html', {'booking': content['booking']})
    html_content = render_to_string('store/' + str(html), {'message': content['message']})
    text_content = strip_tags(html_content)
    # d = {'username': 'username' }

    # body = htmly.render(d)

    # email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to, bcc=bcc, )
    # email.attach_alternative(subject=subject, body=text_content, from_email=from_email, to=to, bcc=bcc, )
    response = send_mail(subject, html_content, from_email, to, html_message=html_content)
    # response = email.send()

    return response