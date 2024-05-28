# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Specify the command to run your chatbot (replace with your actual script name)
CMD ["python", "main.py"]
