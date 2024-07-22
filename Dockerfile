# Use Python 3.11 as the base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libpq-dev \
    cron \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app/

# Copy the .env file
COPY .env /app/.env

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ChromeDriver update script
COPY update_chromedriver.py /usr/local/bin/update_chromedriver.py

# Set up cron job
RUN echo "0 * * * * /usr/local/bin/python /usr/local/bin/update_chromedriver.py >> /var/log/cron.log 2>&1" > /etc/cron.d/update-chromedriver
RUN chmod 0644 /etc/cron.d/update-chromedriver
RUN crontab /etc/cron.d/update-chromedriver

# Run the initial ChromeDriver update
RUN python /usr/local/bin/update_chromedriver.py

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create a startup script
RUN echo "#!/bin/bash\n\
    cron\n\
    export \$(cat /app/.env | xargs)\n\
    gunicorn --workers 3 --bind 0.0.0.0:8000 daospace.wsgi:application" > /start.sh && \
    chmod +x /start.sh

# Run the startup script
CMD ["/start.sh"]