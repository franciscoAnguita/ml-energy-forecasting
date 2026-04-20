# 🚢 DEPLOYMENT GUIDE
## Deploying the Energy Forecasting API to Production

---

## 📋 Overview

This guide covers deploying your ML API to production environments. Choose the deployment method that fits your needs:

1. **Docker** (Recommended) - Containerized deployment
2. **Cloud Platforms** - Heroku, AWS, Google Cloud, Azure
3. **Virtual Private Server (VPS)** - DigitalOcean, Linode, etc.

---

## 🐳 METHOD 1: Docker Deployment

### **Why Docker?**
- ✅ Consistent environment across dev/prod
- ✅ Easy to scale
- ✅ Works on any platform
- ✅ Industry standard

---

### **Step 1: Create Dockerfile**

Already included in your project as `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Start the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### **Step 2: Build Docker Image**

```bash
# Build the image
docker build -t energy-forecasting-api .

# Verify image was created
docker images | grep energy-forecasting
```

---

### **Step 3: Run Container Locally (Test)**

```bash
# Run the container
docker run -d -p 8000:8000 --name energy-api energy-forecasting-api

# Check if it's running
docker ps

# Test the API
curl http://localhost:8000/

# View logs
docker logs energy-api

# Stop container
docker stop energy-api

# Remove container
docker rm energy-api
```

---

### **Step 4: Push to Docker Hub (Optional)**

```bash
# Login to Docker Hub
docker login

# Tag your image
docker tag energy-forecasting-api yourusername/energy-forecasting-api:v1.0

# Push to Docker Hub
docker push yourusername/energy-forecasting-api:v1.0
```

Now anyone can pull and run your API:
```bash
docker pull yourusername/energy-forecasting-api:v1.0
docker run -p 8000:8000 yourusername/energy-forecasting-api:v1.0
```

---

## ☁️ METHOD 2: Cloud Platform Deployment

### **Option A: Heroku**

**Pros:** Free tier, easy setup, Git-based deployment
**Cons:** Limited free hours, slower cold starts

#### **Setup Steps:**

1. **Install Heroku CLI:**
```bash
# macOS
brew install heroku/brew/heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login to Heroku:**
```bash
heroku login
```

3. **Create Heroku app:**
```bash
heroku create energy-forecasting-api
```

4. **Create Procfile:**
```bash
echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

5. **Deploy:**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

6. **Open your app:**
```bash
heroku open
```

Your API is now live at: `https://energy-forecasting-api.herokuapp.com`

---

### **Option B: AWS (Amazon Web Services)**

**Services to use:**
- **AWS Elastic Beanstalk** - Easy deployment (recommended for beginners)
- **AWS ECS** - Docker containers
- **AWS Lambda** - Serverless (for low traffic)

#### **Using Elastic Beanstalk:**

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize:**
```bash
eb init -p python-3.10 energy-forecasting-api
```

3. **Create environment:**
```bash
eb create production
```

4. **Deploy:**
```bash
eb deploy
```

5. **Open:**
```bash
eb open
```

**Estimated cost:** $10-50/month depending on traffic

---

### **Option C: Google Cloud Run**

**Pros:** Pay-per-use, auto-scaling, Docker-based
**Cons:** Requires Google Cloud account

#### **Setup Steps:**

1. **Install gcloud CLI:**
```bash
# Follow: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate:**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Build and deploy:**
```bash
gcloud run deploy energy-forecasting-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

4. **Your API is live!** URL provided in output

**Estimated cost:** ~$0-5/month for low traffic (free tier available)

---

### **Option D: Azure**

**Using Azure App Service:**

1. **Install Azure CLI:**
```bash
# Follow: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

2. **Login:**
```bash
az login
```

3. **Create resource group:**
```bash
az group create --name energy-api-rg --location eastus
```

4. **Create app service:**
```bash
az webapp up --name energy-forecasting-api \
  --resource-group energy-api-rg \
  --runtime "PYTHON:3.10"
```

**Estimated cost:** $10-100/month depending on plan

---

## 🖥️ METHOD 3: VPS Deployment (DigitalOcean, Linode, etc.)

### **Why VPS?**
- Full control
- More affordable for consistent traffic
- Good for learning

---

### **Step 1: Setup VPS**

1. **Create a droplet/instance** (Ubuntu 22.04 recommended)
2. **SSH into server:**
```bash
ssh root@your-server-ip
```

---

### **Step 2: Install Dependencies**

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.10
apt install python3.10 python3.10-venv python3-pip -y

# Install nginx (reverse proxy)
apt install nginx -y

# Install supervisor (process manager)
apt install supervisor -y
```

---

### **Step 3: Deploy Application**

```bash
# Create app directory
mkdir -p /var/www/energy-api
cd /var/www/energy-api

# Clone your repo (or use SCP to upload files)
git clone https://github.com/yourusername/ml-energy-forecasting.git .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test locally
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

### **Step 4: Configure Supervisor**

Create `/etc/supervisor/conf.d/energy-api.conf`:

```ini
[program:energy-api]
directory=/var/www/energy-api
command=/var/www/energy-api/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/energy-api/err.log
stdout_logfile=/var/log/energy-api/out.log
```

Create log directory and start:
```bash
mkdir -p /var/log/energy-api
supervisorctl reread
supervisorctl update
supervisorctl start energy-api
```

---

### **Step 5: Configure Nginx**

Create `/etc/nginx/sites-available/energy-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your-server-ip

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable and restart:
```bash
ln -s /etc/nginx/sites-available/energy-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

Your API is now live at: `http://your-server-ip/`

---

### **Step 6: Enable HTTPS (Optional but Recommended)**

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
certbot --nginx -d your-domain.com

# Auto-renew
certbot renew --dry-run
```

Your API is now at: `https://your-domain.com/`

---

## 🔒 Production Best Practices

### **1. Environment Variables**

Never hardcode secrets! Use environment variables:

```bash
# .env file (DO NOT commit to git!)
MODEL_PATH=/var/www/energy-api/models/energy_model.pkl
SCALER_PATH=/var/www/energy-api/models/scaler.pkl
LOG_LEVEL=INFO
```

Load in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH")
```

---

### **2. Logging**

Add proper logging in `api/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(data: PredictionInput):
    logger.info(f"Prediction request: {data}")
    # ... prediction logic
    logger.info(f"Prediction result: {result}")
    return result
```

---

### **3. Rate Limiting**

Protect against abuse:

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/predict")
@limiter.limit("10/minute")  # 10 requests per minute
async def predict(request: Request, data: PredictionInput):
    # ... prediction logic
```

---

### **4. Health Check Endpoint**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }
```

Monitor this endpoint with:
- UptimeRobot (free)
- Pingdom
- AWS CloudWatch

---

### **5. CORS Configuration**

For production, restrict CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

### **6. Error Tracking**

Use Sentry for error monitoring:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

---

## 📊 Monitoring & Maintenance

### **Metrics to Track:**
- Request count
- Response times
- Error rates
- Model prediction distribution
- Server CPU/Memory usage

### **Tools:**
- **Grafana + Prometheus** - Metrics visualization
- **ELK Stack** - Log aggregation
- **New Relic / Datadog** - APM (paid)

---

## 🔄 CI/CD Pipeline (Optional)

**Using GitHub Actions:**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/energy-api
            git pull
            source venv/bin/activate
            pip install -r requirements.txt
            supervisorctl restart energy-api
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (Low Traffic) | Paid (High Traffic) |
|----------|-----------|-------------------|---------------------|
| Heroku | 550 hrs/month | $7/month | $25-250/month |
| Google Cloud Run | 2M requests/month | $0-5/month | $10-100/month |
| AWS | 12 months free | $10-30/month | $50-500/month |
| DigitalOcean VPS | N/A | $6/month | $12-48/month |
| Azure | 12 months free | $10-30/month | $50-500/month |

---

## 🐛 Common Issues

### **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

### **Model File Too Large for Git**
```bash
# Use Git LFS
git lfs install
git lfs track "*.pkl"
git add .gitattributes
```

### **Out of Memory**
- Increase VPS RAM
- Use model compression
- Reduce number of workers

---

## ✅ Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Model file accessible
- [ ] Dependencies installed
- [ ] CORS properly configured
- [ ] HTTPS enabled (production)
- [ ] Logging implemented
- [ ] Error tracking enabled
- [ ] Health check endpoint working
- [ ] Rate limiting configured
- [ ] Firewall rules set
- [ ] Monitoring set up
- [ ] Backup strategy defined

---

## 📚 Further Reading

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt (SSL)](https://letsencrypt.org/)

---

**Questions?** Open an issue on GitHub or refer to the API_GUIDE.md for API-specific documentation.
