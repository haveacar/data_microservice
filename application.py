from controls import get_data_from_redis, DataProcess, configuration
import schedule
import time

def run()-> None:
    """
    Retrieves data from Redis, processes it to compute emissions and object counts,
    and generates diagrams visualizing this data.
    :return: None
    """
    # Set up data processing with predefined emissions factors
    emissions = (0.1386, 0.9240, 2.68, 8.0400, 0,0,0,0)
    detected_objects = (
        'car',
        'motorbike',
        'bus',
        'truck',
        'person',
        'dog',
        'bicycle',
        'cat'
    )

    # Retrieve object count data from Redis
    redis_data = get_data_from_redis(detected_objects)

    # Initialize data processing with Redis data, emissions factors, and AWS credentials
    data_process = DataProcess(
        redis_data,
        emissions,
        configuration.get('aws_access'),
        configuration.get('aws_secret')
    )
    # Generate and display emission and count diagrams
    data_process.emission_diagram()
    data_process.count_diagram()


# Schedule the run function to be called every 10 minutes
schedule.every(10).minutes.do(run)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)