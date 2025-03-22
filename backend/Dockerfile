# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Run Flask app
CMD ["python", "app.py"]
