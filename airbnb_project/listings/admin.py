from django.contrib import admin
from .models import Host, Listing, ListingImage, Amenity, ListingAmenity


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingAmenityInline(admin.TabularInline):
    model = ListingAmenity
    extra = 1


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_superhost', 'joined_date')
    search_fields = ('name',)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price_per_night',
                    'currency', 'rating', 'host')
    list_filter = ('property_type', 'currency')
    search_fields = ('title', 'location', 'description')
    inlines = [ListingImageInline, ListingAmenityInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
