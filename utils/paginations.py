from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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

class FriendshipPagination(PageNumberPagination):
    """
    Custom pagnation class.

    Now only for Friendship model, we might change this name later
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