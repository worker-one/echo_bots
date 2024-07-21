# Use an official Python runtime as a parent image
FROM python:3.9-slim
MAINTAINER Konstantin Verner <konst.verner@gmail.com>

# Set the working directory in the container to /app
WORKDIR /app

# Copy the pyproject.toml and the README.md into the container at /app
COPY pyproject.toml README.md /app/

# Copy the .env file into the container
COPY .env /app/

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install optional dependencies if needed
RUN pip install --no-cache-dir .

# Copy the rest of the application code into the container
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application when the container launches
CMD ["python", "src/telegram_bot/main.py"]
