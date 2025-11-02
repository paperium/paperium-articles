# Dockerfile
# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app

# Expose the port Uvicorn will listen on
EXPOSE 7860

# Define the command to run the application using Uvicorn
# Uvicorn MUST bind to 0.0.0.0 and port 7860, as required by Hugging Face Spaces.

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
