# AVALYOS Getting Started - Visual Guide

## 🚀 Start Here: 3 Quick Options

### Option 1: 5-Minute Demo (Fastest)
```
1. Activate Virtual Environment
   .\.venv\Scripts\Activate.ps1

2. Run Streamlit
   streamlit run app.py

3. Open Browser
   http://localhost:8501
   
4. Explore 3 Pages
   ✅ Page 1: Select companies by location
   ✅ Page 2: Run quantum simulations
   ✅ Page 3: Search and analyze companies
```

**Time**: ⏱️ 5 minutes  
**Requirements**: Python 3.13, .venv activated  
**Result**: Interactive web app in your browser

---

### Option 2: Full Stack (Complete)
```
1. Activate Virtual Environment
   .\.venv\Scripts\Activate.ps1

2. Terminal 1: Start Backend
   uvicorn aval_backend:app --port 8000
   
3. Terminal 2: Start Frontend
   streamlit run app.py --server.port 8501

4. Open Browser
   Frontend: http://localhost:8501
   API Docs: http://localhost:8000/docs

5. Test API Endpoints
   GET http://localhost:8000/
   GET http://localhost:8000/sample
   GET http://localhost:8000/sample/many/100
```

**Time**: ⏱️ 10 minutes  
**Requirements**: Python 3.13, virtual environment, ports 8000 & 8501 free  
**Result**: Complete quantum computing system with web interface

---

### Option 3: Production Setup (Enterprise)
```
1. Install Databases
   - PostgreSQL 15+
   - MongoDB 6+

2. Setup Databases
   python setup_databases.py
   (Follow interactive wizard)

3. Configure Environment
   - Copy .env.example to .env
   - Set database credentials
   - Set API keys

4. Initialize Databases
   - PostgreSQL tables created
   - MongoDB collections created
   - Company data loaded

5. Deploy Application
   - Docker: docker-compose up
   - Linux: systemctl start services
   - Cloud: Deploy to AWS/Azure/GCP

6. Monitor & Maintain
   - Check logs
   - Monitor performance
   - Backup databases
```

**Time**: ⏱️ 30-60 minutes  
**Requirements**: Databases, deployment platform, DevOps knowledge  
**Result**: Enterprise-grade production system

---

## 📚 Documentation by Role

### 👨‍💻 Developer Getting Started
**Start with**: `QUICKSTART.md`
```
1. Read: QUICKSTART.md (5 min)
2. Do: Follow 5-minute setup
3. Explore: Try all 3 Streamlit pages
4. Test: Run pytest tests/test_backend.py
5. Learn: Read README.md
```

### 🔧 System Administrator
**Start with**: `DEPLOYMENT.md`
```
1. Choose: Pick deployment option
2. Setup: Follow step-by-step guide
3. Secure: Review security checklist
4. Monitor: Set up monitoring/logging
5. Maintain: Follow maintenance plan
```

### 📊 Business Stakeholder
**Start with**: `PROJECT_SUMMARY.md`
```
1. Overview: Read executive summary
2. Architecture: Understand system design
3. Features: See what it does
4. Technology: Learn the tech stack
5. Metrics: Review success measures
```

### 🐛 Troubleshooter
**Start with**: `TROUBLESHOOTING.md`
```
1. Symptoms: Find matching issue
2. Solutions: Apply recommended fix
3. Verify: Test that it works
4. Reference: Check README.md for details
5. Escalate: Use diagnostic info if needed
```

---

## ⚡ Quick Command Reference

### Run Frontend Only
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```
→ Open http://localhost:8501

### Run Backend Only
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn aval_backend:app --port 8000
```
→ Open http://localhost:8000/docs

### Run Tests
```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_backend.py -v
```
→ Should see: `4 passed`

### Generate Database
```powershell
.\.venv\Scripts\Activate.ps1
python generate_database.py
```
→ Creates companies.json with 29 companies

### Setup Databases
```powershell
.\.venv\Scripts\Activate.ps1
python setup_databases.py
```
→ Interactive wizard for PostgreSQL/MongoDB

### Test Search
```powershell
python -c "from utils import load_data, search_companies; data = load_data('companies.json'); print(search_companies(data, 'Microsoft'))"
```
→ Output: `[{'name': 'Microsoft', 'code': 'ms'}]`

---

## 🎯 What Each Page Does

### Page 1: Global Company Navigator
```
┌─────────────────────────────────────────┐
│ SELECT COMPANY LOCATION                 │
├─────────────────────────────────────────┤
│ Continent:  [Asia ▼]                    │
│ Country:    [Japan ▼]                   │
│ State:      [Tokyo ▼]                   │
│ City:       [Tokyo ▼]                   │
├─────────────────────────────────────────┤
│ ✅ COMPANY FOUND: Toyota (ty01)         │
│ Location: Tokyo, Japan, Asia            │
│ Employees: 50,000                       │
│ Sector: Automotive                      │
└─────────────────────────────────────────┘
```
**Purpose**: Browse companies hierarchically  
**Try**: Select different continents and watch options change

### Page 2: Quantum Simulator
```
┌─────────────────────────────────────────┐
│ QUANTUM OPERATIONS SIMULATOR            │
├─────────────────────────────────────────┤
│ [Sample Once] [Run 100 Samples]         │
├─────────────────────────────────────────┤
│ RESULTS:                                │
│ Mean:     45.2                          │
│ Variance: 123.4                         │
│ Std Dev:  11.1                          │
├─────────────────────────────────────────┤
│ Distribution Chart:                     │
│ ████ 45                                 │
│ ███  42                                 │
│ ██   35                                 │
│ ████ 51                                 │
└─────────────────────────────────────────┘
```
**Purpose**: Run quantum simulations  
**Try**: Click "Run 100 Samples" to see distribution

### Page 3: Company Browser
```
┌─────────────────────────────────────────┐
│ COMPANY SEARCH & ANALYSIS               │
├─────────────────────────────────────────┤
│ Search: [Microsoft          ]           │
│                                         │
│ RESULTS:                                │
│ ✓ Microsoft (ms)  [Details ▼]          │
│   Sector: Technology                    │
│   Branches: 8                           │
├─────────────────────────────────────────┤
│ SELECTED: Microsoft                     │
│ Branches: 8 locations worldwide         │
│ Quantum Distribution: [Chart]           │
│ Global Stats: Sectors, Countries        │
└─────────────────────────────────────────┘
```
**Purpose**: Search and analyze companies  
**Try**: Search for different companies and expand details

---

## 🔐 Accessing Protected Endpoints

### Without Authentication (Default)
```bash
curl http://localhost:8000/sample
```

### With API Key
```bash
# Set API key in .env
AVAL_API_KEY=my_secret_key

# Use header
curl -H "X-API-Key: my_secret_key" http://localhost:8000/sample
```

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    USER BROWSER                      │
│              http://localhost:8501                   │
│  (Streamlit: Pages 1, 2, 3)                         │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌──────────────────────────────────────────────────────┐
│              FASTAPI BACKEND                         │
│          http://localhost:8000                       │
│  - Thread-safe Q# operations                        │
│  - Rate limiting & Auth                             │
│  - 4 REST endpoints                                 │
└──────────────────────┬───────────────────────────────┘
                       │ Data Access
                       ▼
┌──────────────────────────────────────────────────────┐
│                   DATABASES                          │
│  - companies.json (Hierarchical)                    │
│  - PostgreSQL (User actions)                        │
│  - MongoDB (Company data)                           │
│  - Q# Simulator (Quantum)                           │
└──────────────────────────────────────────────────────┘
```

---

## ✅ Verification Steps

### Step 1: Check Python
```powershell
python --version
# Expected: Python 3.13.3 (or higher)
```

### Step 2: Check Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
pip list | Select-String "qsharp"
# Expected: qsharp 1.22.0
```

### Step 3: Check Companies Data
```powershell
python -c "import json; d=json.load(open('companies.json')); print(f'Companies: {len(d[\"companies\"])}')"
# Expected: Companies: 29
```

### Step 4: Check Backend Startup
```powershell
.\.venv\Scripts\Activate.ps1
timeout 5 uvicorn aval_backend:app 2>&1 | findstr "Uvicorn"
# Expected: "Uvicorn running on http://0.0.0.0:8000"
```

### Step 5: Check Frontend Startup
```powershell
# This will open your browser automatically - just close it after confirming
timeout 10 streamlit run app.py 2>&1 | findstr "ready"
```

---

## 🎓 Learning Path

### Level 1: User
**Goal**: Understand what AVALYOS does
**Time**: 15 minutes
```
1. Read QUICKSTART.md
2. Run streamlit run app.py
3. Explore all 3 pages
4. Watch data change as you interact
```

### Level 2: Developer
**Goal**: Understand architecture and modify code
**Time**: 1-2 hours
```
1. Read README.md
2. Review aval_backend.py (architecture)
3. Review utils.py (helper functions)
4. Run pytest tests/
5. Make small code changes and test
```

### Level 3: DevOps/Admin
**Goal**: Deploy and maintain system
**Time**: 2-4 hours
```
1. Read DEPLOYMENT.md
2. Choose deployment option
3. Follow setup instructions
4. Configure monitoring
5. Test disaster recovery
```

### Level 4: Architect
**Goal**: Understand system design deeply
**Time**: 4+ hours
```
1. Read PROJECT_SUMMARY.md
2. Review all components
3. Study security implementation
4. Plan scaling strategy
5. Design disaster recovery
```

---

## 🆘 Common First-Time Issues

### Issue: "Port 8501 already in use"
```powershell
streamlit run app.py --server.port 8502
# Use different port (8502, 8503, etc.)
```

### Issue: "Module not found: qsharp"
```powershell
pip install qsharp==1.22.0
```

### Issue: "companies.json not found"
```powershell
python generate_database.py
```

### Issue: "Nothing happens when I click buttons"
1. Check backend is running: `uvicorn aval_backend:app`
2. Verify port 8000 is free: `netstat -ano | findstr :8000`
3. Check Streamlit logs in browser console (F12)

---

## 📞 Getting Help

### Quick Fixes (1 minute)
- Check QUICKSTART.md "Common Issues"
- Check browser console for errors (F12)
- Check terminal for stack traces

### Detailed Help (5-10 minutes)
- Search TROUBLESHOOTING.md for your issue
- Run verification steps above
- Check logs (uvicorn.log, uvicorn.err)

### Deep Dive (30+ minutes)
- Read README.md for architecture
- Review PROJECT_SUMMARY.md for design
- Examine source code with comments
- Run tests to isolate problem

### Last Resort
- Regenerate database: `python generate_database.py`
- Reinstall packages: `pip install -r requirements.txt`
- Fresh virtual environment (nuclear option)

---

## 🎉 You're All Set!

```
✅ AVALYOS is ready to use!

Quick start:
1. .\.venv\Scripts\Activate.ps1
2. streamlit run app.py
3. Open http://localhost:8501

For help:
- Quick setup: Read QUICKSTART.md
- Full guide: Read README.md
- Issues: See TROUBLESHOOTING.md
- Production: Read DEPLOYMENT.md

Enjoy exploring quantum computing! 🚀
```

---

**Ready to get started?**

👉 **NEXT STEP**: Run `streamlit run app.py`

Questions? → Check `QUICKSTART.md`  
Problems? → Check `TROUBLESHOOTING.md`  
Want more? → Read `README.md`
