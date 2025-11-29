# Using a lightweight official Python image
FROM python:3.12-slim

# Setting the working directory inside the container
WORKDIR /app

# Install all system dependencies needed for SQLite and pip
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copying the project files into container
COPY . /app

# Installing Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 (Flask default)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
