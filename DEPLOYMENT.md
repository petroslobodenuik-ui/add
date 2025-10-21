Deployment guide — Docker + docker-compose

Goal: run the FastAPI humanitarian app as an independent web application on server 10.10.0.12 using Docker and Portainer (exposed on host port 8080).

Prerequisites on the server 10.10.0.12:
- Docker installed (https://docs.docker.com/engine/install/)
- Docker Compose v2 (or use `docker compose` from Docker CLI)
- SSH access to server
- Portainer (optional, we include steps to install it)

Two recommended deployment flows:

A) Deploy via Portainer from Git (recommended for ease)
1. Install Portainer (if not already):
   ssh user@10.10.0.12
   docker volume create portainer_data
   docker run -d -p 9000:9000 -p 8080:8080 --name portainer --restart=always \
     -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

2. Open Portainer UI: http://10.10.0.12:9000 and set admin credentials.

3. Deploy stack from Git repository in Portainer UI:
   - Environments → Local
   - Stacks → Add stack → Deploy from a Git repository
   - Repository URL: https://github.com/petroslobodenuik-ui/project.git
   - Branch: main
   - Compose path: / (if `docker-compose.yml` in repo root)
   - In advanced options, you can enable Build (Portainer will run `docker compose build`)
   - Deploy the stack

4. Expose the app on port 8080: our `portainer-stack.yml` and `docker-compose.prod.yml` already map container 8080 -> host 8080. Ensure Portainer uses the stack file in the repo root or point to `portainer-stack.yml` as the compose file.

5. Check app: http://10.10.0.12:8080

A2) Build & run directly on the server (manual)
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

5. The app will be available on port 8080 of the server (http://10.10.0.12:8080). Optionally configure firewall to allow port 8080 or put a reverse proxy in front.

B) Build image locally, push to registry, pull on server (CI-friendly)
1. Build locally and push to registry (Docker Hub/GitHub Container Registry):
   docker build -t your-dockerhub-username/humanitarian-app:latest .
   docker push your-dockerhub-username/humanitarian-app:latest

2. On server, create a `docker-compose.yml` that references the image instead of building locally, then `docker compose pull` and `docker compose up -d`.

Reverse proxy (recommended for production):
- Use Nginx/Caddy/Traefik to serve the app on port 80/443 and manage TLS.
-- Example Nginx config to proxy to localhost:8080 (on server):

server {
    listen 80;
    server_name example.com; # update

    location / {
   proxy_pass http://127.0.0.1:8080;
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

Automatic CI/CD using GitHub Actions + GHCR + Portainer webhook
-------------------------------------------------------------
This repository includes a GitHub Actions workflow `.github/workflows/ci-deploy.yml` that will:

- Build the Docker image using buildx and push it to GitHub Container Registry (GHCR) as `ghcr.io/<owner>/humanitarian-app:latest`.
- After push, it calls a Portainer webhook URL (if you set it as a repo secret) to instruct Portainer to pull the new image and redeploy the stack.

Required setup steps in your GitHub repository settings:

1. Create a Personal Access Token (PAT) with `write:packages` (or `packages:write`) scope. Store it in the repository secrets as `GHCR_PAT`.

2. Create a Portainer webhook to update the stack:
   - In Portainer UI → Stacks → choose your stack → Scroll to "Webhooks" or use the stack actions to create an endpoint.
   - Create a webhook that will trigger a "Redeploy stack" action. Copy the full webhook URL.
   - Add the webhook URL as a GitHub repository secret named `PORTAINER_WEBHOOK_URL`.

3. Optional: if your Portainer uses authentication or runs behind a proxy, ensure the webhook URL is reachable from GitHub Actions runners.

How the workflow works:

- On push to `main`, GitHub Actions builds and pushes the image to GHCR using `GHCR_PAT`.
- The workflow then POSTs the `PORTAINER_WEBHOOK_URL` so Portainer will pull the new image and restart the stack.

Portainer stack configuration note:
- Use `portainer-stack.yml` or `docker-compose.prod.yml` which now reference the GHCR image `ghcr.io/petroslobodenuik-ui/humanitarian-app:latest`.
- In Portainer, create/update the stack to use the `ghcr.io/.../humanitarian-app:latest` image and **disable** the build-from-Git option to avoid remote build errors.

If webhook redeploy does not update the stack, another approach is to use a small runner on the server that pulls the image and restarts the stack via `docker compose pull && docker compose up -d` — I can provide a systemd unit and small script for that if you'd prefer.
