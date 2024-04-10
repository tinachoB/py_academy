# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libssl-dev \
    libffi-dev

# Install Python dependencies
COPY requirements/ /app/
RUN pip install --no-cache-dir \
    -r dev.txt \
    -r test.txt \
    -r prod.txt


# Copy the local codebase into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
RUN pip install .
CMD ["code_generator", "run-service"]
