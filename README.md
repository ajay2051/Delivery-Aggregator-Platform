# This project process the delivery request and keeps the track of delivery.

# To Run the project


celery -A project worker  --loglevel=INFO

celery -A project worker flower