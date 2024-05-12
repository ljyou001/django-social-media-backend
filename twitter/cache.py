# memcached: for firendships - followings
FOLLOWING_PATTERN = 'followings:{user_id}'
# Why this constant?
# This is to define the key format of your requests
# As memcached is just like a hash table in the memory
# You need to define the globally unique key for the cache operations
# 
# Why not followers?
# The answered should baesed on the real use case
# 1. follower could be very big, but not too much get requests
# 2. follower could be update very fast

# Memcache for friendship is not so good, but it is perfect for user and profile model
# This is because:
# 1. memcached is not natively support for set, so it is better to save objects
# 2. User and Profile model will not be changed so easily, therefore, it can have a over 98% hit rate

USER_PROFILE_PATTERN = 'user_profile:{user_id}'

# redis
USER_TWEETS_PATTERN = 'user_tweets:{user_id}'
USER_NEWSFEEDS_PATTERN = 'newsfeeds:{user_id}'