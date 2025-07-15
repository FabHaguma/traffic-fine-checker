# Stage 1: Use a modern, supported Python image as a parent image
# Switched from 'buster' (EOL) to 'bullseye'
FROM python:3.9-slim-bullseye AS base

# Set the working directory in the container
WORKDIR /app

# Prevent python from writing pyc files to disc and buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the requirements file into the container
COPY requirements.txt .

# Install the python dependencies
# The 'gcc' installation step was removed as it's not needed for these packages.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the application when the container starts.
CMD ["python", "main.py"]