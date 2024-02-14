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

def upload_configuration(config_file: str = 'settings.json') -> dict:
    """
    Loads configuration settings from a specified JSON file.
    :param config_file: The name of the configuration file
    :return: A dictionary containing the configuration settings.
    """
    path = os.path.join(os.path.dirname(__file__), config_file)
    with open(path) as f:
        data = json.load(f)

    return data


def get_data_from_redis(objects) -> dict:
    """
     Retrieve and process data from Redis for the specified objects.

    :param objects: A sequence of object keys to retrieve data for.
    :return: A dictionary with object keys and their associated data.

    """


class RedisClient:
    def __init__(self):
        """
        Initialize the Redis client with connection settings from configuration.
        """

        # Initialize Redis connection pool
        self.r = redis.Redis(
            host=configuration.get('redis_endpoint'),
            port=configuration.get('redis_port'),
            password=configuration.get('redis_password'),
            decode_responses=True
        )

    def test_redis_connection(self):
        """Tests the Redis connection by setting and then getting a value."""
        test_key = "test_connection_key"
        test_value = "hello_redis"
        try:
            # Use the connection pool to get a Redis connection

            # Set a value in Redis
            self.r.set(test_key, test_value)
            # Retrieve the value from Redis
            retrieved_value = self.r.get(test_key)

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
            cached_data = self.r.get(cache_key)
            if cached_data:
                return eval(cached_data).get('count')
            return 1

        except Exception as err:
            print(f'Error get data from redis {err}')
            return 1


class DataProcess:
    """
    Processes data for creating and uploading emission and count diagrams to AWS S3.
    """

    def __init__(self, data: dict, emission_values: tuple, access_key:str, secret_key:str, region ='eu-central-1'):
        """
        Initialize DataProcess with data, emission values, and AWS credentials.

        :param data: Data to process.
        :param emission_values: Emission values associated with each object type.
        :param access_key: AWS access key.
        :param secret_key: AWS secret access key.
        :param region: AWS region.
        """

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
                                     region_name=region
                                     )
        self.s3 = self.session.client('s3')

    def emission_diagram(self):
        """
        Create and upload an emission diagram to AWS S3.
        """
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
                self.s3.upload_file(tmpfile.name, 'daniel-govnir-public', "diagram0.png")

            except NoCredentialsError as err:
                print(f'Upload Error: {err}')
            else:
                print('Saved to s3')


    def count_diagram(self):
        """
        Create and upload an emission diagram to AWS S3.
        """

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
                self.s3.upload_file(tmpfile.name, 'daniel-govnir-public', "diagram1.png")

            except NoCredentialsError as err:
                print(f'Upload Error: {err}')
            else:
                print('Saved to s3')

# upload configuration
configuration = upload_configuration()

# initialize redis client
redis_client = RedisClient()
