
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the current directory contents into the container at /usr/src/app
COPY . .

EXPOSE 80 18975

# Run app.py when the container launches
# (Modify this with your main script file if different)
CMD ["python", "./application.py"]