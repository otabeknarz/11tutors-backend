# Deployment Guide

## Overview

This guide covers deploying the 11Tutors Django backend to production environments.

---

## Pre-Deployment Checklist

### Security

- [ ] Set `DEBUG = False` in production
- [ ] Use strong `SECRET_KEY` (generate new one for production)
- [ ] Configure `ALLOWED_HOSTS` with production domains
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS_ALLOWED_ORIGINS for production frontend
- [ ] Set up CSRF_TRUSTED_ORIGINS
- [ ] Use environment variables for all secrets
- [ ] Enable Django security middleware
- [ ] Configure secure cookies (SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)

### Database

- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Run migrations on production database
- [ ] Set up database monitoring

### Static Files & Media

- [ ] Configure Cloudflare R2 or AWS S3
- [ ] Run `collectstatic` command
- [ ] Set up CDN for static files
- [ ] Configure proper CORS for media files

### Email

- [ ] Configure production email backend (SMTP)
- [ ] Set up email service (Gmail, SendGrid, Mailgun)
- [ ] Test email delivery

### Third-Party Services

- [ ] VdoCipher API credentials
- [ ] Stripe production keys
- [ ] Stripe webhook endpoint configured
- [ ] Cloudflare R2 / AWS S3 credentials

### Monitoring

- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring

---

## Environment Variables

### Production .env Template

```bash
# Django Core
DJANGO_SECRET_KEY=your-super-secret-production-key-min-50-chars
DJANGO_DEBUG=False
ALLOWED_HOSTS=api.11tutors.com,www.11tutors.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://11tutors.com,https://www.11tutors.com
CSRF_TRUSTED_ORIGINS=https://11tutors.com,https://www.11tutors.com

# Email
EMAIL_HOST_USER=noreply@11tutors.com
EMAIL_HOST_PASSWORD=your-email-password

# VdoCipher
VIDEO_SERVICE_SECRET_KEY=your-vdocipher-api-secret

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://11tutors.com

# Cloudflare R2 / AWS S3
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=11tutors-production
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
```

### Generating SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Production Settings

### settings.py Modifications

```python
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# HTTPS/SSL
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Database
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/static/"
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/media/"

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

---

## Deployment Options

### Option 1: Traditional VPS (DigitalOcean, Linode, AWS EC2)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx -y

# Install supervisor for process management
sudo apt install supervisor -y
```

#### 2. Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/11tutors
sudo chown $USER:$USER /var/www/11tutors
cd /var/www/11tutors

# Clone repository
git clone https://github.com/yourusername/11tutors-backend.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env  # Add production environment variables

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p logs
```

#### 3. Gunicorn Configuration

Create `/var/www/11tutors/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4  # (2 x CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
errorlog = "/var/www/11tutors/logs/gunicorn-error.log"
accesslog = "/var/www/11tutors/logs/gunicorn-access.log"
loglevel = "info"
```

#### 4. Supervisor Configuration

Create `/etc/supervisor/conf.d/11tutors.conf`:

```ini
[program:11tutors]
directory=/var/www/11tutors
command=/var/www/11tutors/venv/bin/gunicorn eleven_tutors.wsgi:application -c /var/www/11tutors/gunicorn_config.py
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/11tutors/logs/supervisor.log
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start 11tutors
sudo supervisorctl status
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/11tutors`:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.11tutors.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.11tutors.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.11tutors.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.11tutors.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/11tutors/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/11tutors /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d api.11tutors.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

#### 7. PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE tutors_db;
CREATE USER tutors_user WITH PASSWORD 'secure_password';
ALTER ROLE tutors_user SET client_encoding TO 'utf8';
ALTER ROLE tutors_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tutors_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tutors_db TO tutors_user;
\q
```

Update DATABASE_URL in .env:

```bash
DATABASE_URL=postgresql://tutors_user:secure_password@localhost:5432/tutors_db
```

---

### Option 2: Platform as a Service (Heroku, Railway, Render)

#### Heroku Deployment

1. **Install Heroku CLI**:

```bash
brew install heroku/brew/heroku  # macOS
```

2. **Create Heroku App**:

```bash
heroku create 11tutors-api
```

3. **Add Buildpack**:

```bash
heroku buildpacks:set heroku/python
```

4. **Create Procfile**:

```
web: gunicorn eleven_tutors.wsgi:application --log-file -
release: python manage.py migrate
```

5. **Create runtime.txt**:

```
python-3.11.0
```

6. **Configure Environment Variables**:

```bash
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set DJANGO_DEBUG=False
heroku config:set DATABASE_URL=postgresql://...
# ... set all other environment variables
```

7. **Add PostgreSQL**:

```bash
heroku addons:create heroku-postgresql:mini
```

8. **Deploy**:

```bash
git push heroku main
```

9. **Run Migrations**:

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

### Option 3: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "eleven_tutors.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

#### docker-compose.yml

```yaml
version: "3.8"

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: tutors_db
      POSTGRES_USER: tutors_user
      POSTGRES_PASSWORD: secure_password

  web:
    build: .
    command: gunicorn eleven_tutors.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/staticfiles
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

volumes:
  postgres_data:
```

#### Build and Run

```bash
# Build image
docker-compose build

# Run migrations
docker-compose run web python manage.py migrate

# Create superuser
docker-compose run web python manage.py createsuperuser

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web
```

---

## Database Migrations

### Running Migrations in Production

```bash
# Backup database first
pg_dump -U tutors_user -h localhost tutors_db > backup_$(date +%Y%m%d).sql

# Run migrations
python manage.py migrate

# If using Docker
docker-compose run web python manage.py migrate

# If using Heroku
heroku run python manage.py migrate
```

### Zero-Downtime Migrations

1. **Backward-compatible migrations**: New columns should be nullable
2. **Multi-step deployment**:
   - Step 1: Add new column (nullable)
   - Step 2: Populate data
   - Step 3: Make column non-nullable
   - Step 4: Remove old column

---

## Monitoring & Logging

### Sentry Integration

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment="production"
)
```

### Application Logs

```bash
# View logs
tail -f /var/www/11tutors/logs/django.log
tail -f /var/www/11tutors/logs/gunicorn-error.log

# Supervisor logs
sudo tail -f /var/www/11tutors/logs/supervisor.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U tutors_user tutors_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:

```bash
0 2 * * * /path/to/backup-script.sh
```

### Media Files Backup

Cloudflare R2 / S3 provides built-in versioning and backup options.

---

## Performance Optimization

### Database

1. **Connection Pooling**: Set `CONN_MAX_AGE = 600`
2. **Indexes**: Ensure all foreign keys and frequently queried fields are indexed
3. **Query Optimization**: Use `select_related` and `prefetch_related`

### Caching (Redis)

```bash
pip install redis django-redis
```

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache session data
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### CDN

Configure Cloudflare CDN for static files and media.

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Nginx or cloud load balancer
2. **Multiple Application Servers**: Run multiple Gunicorn instances
3. **Shared Database**: All servers connect to same PostgreSQL
4. **Shared Cache**: Redis for session and cache storage
5. **Shared Storage**: S3/R2 for media files

### Vertical Scaling

1. **Increase server resources**: CPU, RAM
2. **Optimize Gunicorn workers**: `workers = (2 x CPU) + 1`
3. **Database optimization**: Increase connection pool, add read replicas

---

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**:

   - Check if Gunicorn is running: `sudo supervisorctl status`
   - Check Gunicorn logs: `tail -f logs/gunicorn-error.log`

2. **Static files not loading**:

   - Run `python manage.py collectstatic`
   - Check Nginx configuration
   - Verify S3/R2 credentials

3. **Database connection errors**:

   - Verify DATABASE_URL
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Test connection: `psql $DATABASE_URL`

4. **CORS errors**:
   - Verify CORS_ALLOWED_ORIGINS includes frontend domain
   - Check CSRF_TRUSTED_ORIGINS

---

## Rollback Procedure

```bash
# 1. Stop application
sudo supervisorctl stop 11tutors

# 2. Restore database backup
psql -U tutors_user tutors_db < backup_20240101.sql

# 3. Checkout previous version
git checkout <previous-commit-hash>

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations (if needed)
python manage.py migrate

# 6. Restart application
sudo supervisorctl start 11tutors
```

---

## Security Checklist

- [ ] DEBUG = False
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Secure cookies configured
- [ ] CORS properly configured
- [ ] Database credentials secure
- [ ] API keys in environment variables
- [ ] Stripe webhook signature verification
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] SSH key-based authentication
- [ ] Regular backups
- [ ] Monitoring and alerting set up
