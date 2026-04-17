# Sales CRM

Sales CRM is a Dockerized SaaS-style CRM built with Django, Django REST Framework, React, PostgreSQL, Redis, and Django Channels.

It includes:
- JWT authentication
- Admin/team role system
- Bid tracking with KPI dashboards
- Admin reporting with PDF export
- Real-time internal chat with mentions
- Shared Lead Status Report
- Django admin for backend configuration

## Stack

- Backend: Django + DRF + SimpleJWT + Channels
- Frontend: React + Vite
- Database: PostgreSQL
- Realtime: Redis + WebSockets
- Containers: Docker + Docker Compose

## Project Structure

```text
backend/
  bids/
  chat/
  leads/
  users/
  config/
frontend/
docker-compose.yml
.env.example
```

## Local Run

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up -d --build
```

3. Create the first admin user:

```bash
docker compose exec backend python manage.py createsuperuser
```

4. Open:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Django admin: `http://localhost:8000/admin`

## Demo Data

Seed the main demo data:

```bash
docker compose exec backend python manage.py seed_data
```

Seed Lead Status Report rows:

```bash
docker compose exec backend python manage.py seed_lead_status_data
```

Clean all dummy data safely:

```bash
docker compose exec backend python manage.py clean_demo_data
```

## Step-by-Step Server Deployment Guide

This guide assumes:
- Ubuntu server
- Docker installed
- Docker Compose plugin installed
- You want to deploy directly from GitHub using Docker

### 1. Connect to the server

From your local machine:

```bash
ssh your-user@your-server-ip
```

### 2. Install Docker and Docker Compose

If Docker is not installed yet:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and log in again after adding your user to the Docker group.

### 3. Clone the project from GitHub

Choose a directory:

```bash
cd /opt
sudo mkdir -p sales-crm
sudo chown $USER:$USER sales-crm
cd sales-crm
git clone https://github.com/mdraihanreza/sales-crm.git .
```

### 4. Create the production environment file

Copy the example:

```bash
cp .env.example .env
```

Edit it:

```bash
nano .env
```

Use production-safe values like:

```env
POSTGRES_DB=sales_crm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-this-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=change-this-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_TIME_ZONE=Asia/Kolkata
JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=1
CORS_ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com

VITE_API_BASE_URL=https://your-domain.com/api
REDIS_URL=redis://redis:6379/0
```

Minimum production changes:
- `DJANGO_DEBUG=False`
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- set a strong `DJANGO_SECRET_KEY`
- set a strong `POSTGRES_PASSWORD`
- set correct `DJANGO_ALLOWED_HOSTS`
- set correct `CORS_ALLOWED_ORIGINS`
- set correct `VITE_API_BASE_URL`

### 5. Build and run the containers

```bash
docker compose up -d --build
```

This will:
- build backend and frontend images
- start PostgreSQL
- start Redis
- run Django migrations automatically
- collect Django static files automatically
- start Django with Daphne on port `8000`
- start the React frontend on port `5173`

### 6. Check container status

```bash
docker compose ps
```

Check logs if needed:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 7. Create the admin user

```bash
docker compose exec backend python manage.py createsuperuser
```

### 8. Optional: seed demo data

```bash
docker compose exec backend python manage.py seed_data
docker compose exec backend python manage.py seed_lead_status_data
```

### 9. Open the application

If you are accessing the server directly by IP:

- Frontend: `http://your-server-ip:5173`
- Backend: `http://your-server-ip:8000`
- Admin: `http://your-server-ip:8000/admin`

### 10. Updating the server after new GitHub changes

When you push new code to GitHub:

```bash
cd /opt/sales-crm
git pull origin main
docker compose up -d --build
```

### 11. Restarting the app

```bash
docker compose restart
```

Or restart only one service:

```bash
docker compose restart backend
docker compose restart frontend
```

### 12. Stopping the app

```bash
docker compose down
```

To stop and remove volumes too:

```bash
docker compose down -v
```

Be careful: `-v` removes PostgreSQL data.

## Important Production Note

With the current repository:
- the backend is production-capable with `config.settings.prod`
- the frontend container currently runs the Vite server

For a stronger production setup, add a reverse proxy such as Nginx and SSL via Cloudflare or Let's Encrypt. That is the recommended next step if you want a public domain deployment.

## Fastest Real-World Server Flow

If you want the shortest deployment path:

1. Create an Ubuntu VPS
2. Install Docker
3. Clone this repo
4. Configure `.env`
5. Run `docker compose up -d --build`
6. Create admin user
7. Open ports `5173` and `8000` in the server firewall

## Useful Commands

Rebuild only backend:

```bash
docker compose up -d --build backend
```

Rebuild only frontend:

```bash
docker compose up -d --build frontend
```

Run Django shell:

```bash
docker compose exec backend python manage.py shell
```

Run migrations manually:

```bash
docker compose exec backend python manage.py migrate
```
