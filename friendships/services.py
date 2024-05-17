from django.conf import settings
from django.core.cache import caches

from friendships.models import Friendship
from twitter.cache import FOLLOWING_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']
# to define testing and prod cache setting


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 错误的写法一
        # 这种写法会导致 N + 1 Queries 的问题
        # 即，filter 出所有 friendships 耗费了一次 Query
        # 而 for 循环每个 friendship 取 from_user 又耗费了 N 次 Queries
        # N 次 Queries 很重要的一个原因就是 objects.filter 实际上是懒惰加载
        # 懒惰加载即返回一个 iterator 对象，访问到了那个 item 才查询数据库
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误的写法二
        # 这种写法是使用了 JOIN 操作，让 friendship table 和 user table 在 from_user
        # 这个属性上 join 了起来。join 操作在大规模用户的 web 场景下是禁用的：因为非常慢。
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')  # select_related 会被翻译成 LEFT_JOIN 语句
        # return [friendship.from_user for friendship in friendships]

        # 正确的写法一，自己手动 filter id，使用 IN Query 查询
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids) 
        # 最后这一句的 __in 可以实现丢一个查询，让MySQL提供多个答案

        # 正确的写法二，使用 prefetch_related，会自动执行成两条语句，用 In Query 查询
        # 实际执行的 SQL 查询和上面是一样的，一共两条 SQL Queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]
    
    @classmethod
    def has_followed(cls, from_user, to_user):
        """
        This function is useless after we added the following functions
        """
        return Friendship.objects.filter(
            from_user=from_user, 
            to_user=to_user
        ).exists()
    
    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        """
        Get the following user id set based on the from_user_id
        """
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        # FOLLOWING_PATTERN is under the directory 'twitter', as this is a shared feature for the whole project
        user_id_set = cache.get(key) 
        # don't need try and catch
        # Please note, memcached only uses the string to store, here contains a de-serialization step.
        if user_id_set is not None:
            # if there is nothing in the cache, return None
            return user_id_set
        # if user_id_set is None:
        friendships = Friendship.objects.filter(from_user_id=from_user_id) # query first
        user_id_set = set([
            fs.to_user_id 
            for fs in friendships
        ]) # then convert to set
        cache.set(key, user_id_set) # save to the cache
        # Please note, memcached only uses the string to store, here contains a serialization step.
        return user_id_set
        # Learning note: when will the cache disappear?
        # 1. Manually delete
        # 2. Expired due to the TTL
        # 3. Low memory: delete the LRU, least recently used, cached keys
    
    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        """
        Invalidate the following cache

        In production, if there are any changes in the following cache
        We normally invalid it directly, rather than update it.
        Why?
        This is to avoid the inconsistancy caused by async tasks (exp)
        Also, memcached can only support string as value, it doesn't support append/add natively
        """
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def get_following_user_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]