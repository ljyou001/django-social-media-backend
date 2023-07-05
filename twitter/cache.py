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

# redis
# ...