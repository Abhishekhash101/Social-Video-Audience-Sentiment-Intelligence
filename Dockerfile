# 1. Use an official Python runtime as a parent image
FROM python:3.9-slim

# 2. Set the working directory in the container
WORKDIR /app

# --- NEW STEP: Install System Dependencies ---
# LightGBM needs 'libgomp1' to run. We install it here.
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# ---------------------------------------------

# 3. Copy the current directory contents into the container at /app
COPY . /app

# 4. Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Make port 5000 available to the world outside this container
EXPOSE 5000

# 6. Define environment variable
ENV FLASK_APP=app.py

# 7. Run app.py when the container launches
CMD ["python", "app.py"]