# Rate Limiter

## What is rate limiter and why

Rate limiter is a component to limit the number of requests to certain APIs or resources.

This is for the safety and protect system, especially the database, from attack.

## Key Characters

1. select some features to select, this is normally API by API
2. select time duration, normally, second, minute, hour and day, not month or year

## What Tools to Select

In this project, we will use django-ratelimit.

A rate limiter will store the rate information into the cache. (Think: why not DB/webserver)

## How it Works

Understand Tokenized method:

- Say, your limiter feature is IP and your limiter action is login
- Then, a key named "198.168.0.1:login" will be stored in memcached
- If the result is None, it means no such request before and you can store a value say 9, if limit is 10/s
- At the same time, set a timeout=1s, using a cache mechanism called TTL(time to live).
- If the value goes to 0, then stop the request

This is a very simple method but it is not so accurate as a rate limiter.

- Say, if your limit is 3/60s.
- You made requests at sec 1, 58 and 59
- Tokenized method will allow your requst at the second 61, 62
- Obviously, you were allowed 4 times at sec 58, 59, 61 and 62

Although, in rate limiter, we don't presue absolutely accurate since we just want to block out most of requsts flood is enough.
But, django-ratelimit also made some improvement to the purely tokenized method:

- It will record the timestamp (to second in this case) in the key for every individual request, say "192.168.0.1:login:20240525-142518"
- Then split 1 minutes to 60 seconds and generate 60 keys, request 60 times to the redis and sum up request number

It also made use of cache's mechanism:

- Memcached can also support get_many() to shorten the server-to-server round trip time
- Memcached/Redis can support a atomic operation for +-1 the request number, also expiry

As for limits based on hour, such as 10/hour, the timestamp will just go to minute level.

This is also called sliding window method. The advantage is it is more precise but it will have many requests to cache.

## Practical Use

### Install django-ratelimit

```shell
pip install django-ratelimit
```

### Add configs in settings

```python
RATELIMIT_USER_CACHE = 'ratelimit'
RATELIMIT_CACHE_PREFIX = 'rl:' # You can also delete this line and use the prefix above
RATELIMIT_ENABLE = not TESTING
```

### Use decorator for API

```python
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
...
@required_params(method='get', params=['tweet_id'])
@method_decorator(ratelimit(key='user', rate='3/m', method='GET', block=True)) # 3/m for learning
def list(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    comments = self.filter_queryset(queryset).\
            prefetch_related('user').\
            order_by('-created_at')
    serializer = CommentSerializer(
        comments, 
        many=True,
        context={'request': request},
    )
    return Response({
        'success': True, 
        'comments': serializer.data,
    }, status=status.HTTP_200_OK)
```

You can switch `@required_params` and `@method_decorator(ratelimit())`, but we don't suggest.

Because:

1. Decorators will run line by line, which mean `@required_params` first then `@method_decorator(ratelimit())`
2. `@required_params` will not request DB or cache, which means best performance and can filter some invalid requests
3. `@method_decorator(ratelimit())` is using cache to protect DB. We also want to make a clear level while requesting the API for better performance

### 403 Error or 429 Error

After you requested too many times, you will receive a 403 no premission error.

```shell
HTTP 403 Forbidden
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "detail": "You do not have permission to perform this action."
}
```

This error is thrown by Django-restframework and ratelimit together

In ratelimit's source code, it directly used the PermissionDenied exception from restframework, which is a 403 error

```python
from django.core.exceptions import PermissionDenied
class Ratelimited(PermissionDenied):
    pass
```

If we wan to change this exception value, then we need to add this to settings add this line and write your own method

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # Settings for django_filters
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],

    'EXCEPTION_HANDLER': ' utils.ratelimit.exception_handler',
}
```

## Your Own Improvement

Write you own rate limiter, for both methods