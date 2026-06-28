# AVALYOS Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Generate Database
```bash
python generate_database.py
```

Output should show:
```
✅ Generated database with:
   - Companies: 30
   - Branches: 190+
   - Continents: 6
   - Countries: 30+
```

### 4. Run Streamlit
```bash
streamlit run app.py
```

Opens at: **http://localhost:8501**

## 🎯 What You Get

### Page 1: Global Company Navigator
- Select from 6 continents
- Drill down to countries, states, cities
- View company location details

### Page 2: Quantum Simulator
- Click "Sample Once" for single Q# execution
- Click "Run 100 Samples" for Monte Carlo analysis
- View mean, variance, standard deviation
- See distribution histogram

### Page 3: Company Browser
- Search for companies (Microsoft, Google, Amazon, etc.)
- Expand results to see branches
- View company statistics
- See global distribution by sector/continent

## 🚀 Optional: Full Setup with Backend & Databases

### Step 1: Start Backend (Terminal 1)
```powershell
uvicorn aval_backend:app --host 0.0.0.0 --port 8000
```

Check health:
```bash
curl http://localhost:8000/
```

Expected: `{"message":"AVALYOS Q# Backend Ready"}`

### Step 2: Start Streamlit (Terminal 2)
```powershell
streamlit run app.py
```

### Step 3: Setup Databases (Optional)
```powershell
python setup_databases.py
```

Follow the interactive wizard to:
1. Set up PostgreSQL
2. Set up MongoDB
3. Load company data

---

## 🧪 Verify Installation

### Test 1: Search Function
```powershell
python -c "from utils import load_data, search_companies; data = load_data('companies.json'); print(search_companies(data, 'Microsoft'))"
```

Expected output:
```
[{'name': 'Microsoft', 'code': 'ms00'}]
```

### Test 2: Backend Health
```powershell
curl http://localhost:8000/
```

Expected:
```json
{"message":"AVALYOS Q# Backend Ready","version":"1.0"}
```

### Test 3: Run Tests
```powershell
pytest tests/test_backend.py -v
```

Expected:
```
test_health PASSED
test_sample_one PASSED
test_sample_many PASSED
test_branches_for_company PASSED
====== 4 passed ======
```

## 📂 File Guide

| File | Purpose |
|------|---------|
| `aval_backend.py` | FastAPI server + Q# integration |
| `app.py` | Streamlit main entry point |
| `pages/1_Global_Company_Navigator.py` | Hierarchical company search |
| `pages/2_Quantum_Simulator.py` | Q# quantum operations UI |
| `pages/3_Company_Browser.py` | Company profile & analysis |
| `utils.py` | Helper functions |
| `companies.json` | Company hierarchical data |
| `generate_database.py` | Create sample database |
| `database_models.py` | PostgreSQL/MongoDB schemas |
| `setup_databases.py` | Database initialization wizard |
| `requirements.txt` | Python dependencies |
## ⚠️ Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'qsharp'"
**Solution**: 
```powershell
pip install qsharp==1.22.0
```

### Issue: "Streamlit app won't start"
**Solution**: Make sure you're in project directory with `.venv` activated
```powershell
cd c:\Users\USER\OneDrive\Desktop\aval_program
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Issue: "companies.json not found"
**Solution**: Generate it
```powershell
python generate_database.py
```

### Issue: Backend returns 429 (Too Many Requests)
**Solution**: You've hit the rate limit (60 requests/minute default)
**Fix**: 
- Set `AVAL_RATE_PER_MIN=1000` in `.env`
- Wait 60 seconds for queue to reset

---

## 🔐 Security Notes

- Backend implements rate limiting: 60 requests/minute per API key
- Optional authentication: Set `AVAL_API_KEY` in `.env`
- All Q# operations run in isolated worker thread
- PostgreSQL/MongoDB connections use connection pooling

---

## 📞 Getting Help

1. **Check logs**: Look at terminal output for errors
2. **Run tests**: `pytest tests/test_backend.py -v`
3. **Verify data**: `python -c "import json; print(json.load(open('companies.json')))"`
4. **Check backends**: 
   - FastAPI: http://localhost:8000/
   - Streamlit: http://localhost:8501

---

## 🎓 Next Steps

1. ✅ Run the 5-minute setup above
2. ✅ Explore all 3 Streamlit pages
3. ✅ Run the backend and test API endpoints
4. ✅ (Optional) Set up PostgreSQL/MongoDB with `setup_databases.py`
5. 📖 Read full documentation in README.md

---

**You're all set! 🎉**

Questions? Check README.md for detailed documentation.
| No output | Verify `qsharp.init()` succeeds |
| Wrong results | Ensure Q# code compiled with latest changes |

---

**Last Updated:** November 25, 2025  
**Status:** ✅ Ready for Production
