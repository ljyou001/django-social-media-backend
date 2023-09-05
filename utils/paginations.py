from dateutil import parser
from rest_framework.pagination import BasePagination
from rest_framework.pagination import \
    PageNumberPagination as DjangoPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DjangoPageNumberPagination):
    """
    Custom pagnation class.

    Now only for Friendship model, we might change this name later

    # LEARNING NOTES: Pagnation in SQL and Django
    # pagination in database is using limit+offset to work
    #
    # mysql> select * from friendships_friendship;
    # +----+----------------------------+----------------------------+--------------+------------+
    # | id | created_at                 | updated_at                 | from_user_id | to_user_id |
    # +----+----------------------------+----------------------------+--------------+------------+
    # |  1 | 2023-06-28 08:19:40.899457 | 2023-06-28 08:19:40.899474 |            1 |          2 |
    # |  2 | 2023-06-28 08:19:46.292246 | 2023-06-28 08:19:46.292269 |            2 |          1 |
    # |  3 | 2023-06-28 08:19:55.311838 | 2023-06-28 08:19:55.311855 |            1 |          4 |
    # |  4 | 2023-06-28 08:19:59.119997 | 2023-06-28 08:19:59.120018 |            1 |          5 |
    # +----+----------------------------+----------------------------+--------------+------------+
    # 4 rows in set (0.00 sec)
    #
    # mysql> select * from friendships_friendship order by created_at desc limit 2 offset 1;
    # +----+----------------------------+----------------------------+--------------+------------+
    # | id | created_at                 | updated_at                 | from_user_id | to_user_id |
    # +----+----------------------------+----------------------------+--------------+------------+
    # |  3 | 2023-06-28 08:19:55.311838 | 2023-06-28 08:19:55.311855 |            1 |          4 |
    # |  2 | 2023-06-28 08:19:46.292246 | 2023-06-28 08:19:46.292269 |            2 |          1 |
    # +----+----------------------------+----------------------------+--------------+------------+
    # 2 rows in set (0.01 sec)
    #
    # naked mysql> select ? from <table> order by <order> desc limit <page_size> offset <(page-1)*page_size>;
    #
    # In Django, it has overriden the slice function in python, so you can use the following:
    # $ python manage.py shell
    # >>> from friendships.models import Friendship
    # >>> Friendship.objects.all().order_by('-created_at')[:2]
    #
    # >>> queryset.order_by(<order>)[<offset>：<offset+pagesize>]
    #
    #
    # To better utilize pagnation, we created this class in the utils.paginations.py
    """
    
    page_size = 20
    # Default page size
    page_size_query_param = 'page_size' 
    max_page_size = 100
    # page_size_query_param has default value None, don't allow client to set the page size
    # Now we allow client to set the page size and max_page_size is the max page size
    # max_page_size default value is None, which means no limitation

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next': self.page.has_next(),
            'results': data,
        })


class EndlessPagination(BasePagination):
    """
    Endless Pagination for Newsfeed and Tweets

    # LEARNING NOTES: Why endless pagenation?
    # this is because user could created new items while you are reading the tweets
    # Say user1 has the following tweets for now [6,5,4,3,2,1]
    # and you want the 1st page of the tweets with size 3, 
    # GET /api/tweets?user_id=1&page_size=3
    # you will get [6,5,4]
    # However, user1 created tweets before you go to the next page [7,6,5,4,3,2,1]
    # GET /api/tweets?user_id=1&page_size=3&page=2
    # you will get [4,3,2], which mean you have get 4 for twice.
    # Still it could be worse...
    # 
    # That's why we need to use the EndlessPagination
    # anchored by "less_than", we will not get the same or messed up results
    # normally we use snowflake algo for this kind of pagination
    # However, here we directly use the created_at for simplification
    """

    page_size = 20
    max_upside_paginate = 100 

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False
        self.beyond_upside_paginate = False

    def to_html(self):
        pass
    
    def paginate_ordered_list(self, reverse_order_list, request):
        """
        Very brute force way to paginate the ordered list
        Assume all data are in the cache.
        We will discuss later if only particial data is in the cache
        """
        # Getting newer data
        if 'created_at__gt' in request.query_params:
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            # Why isoparse?
            # We want to unify the time format, then we can compare the created_at
            # originally 2023-06-28 08:19:40.123456 to datetime
            objects = []
            for obj in reverse_order_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects
        
        index = 0
        # Getting older data
        if 'created_at__lt' in request.query_params:
            created_at__gt = parser.isoparse(request.query_params['created_at__lt'])
            for index, obj in enumerate(reverse_order_list):
                if obj.created_at < created_at__gt:
                    break
            else:
                reverse_order_list = []
            # for-else: else is tracking to break in the for loop
            # If there is a break hit in the loop, then else block will not executed
            # Otherwise, else block will be executed
        self.has_next_page = len(reverse_order_list) > index + self.page_size 
        return reverse_order_list[index: index + self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)
        
        if 'created_at__gt' in request.query_params:
            # Upside pagination
            # Directly return all the items greter than the created_at
            self.beyond_upside_paginate = False
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            if len(queryset) <= self.max_upside_paginate:
                return queryset.order_by('-created_at')
            self.beyond_upside_paginate = True

        if 'created_at__lt' in request.query_params:
            # Downside pagination processing
            self.beyond_upside_paginate = False
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)
        
        # Also include: neither parm situation
        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        # Using the page_size + 1 to know whether there is a next page
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]
    
    def get_paginated_response(self, data):
        return Response({
            'beyond_upside_paginate': self.beyond_upside_paginate,
            'has_next_page': self.has_next_page,
            'results': data,
        })