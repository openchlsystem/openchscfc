#!/bin/sh

# Exit on error
set -e

# Run migrations
python manage.py migrate --noinput

# Collect static (if needed)
python manage.py collectstatic --noinput

# Execute main container command
exec "$@"