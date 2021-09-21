
from .models import Booking, BookingDetail, Categorie, Author, Publisher, User, Contact
from django.contrib.auth.decorators import login_required


def get_contact(request):
    if request.user.is_authenticated and not request.user.is_staff:
        contact = Contact.objects.filter(user=request.user).first()
    else:
        contact = 0
    return {'contact': contact}

def get_booking(request):
    # bookings_list = Booking.objects.filter(contacted=False).order_by('created_at')
    bookings_list = Booking.objects.exclude(status__contains='S')
    # booking_detail_list = BookingDetail.objects.all()
    return {
        'bookings_list': bookings_list,
        #'booking_detail_list': booking_detail_list,
        }

def get_categories(request):
    categories_list = Categorie.objects.all().order_by('name')
    return {'categories_list': categories_list}

def get_authors(request):
    authors_list = Author.objects.all().order_by('name')
    return {'authors_list': authors_list}

def get_publishers(request):
    publishers_list = Publisher.objects.all().order_by('name')
    return {'publishers_list': publishers_list}