# Deployment Guide

## Overview
The Unified GenAI Platform is designed to be deployed using Docker containers. We provide a `docker-compose.yml` configuration suitable for both development and staging/production environments.

## Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.0+
- Git

## Production Setup

### 1. Environment Configuration
Create a production `.env` file. Ensure `DEBUG=False` and set strong secrets.

```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

Key variables to secure:
- `JWT_SECRET`: Use a long random string (`openssl rand -hex 32`)
- `STRIPE_SECRET_KEY`: Use live keys
- `POSTGRES_PASSWORD`: Strong password
- `ALLOWED_ORIGINS`: Set to your actual domain (e.g., `https://app.yourdomain.com`)

### 2. Build and Run
Use the production settings (if we had separate compose files, or just `docker-compose.yml` with overrides).
For now, we use the standard compose file.

```bash
docker compose --env-file .env.prod up -d --build
```

### 3. Verification
Check service health:
```bash
docker compose ps
# Ensure all services (api, frontend, redis, qdrant, postgres) are "Up"
```

Verify API health:
```bash
curl http://localhost:8000/health
```

## Scaling
- **API**: Stateless, can be scaled: `docker compose up -d --scale api=3`
- **Worker**: If using celery/background tasks, scale similarly.

## Troubleshooting
View logs:
```bash
docker compose logs -f api
```

Restart specific service:
```bash
docker compose restart api
```
