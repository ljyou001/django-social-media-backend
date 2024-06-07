from testing.testcases import TestCase
from utils.redis_client import RedisClient


class UtilsTests(TestCase):

    def setUp(self):
        super(UtilsTests, self).setUp()

    def test_redis_client(self):
        conn = RedisClient.get_connection()

        # # set, get
        # conn.set('a', 'b')
        # self.assertEqual(conn.get('a'), b'b')
        # self.assertIsNone(conn.get('c'))

        # # hset, hget
        # conn.hset('hash', 'key', 'value')
        # self.assertEqual(conn.hget('hash', 'key'), b'value')
        # self.assertIsNone(conn.hget('hash', 'key2'))

        # llen, lpush, rpush
        conn.lpush('list', '1')
        conn.rpush('list', '2')
        cached_list = conn.lrange('list', 0, -1)
        # Need to pay attention here
        # In redis, slicing function here, both 0 and -1 are included
        self.assertEqual(cached_list, [b'1', b'2'])
        # The result will also saved as binary strings, so we need to use b'2' here.

        # # sadd, smembers
        # conn.sadd('set', 'a')
        # self.assertEqual(conn.smembers('set'), {b'a'})
        # self.assertEqual(conn.smembers('set2'), set())

        RedisClient.clear()
        cached_list = conn.lrange('list', 0, -1)
        self.assertEqual(cached_list, [])