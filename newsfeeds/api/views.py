from django.utils.decorators import method_decorator
from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    @method_decorator(ratelimit(key='user', rate='5/s', method='GET', block=True))
    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        # cached_newsfeeds only covers the first 200 pieces of data
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        # paginate and determine whether to return paginated data or None
        if page is None:
            # If page is None, that means we need to fetch data from DB
            # Because the data we need is not in the cache
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context = {'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)