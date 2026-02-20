# ✈️ Professional Flight Planner

A comprehensive AI-powered flight planning system with real-time weather, route optimization, airspace restrictions, and ETOPS compliance checking.

![Phase 2 Complete](https://img.shields.io/badge/Phase-2%20Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## 🚀 Features

### Phase 1: Core System
- ✈️ **Aircraft Database**: 18 aircraft types (Boeing, Airbus, Embraer)
- 🌐 **Airport Database**: 60+ major airports worldwide
- ⛽ **Fuel Calculator**: ICAO-compliant fuel planning
- 🤖 **AI Integration**: GPT-4o-powered assistant
- 📊 **Fine-tuning**: Custom model training capability
- 🖥️ **Web Interface**: Professional Streamlit UI

### Phase 2: Advanced Features
- 🌤️ **Real-time Weather**: METAR, TAF, SIGMETs integration
- 🗺️ **Route Optimization**: Great circle routing with waypoints
- 🚫 **Airspace Restrictions**: No-fly zones and conflict area checking
- ✓ **ETOPS Compliance**: Twin-engine overwater verification

### Product Features
- 👤 **User Authentication**: Secure login and registration
- 💾 **Flight Plan Storage**: Save and manage flight plans
- 📈 **Dashboard**: Personal statistics and analytics
- 📚 **Flight History**: Track all your plans

## 📋 Installation

### Local Setup

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key** (for AI features)
   - Get your key from [platform.openai.com](https://platform.openai.com)
   - Set as environment variable:
     ```bash
     # Windows
     set OPENAI_API_KEY=your-key-here
     
     # Mac/Linux
     export OPENAI_API_KEY=your-key-here
     ```
   - Or enter it in the app's sidebar

4. **Run the application**
   ```bash
   # Authenticated version (with user accounts)
   streamlit run app_auth.py
   
   # Professional version (no login required)
   streamlit run app_pro.py
   
   # Basic AI assistant
   python ai_flight_planner.py
   ```

## ☁️ Deployment

### Deploy to Streamlit Cloud (Free & Easiest)

1. **Create a GitHub repository**
   - Push all your project files to GitHub
   - Make sure `.gitignore` is included

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `app_auth.py`
   - Click "Deploy"

3. **Add secrets** (for OpenAI API key)
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add:
     ```toml
     OPENAI_API_KEY = "your-key-here"
     ```

### Deploy to Railway (Alternative)

1. Install Railway CLI: `npm install -g railway`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`
5. Add environment variable: `railway variables set OPENAI_API_KEY=your-key`

### Deploy to Heroku (Alternative)

1. Create `Procfile`:
   ```
   web: streamlit run app_auth.py --server.port=$PORT
   ```
2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-key
   git push heroku main
   ```

## 📖 Usage Guide

### For Pilots

1. **Register an account**
   - Click "Register" tab
   - Enter username, email, password
   - Optionally add pilot license info

2. **Create a flight plan**
   - Go to "New Flight Plan" tab
   - Select aircraft, origin, destination
   - Set altitude and wind conditions
   - Click "Generate Flight Plan"

3. **Review safety checks**
   - Airspace clear ✅
   - ETOPS compliant ✅
   - Fuel adequate ✅

4. **Save and track**
   - Plan automatically saves to your account
   - View all plans in "My Flight Plans"
   - Track statistics in "Dashboard"

### For Developers

**Test individual modules:**
```bash
python aircraft_database.py    # Test aircraft lookups
python airport_database.py     # Test route calculations
python fuel_calculator.py      # Test fuel planning
python weather_integration.py  # Test weather API
python route_optimization.py   # Test routing
python airspace_restrictions.py # Test airspace checks
python etops_compliance.py     # Test ETOPS
python database.py             # Test database
```

**Generate training data for fine-tuning:**
```bash
python training_data_generator.py
```

**Fine-tune GPT-4o:**
```bash
python finetune_model.py --auto
```

## 📁 Project Structure

```
flight-planner/
├── app_auth.py                 # Main authenticated app
├── app_pro.py                  # Professional app (no auth)
├── database.py                 # User authentication & storage
├── aircraft_database.py        # 18 aircraft types
├── airport_database.py         # 60+ airports
├── fuel_calculator.py          # ICAO fuel planning
├── weather_integration.py      # Real-time weather
├── route_optimization.py       # Route generation
├── airspace_restrictions.py    # No-fly zones
├── etops_compliance.py         # ETOPS checking
├── ai_flight_planner.py        # AI integration
├── training_data_generator.py  # Fine-tuning data
├── finetune_model.py          # Model training
├── requirements.txt            # Dependencies
├── .gitignore                 # Git exclusions
├── .streamlit/
│   └── config.toml            # Streamlit config
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for AI features

### Database

- SQLite database: `flight_planner.db`
- Automatically created on first run
- Contains: users, flight_plans, flight_history, preferences

## ⚠️ Important Notes

**For Educational/Demonstration Use Only**

- This system is for educational purposes
- Always use certified flight planning tools for real operations
- Weather data is for reference only
- Verify all information with official aviation sources
- Not approved for commercial aviation use

**Data Privacy**

- User passwords are hashed (SHA-256)
- Flight plans stored locally in SQLite
- No data transmitted to third parties (except OpenAI API)
- Database file should not be committed to public repositories

## 🛠️ Technical Details

**Built With:**
- Python 3.9+
- Streamlit (Web UI)
- OpenAI GPT-4o (AI Assistant)
- SQLite (Database)
- FAA Aviation Weather API (Weather data)

**Key Algorithms:**
- Haversine formula (great circle distance)
- ICAO fuel planning standards
- Wind correction calculations
- ETOPS diversion verification

## 📊 System Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| Aircraft Types | ✅ | 18 types (737, 747, 777, 787, A320, A330, A350, A380, etc.) |
| Airports | ✅ | 60+ major international airports |
| Weather | ✅ | METAR, TAF, SIGMETs (real-time) |
| Route Planning | ✅ | Great circle with waypoints |
| Airspace | ✅ | 12+ restricted zones |
| ETOPS | ✅ | 30+ diversion airports |
| User Accounts | ✅ | Full authentication system |
| AI Assistant | ✅ | Natural language processing |

## 🤝 Contributing

This is an educational project. Contributions welcome!

## 📄 License

Educational use only. Not for commercial aviation operations.

## 👤 Author

Built as a comprehensive learning project demonstrating:
- Aviation systems integration
- AI/ML implementation
- Full-stack development
- Production deployment

## 🆘 Support

For issues or questions:
1. Check the documentation above
2. Review individual module tests
3. Verify API keys are set correctly
4. Check Streamlit Cloud logs (if deployed)

---

**Version 2.0 | Phase 2 Complete | February 2026**

✈️ Safe flights!
