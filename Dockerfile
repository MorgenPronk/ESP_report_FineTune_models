# Use the official Python image with the desired version
# During development this is the version that was used: 3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)
FROM python:3.12.4-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY ./app

# Install dependencies from the requirments file
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run your script
CMD ["python", "your_script.py"]

