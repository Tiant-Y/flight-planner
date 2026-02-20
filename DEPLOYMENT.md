# 🚀 Deployment Guide

Complete guide to deploying your Flight Planner to the cloud.

## Option 1: Streamlit Cloud (Recommended - FREE)

### Prerequisites
- GitHub account
- All project files in a GitHub repository

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Initialize git (if not done already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Flight Planner v2.0"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/flight-planner.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Authorize Streamlit Cloud
4. Click "New app"
5. Configure:
   - **Repository**: `YOUR_USERNAME/flight-planner`
   - **Branch**: `main`
   - **Main file path**: `app_auth.py`
6. Click "Advanced settings" (optional)
7. Add secrets:
   ```toml
   # In the secrets section, add:
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```
8. Click "Deploy"

#### 3. Wait for Deployment

- Initial deployment takes 2-5 minutes
- You'll get a URL like: `https://YOUR_APP.streamlit.app`
- Share this URL with anyone!

#### 4. Managing Your App

- **Reboot app**: From Streamlit Cloud dashboard
- **View logs**: Click "Manage app" → "Logs"
- **Update secrets**: "Settings" → "Secrets"
- **Update code**: Just push to GitHub, auto-deploys

### Cost: **FREE** ✅
- Unlimited public apps
- 1GB RAM per app
- Shared compute resources

---

## Option 2: Railway (Easy - Paid)

### Prerequisites
- Railway account ([railway.app](https://railway.app))
- Railway CLI installed

### Deployment Steps

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variable
railway variables set OPENAI_API_KEY=sk-your-key-here

# Get your URL
railway domain
```

### Cost: ~$5-10/month
- 500 hours free tier
- Then $5-10/month depending on usage

---

## Option 3: Heroku (Traditional - Paid)

### Prerequisites
- Heroku account
- Heroku CLI installed

### Additional Files Needed

Create `Procfile`:
```
web: streamlit run app_auth.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:
```
python-3.11.0
```

### Deployment Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-flight-planner

# Set config
heroku config:set OPENAI_API_KEY=sk-your-key-here

# Deploy
git push heroku main

# Open app
heroku open
```

### Cost: $7/month minimum
- Free tier discontinued in 2022
- Hobby plan: $7/month

---

## Option 4: Self-Hosted (VPS)

### Prerequisites
- VPS (DigitalOcean, AWS EC2, etc.)
- Ubuntu 22.04 or similar

### Setup Steps

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3-pip -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/flight-planner.git
cd flight-planner

# Install dependencies
pip3 install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=sk-your-key-here

# Install screen (to keep app running)
sudo apt install screen -y

# Start in screen session
screen -S flight-planner
streamlit run app_auth.py --server.port=8501 --server.address=0.0.0.0

# Detach from screen: Ctrl+A, then D
# Reattach: screen -r flight-planner
```

### Configure Firewall
```bash
sudo ufw allow 8501
sudo ufw enable
```

### Production Setup with Nginx

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/flight-planner
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/flight-planner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Cost: $5-20/month
- DigitalOcean: $5/month (basic droplet)
- AWS EC2: $5-20/month depending on instance

---

## Database Considerations

### For Production (Multiple Users)

Current setup uses SQLite (single file database). For production with many users, consider upgrading to PostgreSQL:

#### Update database.py

Replace:
```python
DB_PATH = "flight_planner.db"
conn = sqlite3.connect(DB_PATH)
```

With:
```python
import psycopg2
DB_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DB_URL)
```

#### Add to requirements.txt
```
psycopg2-binary>=2.9.0
```

#### Setup on Railway/Heroku
Both platforms offer free PostgreSQL:
- Railway: Add PostgreSQL plugin
- Heroku: `heroku addons:create heroku-postgresql`

---

## Environment Variables

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `DATABASE_URL` - PostgreSQL connection string (if using)
- `PORT` - Port number (usually set by platform)

---

## Monitoring & Maintenance

### Check Logs

**Streamlit Cloud:**
- Dashboard → "Manage app" → "Logs"

**Railway:**
```bash
railway logs
```

**Heroku:**
```bash
heroku logs --tail
```

### Update Your App

**All platforms:**
1. Make changes locally
2. Commit and push to GitHub
3. Platform auto-deploys (or manual deploy)

---

## Security Checklist

- [ ] `.gitignore` includes `.env` and `*.db`
- [ ] API keys stored as environment variables
- [ ] Database file not committed to repository
- [ ] User passwords hashed in database
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] Regular backups of database (if production)

---

## Troubleshooting

### App won't start
- Check logs for errors
- Verify all dependencies in requirements.txt
- Check Python version compatibility

### Database errors
- Ensure database file has write permissions
- Check if database module initialized
- Verify SQLite version

### API errors
- Confirm OPENAI_API_KEY is set correctly
- Check API key has credits
- Verify network connectivity

### Performance issues
- Check available RAM
- Consider upgrading plan
- Optimize database queries

---

## Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| **Streamlit Cloud** | ✅ Unlimited | N/A | Quick demos, personal projects |
| **Railway** | 500 hrs | $5-10/mo | Production apps, good performance |
| **Heroku** | ❌ None | $7/mo | Traditional hosting, lots of add-ons |
| **Self-hosted VPS** | ❌ None | $5-20/mo | Full control, custom setup |

---

## Recommended Deployment Path

**For Learning/Demo:**
→ Streamlit Cloud (FREE)

**For Small Production:**
→ Railway ($5-10/month)

**For Large Scale:**
→ Self-hosted VPS + PostgreSQL + Nginx

---

## Next Steps After Deployment

1. ✅ Test all features on deployed app
2. ✅ Share URL with users
3. ✅ Monitor logs for errors
4. ✅ Set up analytics (optional)
5. ✅ Configure custom domain (optional)
6. ✅ Set up automated backups (if production)

---

**Deployment complete!** 🎉

Your Flight Planner is now live and accessible worldwide!
