from controls import get_data_from_redis, DataProcess, data

def run():
    # set up data processing
    emissions = (0.1386, 0.9240, 2.68, 8.0400, 0,0,0,0)
    detected_objects = ('car', 'motorbike', 'bus', 'truck', 'person', 'dog', 'bicycle', 'cat')

    redis_data = get_data_from_redis(detected_objects)

    data_process = DataProcess(redis_data, emissions, data.get('aws_access'), data.get('aws_secret'))
    # create diagrams
    data_process.emission_diagram()
    data_process.count_diagram()


if __name__ == '__main__':
    run()