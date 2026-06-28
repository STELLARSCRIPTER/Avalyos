# AVALYOS Deployment Guide

## 🚀 Deployment Strategies

This guide covers deploying AVALYOS to production environments.

---

## Option 1: Local/Development Deployment

### Best For
- Testing and development
- Single-user applications
- Learning and exploration
- Small team demos

### Requirements
- Windows/macOS/Linux machine
- Python 3.13+
- 4GB RAM minimum
- 2GB disk space

### Steps

1. **Clone/Setup Project**
```powershell
cd c:\Users\USER\OneDrive\Desktop\aval_program
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Generate Database**
```powershell
python generate_database.py
```

3. **Run Application**
```powershell
# Terminal 1: Backend
uvicorn aval_backend:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
streamlit run app.py
```

4. **Access**
- Streamlit: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 2: Docker Containerization

### Best For
- Production deployments
- Multi-environment consistency
- Easy scaling
- Cloud platforms (AWS, Azure, GCP)

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Create non-root user
RUN useradd -m -u 1000 avalyos
USER avalyos

# Run both services
CMD ["sh", "-c", "uvicorn aval_backend:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port=8501 --server.headless=true"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: avalyos
      POSTGRES_PASSWORD: avalyos_password
      POSTGRES_DB: avalyos_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:6-alpine
    environment:
      MONGO_INITDB_ROOT_USERNAME: avalyos
      MONGO_INITDB_ROOT_PASSWORD: avalyos_password
      MONGO_INITDB_DATABASE: avalyos_db
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  avalyos:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://avalyos:avalyos_password@postgres:5432/avalyos_db
      MONGODB_URI: mongodb://avalyos:avalyos_password@mongodb:27017/avalyos_db
      AVAL_API_KEY: ${AVAL_API_KEY}
      AVAL_RATE_PER_MIN: 1000
    depends_on:
      - postgres
      - mongodb
    volumes:
      - ./companies.json:/app/companies.json

volumes:
  postgres_data:
  mongodb_data:
```

### Build & Run

```bash
# Build image
docker build -t avalyos:latest .

# Run container
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Option 3: Cloud Platform Deployment

### AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize**
```bash
eb init -p "python 3.13" avalyos
```

3. **Create environment**
```bash
eb create avalyos-prod --instance-type t3.medium
```

4. **Deploy**
```bash
eb deploy
```

5. **Monitor**
```bash
eb logs
eb status
```

### Azure App Service

1. **Create App Service**
```bash
az appservice plan create -n avalyos-plan -g avalyos-group --sku B2
az webapp create -n avalyos -g avalyos-group -p avalyos-plan --runtime "PYTHON|3.13"
```

2. **Configure**
```bash
# Set environment variables
az webapp config appsettings set -n avalyos -g avalyos-group \
  --settings DATABASE_URL="postgresql://..." MONGODB_URI="mongodb://..."
```

3. **Deploy**
```bash
az webapp deployment source config-zip -n avalyos -g avalyos-group --src package.zip
```

### Google Cloud Run

1. **Build image**
```bash
docker build -t gcr.io/PROJECT-ID/avalyos .
```

2. **Push to registry**
```bash
docker push gcr.io/PROJECT-ID/avalyos
```

3. **Deploy**
```bash
gcloud run deploy avalyos \
  --image gcr.io/PROJECT-ID/avalyos \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=...,MONGODB_URI=..."
```

---

## Option 4: Linux Server Deployment

### Setup Virtual Machine

1. **Create VM** (AWS EC2, DigitalOcean, Linode, etc.)
   - OS: Ubuntu 22.04 LTS
   - Size: t3.medium (2GB RAM, 2 vCPU) or larger
   - Storage: 20GB

2. **Initial Setup**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3.13 \
    python3-pip \
    postgresql \
    mongodb-org \
    nginx \
    git

# Create application user
sudo useradd -m -s /bin/bash avalyos
sudo su - avalyos
```

3. **Deploy Application**
```bash
# Clone repository
git clone <your-repo> avalyos
cd avalyos

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate database
python generate_database.py

# Setup databases
python setup_databases.py
```

4. **Configure Systemd Services**

Create `/etc/systemd/system/avalyos-backend.service`:
```ini
[Unit]
Description=AVALYOS FastAPI Backend
After=network.target

[Service]
User=avalyos
WorkingDirectory=/home/avalyos/avalyos
Environment="PATH=/home/avalyos/avalyos/.venv/bin"
ExecStart=/home/avalyos/avalyos/.venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000 \
    aval_backend:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/avalyos-frontend.service`:
```ini
[Unit]
Description=AVALYOS Streamlit Frontend
After=network.target

[Service]
User=avalyos
WorkingDirectory=/home/avalyos/avalyos
Environment="PATH=/home/avalyos/avalyos/.venv/bin"
ExecStart=/home/avalyos/avalyos/.venv/bin/streamlit run \
    app.py \
    --server.port=8501 \
    --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Enable Services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable avalyos-backend avalyos-frontend
sudo systemctl start avalyos-backend avalyos-frontend
sudo systemctl status avalyos-backend avalyos-frontend
```

6. **Configure Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/avalyos`:
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name avalyos.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name avalyos.example.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/avalyos.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/avalyos.example.com/privkey.pem;

    # API backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/avalyos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Option 5: Production Configuration

### Environment Variables

Create `.env.production`:
```bash
# Backend
AVAL_PORT=8000
AVAL_API_KEY=your_secure_random_key_here
AVAL_RATE_PER_MIN=1000
QSHARP_QUEUE_MAX=128

# Databases (production instances)
DATABASE_URL=postgresql://avalyos:secure_password@prod-db.example.com:5432/avalyos_db
MONGODB_URI=mongodb://avalyos:secure_password@prod-mongo.example.com:27017/avalyos_db

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false
```

### Security Checklist

- [ ] Change default API key: `openssl rand -hex 32`
- [ ] Use strong database passwords (20+ characters)
- [ ] Enable SSL/TLS (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Use environment variables (not hardcoded secrets)
- [ ] Enable CORS only for trusted origins
- [ ] Setup monitoring and logging
- [ ] Regular backups of PostgreSQL/MongoDB
- [ ] Keep dependencies updated: `pip list --outdated`

### Performance Tuning

**FastAPI/Uvicorn**:
```bash
# Use Gunicorn for production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile - \
    --bind 0.0.0.0:8000 \
    aval_backend:app
```

**Streamlit**:
```bash
# Headless mode for production
streamlit run app.py \
    --server.headless=true \
    --server.port=8501 \
    --logger.level=warning
```

**Database**:
- PostgreSQL: Enable connection pooling (PgBouncer)
- MongoDB: Enable compression, optimize queries
- JSON: Cache frequently accessed data

### Monitoring & Logging

**Application Monitoring**:
```bash
pip install prometheus-client
pip install sentry-sdk
```

**Log Aggregation**:
```bash
# Example: ELK Stack
# Or: Splunk, DataDog, CloudWatch
```

---

## Option 6: Kubernetes Deployment

### Helm Chart Structure

```
avalyos-helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
```

### Install

```bash
helm install avalyos ./avalyos-helm \
    --namespace avalyos \
    --create-namespace
```

---

## Post-Deployment Checklist

- [ ] Verify application startup in logs
- [ ] Test all API endpoints
- [ ] Test all Streamlit pages
- [ ] Database connections working
- [ ] Rate limiting functional
- [ ] SSL/TLS certificate valid
- [ ] Monitoring alerts configured
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Scaling Recommendations

### Horizontal Scaling

For multiple users/high load:

1. **Load Balancer** (Nginx, HAProxy, AWS ELB)
   - Route to multiple backend instances
   - Route to multiple frontend instances

2. **Database Replication**
   - PostgreSQL streaming replication
   - MongoDB replica sets
   - JSON caching layer (Redis)

3. **API Gateway** (Kong, AWS API Gateway)
   - Rate limiting at gateway level
   - Request/response transformation
   - Authentication/authorization

### Vertical Scaling

For increasing computational needs:

1. Upgrade VM size (more RAM, CPU)
2. Increase worker threads: `QSHARP_QUEUE_MAX=256`
3. Enable connection pooling
4. Optimize database indexes

---

## Maintenance Plan

### Daily
- Monitor application logs
- Check service status
- Verify database backups

### Weekly
- Review performance metrics
- Check for security updates
- Test disaster recovery

### Monthly
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review and optimize database queries
- Capacity planning review

### Quarterly
- Security audit
- Load testing
- Documentation review
- Disaster recovery drill

---

## Disaster Recovery

### Backup Strategy

```bash
# PostgreSQL
pg_dump -h localhost -U avalyos -d avalyos_db > backup.sql

# MongoDB
mongodump -u avalyos -p password -d avalyos_db -o backup/

# JSON data
cp companies.json companies.json.backup
```

### Recovery Procedure

```bash
# Restore PostgreSQL
psql -U avalyos -d avalyos_db < backup.sql

# Restore MongoDB
mongorestore --authenticationDatabase admin -u avalyos -p password --db avalyos_db backup/

# Restore JSON
cp companies.json.backup companies.json
```

---

## Troubleshooting Production Issues

### High CPU Usage
- Check Q# queue size
- Monitor concurrent requests
- Increase worker count

### High Memory Usage
- Check for memory leaks
- Optimize queries
- Clear caches periodically

### Database Connection Errors
- Verify connection string
- Check database service status
- Review connection pool settings
- Check firewall rules

### Slow Response Times
- Monitor database query performance
- Check network latency
- Profile application code
- Review load balancer configuration

---

## Support & Updates

### Version Management
```bash
# Tag releases
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
```

### Update Procedure
```bash
# 1. Backup
python -c "import shutil; shutil.copy('companies.json', 'backup.json')"

# 2. Update code
git pull

# 3. Update dependencies
pip install --upgrade -r requirements.txt

# 4. Test
python -m pytest tests/

# 5. Restart services
systemctl restart avalyos-backend avalyos-frontend
```

---

**Production Deployment Status**: ✅ Ready  
**Recommended**: Use Option 2 (Docker) or Option 4 (Linux Server) for production  
**Support**: Check TROUBLESHOOTING.md for common issues
