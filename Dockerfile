FROM python:3.10.3-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && cat apt_requirements.txt | xargs apt -y --no-install-recommends install libmagic-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove \
    && apt autoclean

# Install Python dependencies
RUN pip install --upgrade pip gunicorn
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app/

# Create static and media directories if they don't exist
RUN mkdir -p /usr/src/app/static
RUN mkdir -p /usr/src/app/media

# Set appropriate permissions
RUN chmod +x /usr/src/app/entrypoint.sh
RUN chmod -R 755 /usr/src/app/static /usr/src/app/media

EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]