# AVALYOS Troubleshooting Guide

## 🔍 Quick Diagnosis

Start here if something isn't working. Follow the symptom that matches your issue.

---

## 🔴 Backend Issues

### Problem: "Port 8000 already in use"
**Cause**: Another application using port 8000  
**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual PID)
taskkill /PID <PID> /F

# Or use different port
uvicorn aval_backend:app --port 8001
```

### Problem: "qsharp module not found"
**Cause**: qsharp package not installed  
**Solution**:
```powershell
pip install qsharp==1.22.0
```

**Alternative Solution**:
```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: Backend returns "Internal Server Error (500)"
**Cause**: Q# operation failed or queue overflow  
**Solution**:
1. Check backend logs in terminal
2. Try restarting backend:
```powershell
# Press Ctrl+C to stop
# Then restart
uvicorn aval_backend:app
```

3. If queue full (Q# error), wait 60 seconds

### Problem: Backend returns HTTP 429 (Too Many Requests)
**Cause**: Rate limit exceeded (60 requests/minute)  
**Solution**:
1. Wait 60 seconds for queue to clear
2. Or increase limit in `.env`:
```bash
AVAL_RATE_PER_MIN=1000
```

### Problem: "Unable to import qsharp"
**Cause**: Q# SDK not properly installed  
**Solution**:
```powershell
# Full reinstall
pip uninstall qsharp -y
pip install qsharp==1.22.0

# Verify installation
python -c "import qsharp; print(qsharp.__version__)"
```

### Problem: API endpoint returns 404
**Cause**: Wrong URL or endpoint doesn't exist  
**Solution**:

Check available endpoints:
```bash
GET http://localhost:8000/              # Health check
GET http://localhost:8000/sample        # Single sample
GET http://localhost:8000/sample/many/100  # 100 samples
GET http://localhost:8000/branches/Microsoft  # Branches for company
```

---

## 🔴 Frontend Issues

### Problem: "Streamlit app won't start"
**Cause**: Port 8501 in use or dependency missing  
**Solution**:
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install missing packages
pip install streamlit pandas numpy

# Run
streamlit run app.py
```

### Problem: "companies.json not found"
**Cause**: Database file missing  
**Solution**:
```powershell
python generate_database.py
```

Verify file created:
```powershell
Test-Path companies.json
Get-Item companies.json | Select-Object Length
```

### Problem: "Page 3 - Search returns no results"
**Cause**: Search function issue or bad JSON structure  
**Solution**:
```powershell
# Test search function
python -c "from utils import load_data, search_companies; data = load_data('companies.json'); print(search_companies(data, 'Microsoft'))"

# Expected output:
# [{'name': 'Microsoft', 'code': 'ms'}]
```

If no output or error:
1. Regenerate database: `python generate_database.py`
2. Restart Streamlit: Close browser, stop app, restart

### Problem: "AttributeError: 'str' object has no attribute 'get'"
**Status**: ✅ FIXED in current version  
**Historical**: This was caused by wrong data structure iteration  
**If reoccurs**: 
```powershell
# Update from latest
git pull

# Or manually fix: companies are dict keys, not list items
# Correct: data.get("companies", {}).items()
# Wrong: data.get("companies", [])
```

### Problem: Streamlit page takes too long to load
**Cause**: Large data file or slow search  
**Solution**:
```powershell
# Check companies.json size
Get-Item companies.json | Select-Object Length

# If large (>5MB), regenerate
python generate_database.py

# Or reduce in generate_database.py:
# Change: COMPANY_COUNT = 30
# To:     COMPANY_COUNT = 10
```

### Problem: "No module named 'utils'"
**Cause**: Running from wrong directory  
**Solution**:
```powershell
# Must run from project root
cd c:\Users\USER\OneDrive\Desktop\aval_program

# Then run Streamlit
streamlit run app.py
```

---

## 🔴 Database Issues

### Problem: "PostgreSQL connection refused"
**Cause**: PostgreSQL not running or wrong credentials  
**Solution**:

Check if PostgreSQL is running:
```powershell
# Windows Services
Get-Service PostgreSQL* | Select-Object Name, Status

# Or manually start
pg_ctl -D "C:\Program Files\PostgreSQL\data" start
```

Verify credentials in `.env`:
```bash
DATABASE_URL=postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db
```

Test connection:
```powershell
pip install psycopg2-binary
python -c "import psycopg2; conn = psycopg2.connect('postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db'); print('Connected!')"
```

### Problem: "MongoDB connection error"
**Cause**: MongoDB not running or wrong URI  
**Solution**:

Check if MongoDB is running:
```powershell
Get-Service MongoDB | Select-Object Name, Status

# Or manually start
mongod
```

Verify URI in `.env`:
```bash
MONGODB_URI=mongodb://avalyos:avalyos_password@localhost:27017/avalyos_db
```

Test connection:
```powershell
pip install pymongo
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print(client.admin.command('ping'))"
```

### Problem: "sqlalchemy.exc.OperationalError"
**Cause**: Database connection or migration issue  
**Solution**:
```powershell
# Reinstall SQLAlchemy
pip install --upgrade sqlalchemy

# Recreate database
python setup_databases.py
```

### Problem: "Database table already exists"
**Cause**: Trying to init existing database  
**Solution**:

Option 1: Drop and recreate
```powershell
# PostgreSQL
psql -U avalyos -d avalyos_db -c "DROP TABLE IF EXISTS user_session CASCADE;"
psql -U avalyos -d avalyos_db -c "DROP TABLE IF EXISTS simulation_result CASCADE;"
# ... drop other tables

# Then reinit
python setup_databases.py
```

Option 2: Use existing database (in code)
```python
# In database_models.py, comment out init calls
# init_postgres_db()  # Skip if already initialized
```

---

## 🔴 Testing Issues

### Problem: "pytest: command not found"
**Cause**: pytest not installed  
**Solution**:
```powershell
pip install pytest pytest-asyncio
python -m pytest tests/test_backend.py -v
```

### Problem: "Test fails with 'ModuleNotFoundError'"
**Cause**: Wrong working directory  
**Solution**:
```powershell
cd c:\Users\USER\OneDrive\Desktop\aval_program
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_backend.py -v
```

### Problem: "Tests hang or timeout"
**Cause**: Backend server still running or Q# simulator stuck  
**Solution**:
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Wait 5 seconds
Start-Sleep -Seconds 5

# Retry tests
python -m pytest tests/test_backend.py -v
```

---

## 🟡 Performance Issues

### Problem: "Streamlit page refresh is slow"
**Cause**: Large computations or slow data loading  
**Solution**:
```powershell
# Profile which function is slow
python -m cProfile -s cumulative utils.py

# Or add timing:
import time
start = time.time()
# ... your code ...
print(f"Time: {time.time() - start:.2f}s")
```

### Problem: "Search takes too long"
**Cause**: Large companies.json file  
**Solution**:
1. Reduce database size: `python generate_database.py` (set COMPANY_COUNT=10)
2. Or cache results in Streamlit:
```python
@st.cache_data
def search_cached(data, query):
    return search_companies(data, query)
```

### Problem: "Backend responses are slow"
**Cause**: Q# simulator overhead or many pending operations  
**Solution**:
1. Check queue size in backend logs
2. Increase QSHARP_QUEUE_MAX if needed:
```bash
QSHARP_QUEUE_MAX=128
```

---

## 🟡 Configuration Issues

### Problem: "Environment variables not being read"
**Cause**: `.env` file not in project root or not loaded  
**Solution**:
```powershell
# Copy template
Copy-Item .env.example .env

# Edit with your values
notepad .env

# Then load manually (add to startup script):
# In aval_backend.py
from dotenv import load_dotenv
load_dotenv()
```

### Problem: "Getting 'AVAL_API_KEY' env var not set"
**Cause**: Environment variable not configured  
**Solution**:

Option 1: Set in `.env`
```bash
AVAL_API_KEY=my_secret_key_12345
```

Option 2: Set in PowerShell
```powershell
$env:AVAL_API_KEY = "my_secret_key_12345"
```

Option 3: Make optional (in code)
```python
api_key = os.getenv("AVAL_API_KEY", "")  # Default to empty
```

### Problem: "DATABASE_URL not recognized"
**Cause**: Missing or malformed connection string  
**Solution**:

Verify format in `.env`:
```bash
# PostgreSQL (most common)
DATABASE_URL=postgresql://user:password@localhost:5432/database

# or
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/database
```

Test connection string:
```powershell
$env:DATABASE_URL = "postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db"
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

---

## 🟢 Verification Checklist

Before diving deep into troubleshooting, verify basics:

### ✅ Environment
- [ ] Python 3.13+ installed: `python --version`
- [ ] Virtual environment activated: `.\.venv\Scripts\Activate.ps1`
- [ ] Dependencies installed: `pip list | Select-String qsharp`
- [ ] Current directory correct: `Get-Location` shows `aval_program`

### ✅ Files
- [ ] companies.json exists: `Test-Path companies.json`
- [ ] Backend file exists: `Test-Path aval_backend.py`
- [ ] Test file exists: `Test-Path tests/test_backend.py`
- [ ] utils.py exists: `Test-Path utils.py`

### ✅ Services
- [ ] PostgreSQL running (if using): `Get-Service PostgreSQL`
- [ ] MongoDB running (if using): `Get-Service MongoDB`
- [ ] No port conflicts: `netstat -ano | findstr :8000`

### ✅ Connections
- [ ] Backend responds: `curl http://localhost:8000/`
- [ ] Streamlit accessible: `Start http://localhost:8501`
- [ ] Database connection works: `python -c "from database_models import get_session; print(get_session())"`

---

## 📞 Getting Advanced Help

### If issue persists after troubleshooting:

1. **Gather diagnostic info**
```powershell
# Save system info
python --version | Out-File diagnostic.txt
pip list | Out-File -Append diagnostic.txt
Get-Item companies.json | Out-File -Append diagnostic.txt
```

2. **Check logs**
```powershell
# Backend logs are in console output
# Streamlit logs: http://localhost:8501 > Developer Tools (F12)

# Check log files
Get-Content uvicorn.log
Get-Content uvicorn.err
```

3. **Run diagnostic script**
```powershell
python -c "
import sys; print('Python:', sys.version)
import json; d=json.load(open('companies.json')); print('Companies:', len(d.get('companies',{})))
from utils import load_data; data = load_data('companies.json'); print('Loaded OK')
"
```

4. **Isolate the issue**
- Test backend separately: `uvicorn aval_backend:app`
- Test frontend separately: `streamlit run app.py`
- Test database separately: `python setup_databases.py`

---

## 🎓 Common Solutions by Technology

### Q#/Quantum Issues
```powershell
# Reinstall Q#
pip uninstall qsharp -y
pip install qsharp==1.22.0

# Verify
python -c "import qsharp; print('Q# version:', qsharp.__version__)"
```

### FastAPI Issues
```powershell
# Upgrade FastAPI
pip install --upgrade fastapi uvicorn

# Check version
python -c "import fastapi; print(fastapi.__version__)"
```

### Streamlit Issues
```powershell
# Clear cache
streamlit cache clear

# Reinstall
pip install --upgrade streamlit

# Run with debug
streamlit run app.py --logger.level=debug
```

### Database Issues
```powershell
# Test each database
# PostgreSQL
psql -h localhost -U avalyos -d avalyos_db -c "SELECT version();"

# MongoDB
mongosh --eval "db.adminCommand('ping')"

# JSON
python -c "import json; json.load(open('companies.json')); print('JSON OK')"
```

---

## ✨ Tips & Tricks

### Speed up development
```powershell
# Streamlit app only (no backend)
streamlit run app.py

# Backend only for testing
uvicorn aval_backend:app --reload
```

### Debug mode
```powershell
# Python debug with breakpoints
python -m pdb aval_backend.py

# Streamlit debug
streamlit run app.py --logger.level=debug

# FastAPI docs
# Visit http://localhost:8000/docs for interactive API explorer
```

### Quick resets
```powershell
# Regenerate database
python generate_database.py

# Clear Python cache
Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Recurse

# Fresh virtual environment (nuclear option)
Remove-Item .venv -Recurse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

**Remember**: Most issues are solved by:
1. Activating virtual environment: `.\.venv\Scripts\Activate.ps1`
2. Being in project directory: `cd c:\Users\USER\OneDrive\Desktop\aval_program`
3. Reinstalling packages: `pip install -r requirements.txt`
4. Restarting services: Kill process, restart, give it 5 seconds

Good luck! 🚀
