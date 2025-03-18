from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing
from .serializers import ListingSerializer, ListingDetailSerializer


class ListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'property_type']
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['price_per_night', 'rating', 'reviews_count']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ListingDetailSerializer
        return ListingSerializer

    def list(self, request, *args, **kwargs):
        # Handle custom query parameters
        location = request.query_params.get('location')
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        guests = request.query_params.get('guests')

        queryset = self.filter_queryset(self.get_queryset())

        # Apply additional filters based on custom parameters
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Note: In a real app, you would handle check_in, check_out, and guests
        # by querying availability data

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
