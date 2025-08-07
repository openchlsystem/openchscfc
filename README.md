# 📄 DevOps Deployment Guide: Django + Nginx + Docker

This detailed guide is intended for DevOps engineers responsible for deploying and maintaining a Django-based web application behind Nginx using Docker and Docker Compose. It includes configuration best practices, directory structure recommendations, environment management, and diagnostics.

---

## 📦 System Overview

We are deploying a web stack with the following components:

* **Django Backend** with Gunicorn as WSGI server
* **Nginx** as a reverse proxy and static files server
* **Docker Compose** for orchestration
* **.env** for configuration
* Optional: **Host-level Nginx** to proxy external traffic to Docker services

---

## 🛠 Prerequisites

Ensure the following are installed on the deployment environment:

* Docker v20.10+
* Docker Compose v2.0+
* Git
* Optional: Nginx on host (for production reverse proxying)

---

## 🗂 Recommended Directory Layout

```bash
project-root/
├── backend/                  # Django project (formerly cfcbe/)
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
├── frontend/                # Optional frontend project
│   └── dist/
├── deploy/                  # Deployment artifacts
│   ├── docker-compose.yaml
│   ├── .env
│   ├── nginx.conf
│   └── entrypoint.sh
├── staticfiles/             # Django-collected static files
├── ssl_certs/               # TLS certs if using HTTPS
├── README.md
└── .dockerignore
```

---

## ⚙️ Environment Variables (`.env`)

Example `.env`:

```env
HOST_FRONTEND_PORT=8080
HOST_API_PORT=8006
NGINX_FRONTEND_PORT=80
NGINX_API_PORT=8000
BACKEND_CONTAINER_PORT=8006
BACKEND_HOST_PORT=8007
DEBUG=0
```

---


## 🐳 Dockerfile (`backend/Dockerfile`)

```# Use official Python image
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
```
## ⚙️ Docker Compose File (`deploy/docker-compose.yaml`)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "${HOST_FRONTEND_PORT:-8080}:${NGINX_FRONTEND_PORT:-80}"
      - "${HOST_API_PORT:-8006}:${NGINX_API_PORT:-8000}"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/app/staticfiles
    environment:
      - NGINX_FRONTEND_PORT=${NGINX_FRONTEND_PORT:-80}
      - NGINX_API_PORT=${NGINX_API_PORT:-8000}
      - BACKEND_SERVICE=backend
      - BACKEND_PORT=${BACKEND_CONTAINER_PORT:-8006}
    networks:
      - app_network
    restart: unless-stopped

  backend:
    build:
      context: ./cfcbe
      args:
        - PORT=${BACKEND_CONTAINER_PORT:-8006}
    ports:
      - "${BACKEND_HOST_PORT:-8006}:${BACKEND_CONTAINER_PORT:-8006}"
    environment:
      - PORT=${BACKEND_CONTAINER_PORT:-8006}
      - DJANGO_SETTINGS_MODULE=cfcbe.settings
      - DEBUG=${DEBUG:-0}
    command: >
      sh -c "gunicorn --bind 0.0.0.0:${BACKEND_CONTAINER_PORT:-8006} cfcbe.wsgi"
    networks:
      - app_network
    restart: unless-stopped

networks:
  app_network:
    driver: bridge
    name: openchscfc_app_network
```

---

## 🌐 Nginx Config for Docker (`deploy/nginx.conf`)

```worker_processes  1;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # Logging
    access_log  /var/log/nginx/access.log;
    error_log   /var/log/nginx/error.log warn;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream backend {
        server backend:8006;
    }

    server {
        listen 80;

        location /static/ {
            alias /app/staticfiles/;
        }

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}

```

---

## 🖥️ Host Nginx (Optional, for Production Edge Proxying)

Use this config when Nginx on the host proxies requests to Docker services:

```nginx
http {
    upstream docker_frontend {
        server 127.0.0.1:8080;
    }

    upstream docker_backend {
        server 127.0.0.1:8007;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://docker_frontend;
            proxy_set_header Host $host;
        }

        location /api/ {
            proxy_pass http://docker_backend;
            proxy_set_header Host $host;
        }
    }
}
```

Reload with:

```bash
sudo nginx -s reload
```

---

## 🚀 Deployment Commands

```bash
# Build and start containers
cd deploy
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Test an endpoint
curl -i http://localhost/api/webhook/eemis/
```

---

## 🧹 Collect Static Files (Run Once)

```bash
docker-compose exec backend python manage.py collectstatic
```

Make sure `staticfiles/` exists and is mounted into Nginx.

---

## 🧾 .dockerignore Example

```dockerfile
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.db
*.sqlite3
openchs/
ssl_certs/
staticfiles/
```

---

## ✅ DevOps Checklist

| Item                              | Status |
| --------------------------------- | ------ |
| Docker containers build and start | ✅      |
| Backend routes available          | ✅      |
| Nginx routes static and dynamic   | ✅      |
| Static files collected and served | ✅      |
| Host Nginx configured (if needed) | ✅      |

---

## 🆘 Troubleshooting

* Check backend logs: `docker-compose logs backend`
* Check Nginx logs: `docker-compose logs nginx`
* Confirm routes in Django `urls.py`
* Verify exposed ports match host config

---

> Last reviewed: July 2025
