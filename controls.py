import json
import os
import tempfile
import boto3 as boto3
import pandas as pd
import redis
import matplotlib
from botocore.exceptions import NoCredentialsError

matplotlib.use('Agg')  # Use the Agg backend
import matplotlib.pyplot as plt

# get settings
path = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(path) as f:
    data = json.load(f)


def get_data_from_redis(objects) -> dict:
    """Process dara from redis cloud"""
    return {key: redis_client.get_data(key) for key in objects}


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

    def get_data(self, object: str) -> int:
        """Get data from redis cloud"""
        cache_key = f'detection_object:{object}'
        try:
            with redis.Redis(connection_pool=self.pool) as r:
                cached_data = r.get(cache_key)
                if cached_data:
                    return eval(cached_data).get('count')
                return 1

        except Exception as err:
            print(f'Error get data from redis {err}')
            return 1


class DataProcess:
    def __init__(self, data: dict, emission_values: tuple, access_key:str, secret_key:str, region ='eu-central-1'):
        # generate data
        self.data = [{'object_type': object_type, 'count': count} for object_type, count in data.items()]
        # create data frame
        self.df = pd.DataFrame(self.data)
        # add emissions values
        self.df['emission'] = emission_values
        # calculate emissions
        self.df['count_emission'] = self.df['count'] * self.df['emission']

        # initialize  aws client
        self.session = boto3.Session(aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key,
                                     region_name=region)
        self.s3 = self.session.client('s3')

    def emission_diagram(self):
        # sort dataframe
        df_sorted = self.df.sort_values(by='count_emission', ascending=False)
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.bar(df_sorted['object_type'], df_sorted['count_emission'], color='skyblue')
        plt.xlabel('Object Type')
        plt.ylabel('Total Emission')
        plt.title('Total Emission by Object Type')
        plt.xticks(rotation=45)  # Rotate labels to make them readable
        # Save the plot to a file instead of showing it
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            # Make sure to close plt to release memory
            plt.close()
            # Now upload the file to S3
            try:
                self.s3.upload_file(tmpfile.name, data.get('bucket_name'), "diagram0.png")

            except NoCredentialsError as err:
                print(f'Upload Error: {err}')
            else:
                print('Saved to s3')


    def count_diagram(self):
        # sort dataframe
        df_sorted = self.df.sort_values(by='count', ascending=False)
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.bar(df_sorted['object_type'], df_sorted['count'], color='magenta')
        plt.xlabel('Object Type')
        plt.ylabel('Total count')
        plt.title('Total Detected Objects')
        plt.xticks(rotation=45)  # Rotate labels to make them readable
        # Save the plot to a file instead of showing it

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            plt.close()  # Release memory
            # Upload to S3
            try:
                self.s3.upload_file(tmpfile.name, data.get('bucket_name'), "diagram1.png")

            except NoCredentialsError as err:
                print(f'Upload Error: {err}')

            else:
                print('Saved to s3')


# initialize redis client
redis_client = RedisClient(data.get('redis_endpoint'), data.get('redis_port'), data.get('redis_password'))
