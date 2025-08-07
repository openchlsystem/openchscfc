# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project (ensure this includes manage.py)
COPY . .

# Verify Django installation
RUN python -c "import django; print(django.__version__)"

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# Wait for database if needed\n\
if [ -n "$DB_HOST" ]; then\n\
    echo "Waiting for database..."\n\
    while ! nc -z $DB_HOST $DB_PORT; do\n\
      sleep 0.1\n\
    done\n\
    echo "Database available"\n\
fi\n\
\n\
# Run migrations\n\
python manage.py migrate --noinput\n\
\n\
# Collect static files\n\
python manage.py collectstatic --noinput\n\
\n\
exec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Expose the port
EXPOSE 8006

# Set entrypoint and default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8006", "cfcbe.wsgi"]