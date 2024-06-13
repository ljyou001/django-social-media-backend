from utils.redis_client import RedisClient
# Gatekeeper is stored in the redis since we assume we will used it high frequently
# Most of the new features in production require a Gatekeeper


class GateKeeper(object):

    @classmethod
    def get(cls, gk_name):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        # this is how we name the gatekeeper
        if not conn.exists(name):
            return {'percent': 0, 'description': ''}
            # if no such gatekeeper found, then we think it is closed
            # therefore, return percentage 0
        redis_hash = conn.hgetall(name)
        # get all means to get all the key-value pairs in the redis under the key name
        return {
            'percent': int(redis_hash.get(b'percent', 0)), # b here is because redis also use binary to store data
            'description': str(redis_hash.get(b'description', ''))
        }
    
    @classmethod
    def set_kv(cls, gk_name, key, value):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        conn.hset(name, key, value)

    @classmethod
    def is_switch_on(cls, gk_name):
        """
        This is a simple switch only support on/off
        """
        return cls.get(gk_name)['percent'] == 100

    @classmethod
    def in_gk(cls, gk_name, user_id):
        """
        This is a funnel that can apply percentage to control gatekeeper on/off.

        Why use user_id?
        We want a the result of this filter should be stable.
        One user can pass this funnel then he should not be blocked unless you change the percent
        Also, if you increase the percentage, we still want the original users pass the gatekeeper
        """
        return user_id % 100 < cls.get(gk_name)['percent']
    
    @classmethod
    def turn_on(cls, gk_name):
        cls.set_kv(gk_name, 'precent', 100)

    @classmethod
    def turn_off(cls, gk_name):
        cls.set_kv(gk_name, 'precent', 0)