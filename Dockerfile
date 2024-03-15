# Use the official Python base image from Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /skgpizza

# Copy the Python script and requirements file into the container
# Copy the entire skgpizza directory
COPY . /skgpizza

# Install required dependencies
RUN pip install --no-cache-dir -r /skgpizza/requirements.txt

# Install a web server
#RUN apt-get update
#RUN apt-get install mini-httpd -y

# Expose the post for the web server
#EXPOSE 80
# Expose the port for Flask
EXPOSE 8080

# Run Flask application
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
