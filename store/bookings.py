from .models import Booking, BookingDetail


def create_booking(contact, ouvrages):
    booking = Booking()
    booking.contact=contact.first()
    booking.status='W'
    booking.save()
    for ouvrage in ouvrages:
        booking_detail = BookingDetail()
        booking_detail.booking = booking
        booking_detail.ouvrage = ouvrage
        booking_detail.qty = ouvrage.qty
        booking_detail.save()
    return booking