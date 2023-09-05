# Redis

## About Redis
Similar to Memcached, it is also a "key-value" database
Both are for high efficiency, simple query.

Different from MySQL, the relational DB, complicated query, low efficiency. 
However, Memcached can only preserve data in RAM for faster access.
Redis can preserve data in the disk.

Redis can also support more format compared to Memcached.

Redis: 100k QPS
Memcached: 1M QPS
MySQL: 1k QPS avg

## In this project
We will use Redis to cache the tweet information

Say, a user posted a tweet, we can cache it into the Redis as list
This is important for celebrities.
Cuz normally Tweets for one user are 
1. a lot of GET, especially for celebrities.
2. not too many POST, nobody creat too many unless robot
3. not too much storage consumption, say only top 100 tweets.

## How to insatll?

1. Docker
2. Directly install

In our case, we can directly:
```
sudo apt install redis
sudo pip install redis
redis-server
```

While using redis, DO NOT put it into the setting.CACHES
Cuz Django cache can only support strings, 
which means you cannot take the advantages of the redis.
So we need to DIY wrap it up.
Check the code for commit 29