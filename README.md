# Object Detection Data Processor

This project automates the process of fetching object detection data from Redis, calculating emissions based on detected objects, generating visual reports (diagrams), and uploading these reports to AWS S3.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.11 or above installed on your system.
- Docker installed on your system (if you plan to containerize the application).
- An AWS account and an S3 bucket for storing the diagrams.
- A Redis server instance for fetching object detection data.

## Installation

Clone this repository to your local machine:

```bash
git clone https://yourrepositorylink.com/project.git
cd project
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. **AWS Credentials**: Set up your AWS credentials (`aws_access` and `aws_secret`) in the `settings.json` file to enable uploading to S3.
2. **Redis Configuration**: Specify your Redis instance's endpoint, port, and password in the `settings.json` file.
3. **S3 Bucket Name**: Ensure the `bucket_name` in the `settings.json` file is set to your AWS S3 bucket name where the diagrams will be uploaded.

## Usage

To run the application, execute the following command:

```bash
python application.py
```

The application is scheduled to fetch data from Redis, process it, generate emission and count diagrams, and upload these diagrams to the specified S3 bucket every 10 minutes.

## Dockerization

To containerize the application, you can use the provided Dockerfile. Build the Docker image with the following command:

```bash
docker build -t object-detection-data-processor .
```

Run the container:

```bash
docker run -d -p 80:80 -p 18975:18975 object-detection-data-processor
```

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

