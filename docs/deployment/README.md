# 🚀 Deployment Guide

This guide covers deploying the LY-Merch platform to production environments.

## 🏗️ Deployment Options

### 1. Docker Compose (Recommended)
Best for single-server deployments, development staging, and small-scale production.

### 2. Kubernetes
Best for large-scale production, high availability, and complex orchestration needs.

### 3. Manual Deployment
Best for custom environments or when Docker is not available.

## 🐳 Docker Compose Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Server with minimum 2GB RAM, 20GB storage
- Domain name (optional but recommended)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Deploy Application
```bash
# Clone repository
git clone <repository-url>
cd ly-merch

# Create production environment file
cp .env.example .env
```

Edit `.env` with production values:
```bash
# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password_here
MYSQL_PASSWORD=your_secure_user_password_here
MYSQL_USER=myapp
MYSQL_DATABASE=myapp

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Frontend Configuration
REACT_APP_API_URL=https://your-domain.com/api
```

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### Step 3: Initialize Data
```bash
# Wait for database to be ready
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"

# Import initial data
cd scripts
./import_data.sh

# Verify data import
docker-compose exec db mysql -u myapp -p myapp -e "SELECT COUNT(*) FROM products;"
```

### Step 4: SSL Configuration (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Update nginx configuration
sudo nano /etc/nginx/sites-available/ly-merch
```

nginx configuration for SSL:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Enable automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3.0+ (optional but recommended)

### Step 1: Create Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ly-merch
```

```bash
kubectl apply -f namespace.yaml
```

### Step 2: Database Deployment
```yaml
# mysql-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: ly-merch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        - name: MYSQL_DATABASE
          value: "myapp"
        - name: MYSQL_USER
          value: "myapp"
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: user-password
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: ly-merch
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

### Step 3: API Deployment
```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ly-merch
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/ly-merch-api:latest
        env:
        - name: MYSQL_HOST
          value: "mysql"
        - name: MYSQL_USER
          value: "myapp"
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: user-password
        - name: MYSQL_DATABASE
          value: "myapp"
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: ly-merch
spec:
  selector:
    app: api
  ports:
  - port: 8000
    targetPort: 8000
```

### Step 4: Frontend Deployment
```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ly-merch
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/ly-merch-frontend:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: ly-merch
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
```

### Step 5: Ingress Configuration
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ly-merch-ingress
  namespace: ly-merch
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: ly-merch-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

```bash
# Deploy all resources
kubectl apply -f mysql-deployment.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n ly-merch
kubectl get services -n ly-merch
```

## 📊 Manual Deployment

### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- nginx

### Step 1: System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv nodejs npm mysql-server nginx git

# Install PM2 for process management
npm install -g pm2
```

### Step 2: Database Setup
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'myapp'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON myapp.* TO 'myapp'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Backend Deployment
```bash
# Clone and setup backend
git clone <repository-url> /opt/ly-merch
cd /opt/ly-merch/api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create environment file
cat > .env << EOF
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=myapp
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=myapp
EOF

# Create systemd service
sudo tee /etc/systemd/system/ly-merch-api.service > /dev/null << EOF
[Unit]
Description=LY-Merch API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/ly-merch/api
Environment=PATH=/opt/ly-merch/api/venv/bin
EnvironmentFile=/opt/ly-merch/api/.env
ExecStart=/opt/ly-merch/api/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start API service
sudo systemctl daemon-reload
sudo systemctl enable ly-merch-api
sudo systemctl start ly-merch-api
```

### Step 4: Frontend Deployment
```bash
cd /opt/ly-merch/frontend

# Install dependencies and build
npm install
npm run build

# Copy build files
sudo mkdir -p /var/www/ly-merch
sudo cp -r dist/* /var/www/ly-merch/
sudo chown -R www-data:www-data /var/www/ly-merch
```

### Step 5: nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/ly-merch > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/ly-merch;
    index index.html;

    # Frontend
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files optimization
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ly-merch /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Data Import
```bash
cd /opt/ly-merch/scripts

# Import initial data
python3 import_data.py

# Verify import
mysql -u myapp -p myapp -e "SELECT COUNT(*) FROM products;"
```

## 🔍 Monitoring & Maintenance

### Health Checks
```bash
# API health
curl http://your-domain.com/api/v1/health

# Database connection
curl http://your-domain.com/api/v1/stats

# Service status (systemd)
sudo systemctl status ly-merch-api
sudo systemctl status nginx
sudo systemctl status mysql

# Docker services
docker-compose ps
docker-compose logs --tail=50 api
```

### Log Management
```bash
# API logs (systemd)
sudo journalctl -u ly-merch-api -f

# nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker logs
docker-compose logs -f api
docker-compose logs -f db

# Log rotation
sudo logrotate /etc/logrotate.conf
```

### Backup Strategy
```bash
# Database backup
docker-compose exec db mysqldump -u myapp -p myapp > backup_$(date +%Y%m%d).sql

# Automated backup script
cat > backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Database backup
docker-compose exec -T db mysqldump -u myapp -pmyapp myapp > \$BACKUP_DIR/db_\$DATE.sql

# Compress old backups
find \$BACKUP_DIR -name "*.sql" -mtime +7 -exec gzip {} \;

# Remove backups older than 30 days
find \$BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Schedule backup
echo "0 2 * * * /opt/ly-merch/backup.sh" | sudo crontab -
```

### Performance Optimization
```bash
# Enable gzip compression
sudo tee -a /etc/nginx/nginx.conf > /dev/null << EOF
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/css application/javascript application/json image/svg+xml;
EOF

# Optimize MySQL
sudo tee -a /etc/mysql/mysql.conf.d/mysqld.cnf > /dev/null << EOF
[mysqld]
innodb_buffer_pool_size = 256M
max_connections = 50
query_cache_type = 1
query_cache_size = 64M
EOF

sudo systemctl restart mysql nginx
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check MySQL service
sudo systemctl status mysql

# Check connection
mysql -u myapp -p myapp -e "SELECT 1"

# Review logs
sudo journalctl -u mysql -n 50
```

#### API Not Responding
```bash
# Check API service
sudo systemctl status ly-merch-api

# Check logs
sudo journalctl -u ly-merch-api -f

# Test API directly
curl http://localhost:8000/health
```

#### Frontend Loading Issues
```bash
# Check nginx
sudo systemctl status nginx
sudo nginx -t

# Check file permissions
ls -la /var/www/ly-merch/

# Review nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart all services
sudo systemctl restart ly-merch-api nginx mysql

# Or with Docker
docker-compose restart
```

#### Database Recovery
```bash
# Restore from backup
mysql -u myapp -p myapp < backup_20240101.sql

# Or with Docker
docker-compose exec -T db mysql -u myapp -p myapp < backup_20240101.sql
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer (HAProxy, nginx, AWS ALB)
- Multiple API instances with shared database
- CDN for static assets (CloudFront, Cloudflare)

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer equivalent for MySQL)
- Database clustering (MySQL Group Replication)

### Monitoring
- Application monitoring (New Relic, DataDog)
- Infrastructure monitoring (Prometheus + Grafana)
- Log aggregation (ELK Stack, Fluentd)