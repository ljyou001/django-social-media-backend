import time

from django.conf import settings
from django.core.cache import caches
from friendships.hbase_models import HBaseFollower, HBaseFollowing
from friendships.models import Friendship
from gatekeeper.models import GateKeeper
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
    def get_following_user_id_set(cls, from_user_id):
        """
        Get the following user id set based on the from_user_id
        """
        # TO DO: Cache in Redis
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            friendships = Friendship.objects.filter(from_user_id=from_user_id)
        else:
            friendships = HBaseFollowing.filter(prefix=(from_user_id, None))
        user_id_set = set([
            fs.to_user_id 
            for fs in friendships
        ]) 
        return user_id_set
    
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
    
    @classmethod
    def follow(cls, from_user_id, to_user_id):
        """
        Applied gatekeeper for MySQL and HBase
        Only on/off switch
        """
        if from_user_id == to_user_id:
            return None
        
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )

        # Create data in HBase
        now = int(time.time() * 1000000)
        HBaseFollower.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
        # You can return either one 
        return HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
    
    @classmethod
    def unfollow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return 0
        
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            # deleted: how many data got deleted
            # _: detailed number and type got deleted, ignored here
            deleted, _ = Friendship.objects.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).delete()
            return deleted

        instance = cls.get_follow_instance(from_user_id, to_user_id)
        if instance is None:
            return 0
        # Obtaining the instance is mainly for the create_at
        HBaseFollowing.delete(from_user_id=from_user_id, created_at=instance.created_at)
        HBaseFollower.delete(to_user_id=to_user_id, created_at=instance.created_at)
        return 1
    
    @classmethod
    def get_follow_instance(cls, from_user_id, to_user_id):
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        for follow in followings:
            if follow.to_user_id == to_user_id:
                return follow
        return None

    @classmethod
    def has_followed(cls, from_user_id, to_user_id):
        """
        New has_followed function has merged the old one and HBase one
        """
        if from_user_id == to_user_id:
            return True
        
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(
                from_user_id=from_user_id, 
                to_user_id=to_user_id,
            ).exists()
        
        instance = cls.get_follow_instance(from_user_id, to_user_id)
        return instance is not None
    
    @classmethod
    def get_following_count(cls, from_user_id):
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(from_user_id=from_user_id).count()
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        return len(followings)
    
    