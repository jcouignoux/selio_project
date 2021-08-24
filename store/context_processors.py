
from .models import Booking

def get_booking(request):
    bookings_list= Booking.objects.filter(contacted=False).order_by('created_at')
    return {'bookings_list': bookings_list}