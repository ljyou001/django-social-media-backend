from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        # page = self.paginate_queryset(self.get_queryset())
        queryset = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page, 
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)