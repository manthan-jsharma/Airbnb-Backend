from django.db import models


class Host(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    is_superhost = models.BooleanField(default=False)
    joined_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reviews_count = models.IntegerField(default=0)
    property_type = models.CharField(max_length=100, blank=True, null=True)
    host = models.ForeignKey(
        Host, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=1000)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.listing.title}"


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"


class ListingAmenity(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amenity.name} for {self.listing.title}"

    class Meta:
        unique_together = ('listing', 'amenity')
        verbose_name_plural = "Listing Amenities"
