from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from .models import Address, Booking, Contact, Ouvrage, Author, Publisher, Categorie

# Register your models here.

class AdminURLMixin(object):
    def get_admin_url(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:store_%s_change" % (
            content_type.model),
            args=(obj.id,))


# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin, AdminURLMixin):
#     list_filter = ['created_at', 'contacted']
#     fields = ["created_at", "contact_link", 'ouvrage_link', 'contacted']
#     readonly_fields = ["created_at", "contact_link", "ouvrage_link", "contacted"]
# 
#     def has_add_permission(self, request):
#         return False
# 
#     def contact_link(self, booking):
#         url = self.get_admin_url(booking.contact)
#         return mark_safe("<a href='{}'>{}</a>".format(url, booking.contact.name))
# 
#     def ouvrage_link(self, booking):
#         url = self.get_admin_url(booking.ouvrage)
#         return mark_safe("<a href='{}'>{}</a>".format(url, booking.ouvrage.title))
# 
# class BookingInline(admin.TabularInline, AdminURLMixin):
#     model = Booking
#     extra = 0
#     readonly_fields = ["created_at", "ouvrage_link", "contacted"]
#     fields = ["created_at", "ouvrage_link", "contacted"]
#     verbose_name = "Réservation"
#     verbose_name_plural = "Réservations"
# 
#     def has_add_permission(self, request):
#         return False
# 
#     def ouvrage_link(self, booking):
#         url = self.get_admin_url(booking.ouvrage)
#         return mark_safe("<a href='{}'>{}</a>".format(url, booking.ouvrage.title))
# 
#     ouvrage_link.short_description = "Ouvrage"

class UserInline(admin.TabularInline, AdminURLMixin):
    model = User
    extra = 0
    fieldsets = [
        (None, {'fields': ['email',]})
        ] # list columns


class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'postcode', 'city', 'contact')


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    inlines = [
        AddressInline,
    ]


class OuvrageAuthorInline(admin.TabularInline):
    model = Ouvrage.auteurs.through
    extra = 1
    verbose_name = "Ouvrage"
    verbose_name_plural = "Ouvrages"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    # inlines = [OuvrageAuthorInline,]
    search_fields = ['title']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ['nom', 'marge']

@admin.register(Categorie)
class CategoriAdmin(admin.ModelAdmin):
    search_fields = ['nom',]