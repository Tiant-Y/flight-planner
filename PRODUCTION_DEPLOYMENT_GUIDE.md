# PRODUCTION_DEPLOYMENT_GUIDE.md
# Complete Production Deployment Guide
# Auto Weather + Persistent Database

This guide sets up your flight planner with:
1. ✅ Automatic real-time weather (CheckWX API)
2. ✅ Persistent database (PostgreSQL via Supabase)
3. ✅ Production-ready deployment

---

## Part 1: Set Up CheckWX Weather API (5 minutes)

### Step 1: Get Free API Key

1. Go to [checkwxapi.com](https://www.checkwxapi.com)
2. Click **"Sign Up"** (top right)
3. Fill in:
   - Email
   - Password
   - Company: "Personal Project" (or your name)
4. Click **"Create Account"**
5. **Verify your email** (check inbox)
6. Log in → Go to **Dashboard**
7. Copy your **API Key** (looks like: `abc123def456...`)

### Step 2: Test Locally (Optional)

```bash
# Set environment variable
export CHECKWX_API_KEY=your-key-here  # Mac/Linux
set CHECKWX_API_KEY=your-key-here     # Windows

# Test the weather module
python weather_checkwx.py
```

You should see weather data for KLAX and KJFK!

### Step 3: Add to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your app → **⋮ Menu** → **Settings**
3. Go to **Secrets**
4. Add (keep existing OPENAI_API_KEY):
   ```toml
   OPENAI_API_KEY = "sk-your-openai-key"
   CHECKWX_API_KEY = "your-checkwx-key-here"
   ```
5. Click **Save**

---

## Part 2: Set Up Persistent Database (10 minutes)

### Why You Need This

**Problem:** Streamlit Cloud resets the app when:
- No activity for ~1 hour (app goes to sleep)
- You deploy updates
- Server restarts

**Result:** All user accounts and flight plans are lost! 😢

**Solution:** Use PostgreSQL (cloud database that never resets)

---

### Step 1: Create Free Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with GitHub (easiest) or email
4. Click **"New project"**

### Step 2: Create Database

1. Fill in:
   - **Organization:** Create new (use your name)
   - **Project name:** `flight-planner-db`
   - **Database Password:** Create strong password (SAVE THIS!)
   - **Region:** Choose closest to you (e.g., "US West" or "Europe Central")
2. Click **"Create new project"**
3. Wait ~2 minutes (coffee break ☕)

### Step 3: Get Connection String

1. In Supabase dashboard, click **Settings** (left sidebar, bottom)
2. Click **Database**
3. Scroll to **Connection string** section
4. Click **URI** tab
5. Copy the connection string (looks like):
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```
6. **IMPORTANT:** Replace `[YOUR-PASSWORD]` with your actual password!

### Step 4: Add to Streamlit Secrets

1. Go to Streamlit Cloud → Your app → Settings → Secrets
2. Add the DATABASE_URL:
   ```toml
   OPENAI_API_KEY = "sk-your-key"
   CHECKWX_API_KEY = "your-checkwx-key"
   DATABASE_URL = "postgresql://postgres.xxxxx:your-password@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
   ```
3. Click **Save**

### Step 5: Update database.py to Support PostgreSQL

Add this at the top of `database.py`:

```python
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

# Check for PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production: Use PostgreSQL
    USE_POSTGRES = True
    print("✅ Using PostgreSQL (persistent)")
else:
    # Development: Use SQLite
    USE_POSTGRES = False
    DB_PATH = "flight_planner.db"
    print("⚠️ Using SQLite (local only)")


def get_connection():
    """Get database connection"""
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
```

Then replace all instances of:
```python
conn = sqlite3.connect(DB_PATH)
```

With:
```python
conn = get_connection()
```

### Step 6: Update requirements.txt

Add PostgreSQL driver:

```txt
streamlit>=1.28.0
openai>=1.0.0
requests>=2.31.0
psycopg2-binary>=2.9.0
```

---

## Part 3: Deploy Updated App

### Step 1: Update Files Locally

Replace your files with the new improved versions:
- ✅ `app_improved.py` (with CheckWX integration)
- ✅ `weather_checkwx.py` (CheckWX weather module)
- ✅ `database.py` (updated with PostgreSQL support)
- ✅ `requirements.txt` (with psycopg2-binary)

### Step 2: Push to GitHub

Using GitHub Desktop:
1. You'll see 4 changed files
2. Uncheck any `.db`, `.csv`, `.env` files
3. Commit message: "Add CheckWX weather & PostgreSQL database"
4. Click **"Commit to main"**
5. Click **"Push origin"**

### Step 3: Update Streamlit Cloud

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click **⋮ Menu** → **Settings**
4. Change **Main file path** to: `app_improved.py`
5. Click **Save**
6. App will redeploy automatically (2-3 minutes)

---

## Part 4: Test Everything

### Test 1: Weather Integration

1. Open your deployed app
2. Create account / Log in
3. Create new flight plan
4. Check for message:
   - ✅ "Using CheckWX API" → Great! Premium weather
   - ⚠️ "Using FAA" → API key not set (still works, just basic)

### Test 2: Database Persistence

1. Create a flight plan
2. Log out
3. **Wait 5 minutes** (or force restart: Settings → Reboot app)
4. Log back in
5. ✅ Your flight plan should still be there!

If data is there after restart → **Success!** 🎉

---

## Part 5: Monitoring & Maintenance

### Monitor CheckWX Usage

1. Go to [checkwxapi.com](https://www.checkwxapi.com) → Dashboard
2. See requests used (400/day limit on free tier)
3. Upgrade to paid if needed ($10/month for 10,000 requests)

### Monitor Database Usage

1. Go to Supabase → Your project → Database
2. Check **Table Editor** to see your data
3. Free tier includes:
   - 500 MB database
   - Unlimited API requests
   - Automatic backups

### Backup Your Data (Optional)

Supabase automatically backs up daily. To manual backup:
1. Supabase → Database → Backups
2. Click **"Download backup"**

---

## Troubleshooting

### Weather Not Showing

**Problem:** "Error fetching weather"

**Solutions:**
1. Check CHECKWX_API_KEY is in Streamlit secrets
2. Verify API key is valid (login to CheckWX)
3. Check you haven't exceeded 400 requests/day
4. App will fallback to FAA automatically

### Database Errors

**Problem:** "psycopg2 not installed"

**Fix:** Add `psycopg2-binary>=2.9.0` to requirements.txt

**Problem:** "Connection refused"

**Fix:** Check DATABASE_URL in secrets is correct

**Problem:** Data still resetting

**Fix:** Verify you're using `app_improved.py` not `app_auth.py`

### App Won't Start

**Problem:** Import errors

**Fix:** 
```bash
# Test locally first
pip install -r requirements.txt
streamlit run app_improved.py
```

---

## Cost Summary

| Service | Free Tier | Cost After Free |
|---------|-----------|-----------------|
| **Streamlit Cloud** | ✅ Unlimited public apps | Free forever |
| **CheckWX** | ✅ 400 requests/day | $10/mo for 10k |
| **Supabase** | ✅ 500MB, unlimited requests | $25/mo for 8GB |
| **OpenAI API** | ❌ Pay-per-use | ~$0.50-2/day typical |

**Total monthly cost for small usage:** ~$0-10/month

---

## Features Now Available

✅ **Automatic Real-Time Weather**
- Wind speed and direction
- Temperature, visibility
- Flight category (VFR/IFR)
- Automatic headwind calculation
- Humidity, pressure, dewpoint

✅ **Persistent Database**
- User accounts never reset
- Flight plans saved forever
- Statistics preserved
- Works 24/7

✅ **Production Ready**
- Handles multiple users
- Automatic backups
- Scalable
- Professional quality

---

## Next Steps

1. ✅ Get CheckWX API key (5 min)
2. ✅ Create Supabase database (10 min)
3. ✅ Update secrets in Streamlit Cloud
4. ✅ Deploy improved app
5. ✅ Test everything
6. 🎉 Share with users!

---

## Support

**CheckWX Help:** [support@checkwx.com](mailto:support@checkwx.com)
**Supabase Docs:** [supabase.com/docs](https://supabase.com/docs)
**Streamlit Docs:** [docs.streamlit.io](https://docs.streamlit.io)

---

**Congratulations!** Your flight planner is now production-ready with automatic weather and persistent data storage! 🚀✈️
