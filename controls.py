import json
import os
import redis

# get settings
path = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(path) as f:
    data = json.load(f)


class RedisClient:
    def __init__(self, host, port, password):
        """Initializes the RedisClient instance by setting up a connection pool to Redis."""

        # Initialize Redis connection pool
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )

    def test_redis_connection(self):
        """Tests the Redis connection by setting and then getting a value."""
        test_key = "test_connection_key"
        test_value = "hello_redis"
        try:
            # Use the connection pool to get a Redis connection
            with redis.Redis(connection_pool=self.pool) as r:
                # Set a value in Redis
                r.set(test_key, test_value)
                # Retrieve the value from Redis
                retrieved_value = r.get(test_key)

                # Check if the set and get operations were successful
                if retrieved_value == test_value:
                    print("Redis connection test successful: Value set and retrieved correctly.")
                else:
                    print("Redis connection test failed: Retrieved value does not match the set value.")
        except redis.RedisError as e:
            print(f"Redis connection test failed with an error: {e}")


    def get_data(self,object:str):
        """Get data from redis cloud"""
        cache_key = f'detection_object:{object}'
        try:
            with redis.Redis(connection_pool=self.pool) as r:
                cached_data = r.get(cache_key)
                if not cached_data:
                    return 1
                return cached_data

        except Exception as err:
            print(f'Error get data from redis {err}')
            return None


# initialize redis client
redis_client = RedisClient(data.get('redis_endpoint'), data.get('redis_port'), data.get('redis_password'))



def get_data_from_redis()->dict:
    """Process dara from redis cloud"""
    detected_objects = ('car', 'motorbike', 'bus', 'truck', 'person', 'dog', 'bicycle', 'cat')

    data = {key:redis_client.get_data(key) for key in detected_objects}

    return data