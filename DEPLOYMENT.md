# Deployment Guide

This guide covers multiple deployment options for your Research Paper Summarizer application.

## Architecture Overview

- **Frontend**: React app (in `capstone-ui/`)
- **Backend**: FastAPI (in `backend/`)
- **Database**: SQLite (can be migrated to PostgreSQL for production)

---

## Option 1: Vercel (Frontend) + Railway/Render (Backend) - Recommended

### Frontend Deployment (Vercel)

1. **Build the React app:**
   ```bash
   cd capstone-ui
   npm run build
   ```

2. **Deploy to Vercel:**
   - Install Vercel CLI: `npm i -g vercel`
   - Run `vercel` in the `capstone-ui` directory
   - Or use Vercel's GitHub integration

3. **Set Environment Variable:**
   - In Vercel dashboard, add: `REACT_APP_API_BASE_URL=https://your-backend-url.com`

### Backend Deployment (Railway)

1. **Create `Procfile` in `capstone_project/` directory:**
   ```
   web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create `runtime.txt` in `capstone_project/`:**
   ```
   python-3.11
   ```

3. **Update CORS in `backend/main.py`:**
   ```python
   allow_origins=["https://your-frontend-url.vercel.app"]
   ```

4. **Deploy to Railway:**
   - Connect your GitHub repo
   - Railway will auto-detect Python
   - Set environment variables (API keys, etc.)

### Backend Deployment (Render) - Alternative

1. **Create `render.yaml` in `capstone_project/`:**
   ```yaml
   services:
     - type: web
       name: capstone-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
   ```

2. **Deploy to Render:**
   - Connect GitHub repo
   - Create new Web Service
   - Render will use the `render.yaml` config

---

## Option 2: Docker Deployment

### Create Dockerfile for Backend

Create `capstone_project/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create Dockerfile for Frontend

Create `capstone_project/capstone-ui/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Create nginx.conf for Frontend

Create `capstone_project/capstone-ui/nginx.conf`:
```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Create docker-compose.yml

Create `capstone_project/docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./app.db:/app/app.db
      - ./uploads:/app/uploads

  frontend:
    build:
      context: ./capstone-ui
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Or deploy to cloud (AWS ECS, Google Cloud Run, Azure Container Instances)
```

---

## Option 3: Traditional VPS (DigitalOcean, Linode, etc.)

### Server Setup

1. **SSH into your server**

2. **Install dependencies:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip -y

   # Install Node.js 18
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs

   # Install Nginx
   sudo apt install nginx -y
   ```

3. **Clone your repository:**
   ```bash
   git clone <your-repo-url>
   cd capstone_project
   ```

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create systemd service** (`/etc/systemd/system/capstone-backend.service`):
   ```ini
   [Unit]
   Description=Capstone Backend API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/capstone_project
   Environment="PATH=/path/to/capstone_project/venv/bin"
   ExecStart=/path/to/capstone_project/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable capstone-backend
   sudo systemctl start capstone-backend
   ```

### Frontend Setup

1. **Build the React app:**
   ```bash
   cd capstone-ui
   npm install
   REACT_APP_API_BASE_URL=http://your-server-ip:8000 npm run build
   ```

2. **Configure Nginx** (`/etc/nginx/sites-available/capstone`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       # Frontend
       location / {
           root /path/to/capstone_project/capstone-ui/build;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/capstone /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Environment Variables

### Backend (.env file)
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend
```env
REACT_APP_API_BASE_URL=https://your-backend-url.com
```

---

## Database Migration (Optional - for Production)

For production, consider migrating from SQLite to PostgreSQL:

1. **Update `backend/database.py`:**
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
   ```

2. **Install PostgreSQL adapter:**
   ```bash
   pip install psycopg2-binary
   ```

3. **Update requirements.txt:**
   ```
   psycopg2-binary==2.9.9
   ```

---

## Security Checklist

- [ ] Update CORS to only allow your frontend domain
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (use Let's Encrypt for free SSL)
- [ ] Set up proper database backups
- [ ] Configure rate limiting on API endpoints
- [ ] Use a production WSGI server (Gunicorn with Uvicorn workers)
- [ ] Set up monitoring and logging

---

## Quick Deploy Commands

### Railway (Backend)
```bash
railway login
railway init
railway up
```

### Vercel (Frontend)
```bash
cd capstone-ui
vercel
```

### Docker
```bash
docker-compose up -d
```

---

## Troubleshooting

1. **CORS errors**: Update `allow_origins` in `backend/main.py`
2. **API not found**: Check `REACT_APP_API_BASE_URL` environment variable
3. **Database errors**: Ensure database file has proper permissions
4. **Build failures**: Check Node.js and Python versions match requirements

---

## Recommended Production Setup

**Best for beginners**: Vercel (frontend) + Railway (backend)
**Best for scalability**: Docker on AWS/GCP/Azure
**Best for cost**: VPS with Nginx

