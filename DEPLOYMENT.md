Deployment guide — Docker + docker-compose

Goal: run the FastAPI humanitarian app as an independent web application on server 10.10.0.4 using Docker.

Prerequisites on the server 10.10.0.4:
- Docker installed (https://docs.docker.com/engine/install/)
- Docker Compose v2 (or use `docker compose` from Docker CLI)
- SSH access to server

Two recommended deployment flows:

A) Build & run directly on the server (simpler)
1. Copy project to server (use scp/rsync or git clone):
   scp -r C:\Users\admin5\Desktop\base user@10.10.0.4:/home/user/project
   # or on server:
   git clone https://github.com/petroslobodenuik-ui/project.git

2. SSH into server and go to project folder:
   ssh user@10.10.0.4
   cd /home/user/project

3. Build and start containers:
   docker compose build --pull
   docker compose up -d

4. Check logs and status:
   docker compose ps
   docker compose logs -f app

5. The app will be available on port 8000 of the server (http://10.10.0.4:8000). Optionally configure firewall to allow port 8000 or put a reverse proxy in front.

B) Build image locally, push to registry, pull on server (CI-friendly)
1. Build locally and push to registry (Docker Hub/GitHub Container Registry):
   docker build -t your-dockerhub-username/humanitarian-app:latest .
   docker push your-dockerhub-username/humanitarian-app:latest

2. On server, create a `docker-compose.yml` that references the image instead of building locally, then `docker compose pull` and `docker compose up -d`.

Reverse proxy (recommended for production):
- Use Nginx/Caddy/Traefik to serve the app on port 80/443 and manage TLS.
- Example Nginx config to proxy to localhost:8000 (on server):

server {
    listen 80;
    server_name example.com; # update

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Notes:
- If using volumes and mounting the code, ensure the container user has permissions. The Dockerfile sets the container to run as user `app`.
- For a production workload consider using a process manager, proper logging, monitoring, and secrets management.

If хочете, можу:
- додати `Caddyfile` або `nginx` config, 
- створити GitHub Actions workflow, що будує і пушить образ у DockerHub/GHCR,
- або одразу виконати тестовий build локально і запустити `docker compose up` тут (повідомте, якщо це робити).
