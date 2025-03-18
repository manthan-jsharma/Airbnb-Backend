from rest_framework import serializers
from .models import Listing, Host, ListingImage, Amenity, ListingAmenity


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['id', 'name', 'image_url', 'is_superhost', 'joined_date']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image_url', 'is_primary']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class ListingSerializer(serializers.ModelSerializer):
    host = HostSerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'location', 'address', 'price_per_night',
            'currency', 'total_price', 'rating', 'description',
            'reviews_count', 'property_type', 'host', 'images',
            'amenities', 'created_at', 'updated_at'
        ]

    def get_amenities(self, obj):
        amenities = Amenity.objects.filter(
            id__in=ListingAmenity.objects.filter(
                listing=obj).values_list('amenity_id', flat=True)
        )
        return AmenitySerializer(amenities, many=True).data


class ListingDetailSerializer(ListingSerializer):
    class Meta(ListingSerializer.Meta):
        pass
