# AVALYOS - Advanced Quantum Analytics & Visual Integration Operating System

A sophisticated integration of quantum computing (Q#) with a modern web stack for hierarchical company data analysis and quantum simulations.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  Page 1: Global Company Navigator | Page 2: Quantum Sim │
│         Page 3: Company Browser & Analytics              │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ├─► FastAPI Backend (aval_backend.py)
                          │   - Q# Integration
                          │   - Rate Limiting & Auth
                          │   - Worker Thread Pattern
                          │
                          └─► Databases
                              ├─ PostgreSQL (User Actions, Analytics)
                              └─ MongoDB (Company Data, Simulations)

    Data Source: companies.json (Hierarchical JSON Database)
    Quantum: Microsoft Q# with qsharp 1.22.0
```

## 📋 Features

- **Global Company Navigator**: Hierarchical navigation (Continent → Country → State → City)
- **Quantum Simulator**: Monte Carlo simulations with statistical analysis
- **Company Browser**: Search, profile viewing, and quantum distribution analysis
- **Database Integration**: Persistent storage of simulations and user actions
- **Thread-Safe Q#**: Dedicated worker thread for quantum operations
- **Rate Limiting & Auth**: Per-API-key rate limiting and optional authentication
- **Comprehensive Logging**: User actions and simulation results tracked in PostgreSQL

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.13+
- PostgreSQL (optional but recommended)
- MongoDB (optional but recommended)
- pip (Python package manager)

### 2. Installation

#### Clone/Setup Project
```bash
# Navigate to project directory
cd c:\Users\USER\OneDrive\Desktop\aval_program

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Generate Company Database
```bash
python generate_database.py
```

This creates `companies.json` with:
- 30 major global companies
- 6 continents, 30+ countries
- 5-8 branches per company
- Realistic hierarchical structure

#### Setup Databases (Optional)
```bash
python setup_databases.py
```

This interactive wizard helps you:
1. Set up PostgreSQL (user actions & analytics)
2. Set up MongoDB (company/branch data)
3. Load company data into databases

### 3. Running the Application

#### Option A: Run Everything
```bash
# Terminal 1: Start FastAPI backend
uvicorn aval_backend:app --host 0.0.0.0 --port 8000

# Terminal 2: Start Streamlit frontend
streamlit run app.py
```

#### Option B: Streamlit Only (No Backend)
```bash
streamlit run app.py
```

Access Streamlit at: http://localhost:8501

## 📁 Project Structure

```
aval_program/
├── aval_backend.py              # FastAPI server with Q# integration
├── app.py                       # Streamlit main entry point
├── pages/
│   ├── 1_Global_Company_Navigator.py
│   ├── 2_Quantum_Simulator.py
│   └── 3_Company_Browser.py
├── utils.py                     # Helper functions
├── generate_database.py         # Company database generator
├── database_models.py           # SQLAlchemy & MongoDB models
├── setup_databases.py           # Database setup wizard
├── companies.json               # Hierarchical company data
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── tests/
│   └── test_backend.py         # Unit tests (4/4 passing)
└── logs/                        # Application logs
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# FastAPI
AVAL_PORT=8000
QSHARP_QUEUE_MAX=64
AVAL_RATE_PER_MIN=60
AVAL_API_KEY=your_secret_key

# Databases
DATABASE_URL=postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db
MONGODB_URI=mongodb://avalyos:avalyos_password@localhost:27017/avalyos_db
```

### API Keys

Optional per-endpoint authentication:
```bash
curl -H "X-API-Key: your_secret_key" http://localhost:8000/sample
```

## 📊 API Endpoints

### Health Check
```bash
GET http://localhost:8000/
→ {"message": "AVALYOS Q# Backend Ready", "version": "1.0"}
```

### Single Sample
```bash
GET http://localhost:8000/sample
→ {"success": true, "message": "Sample generated", "result": {"branches": [...]}}
```

### Multiple Samples (Monte Carlo)
```bash
GET http://localhost:8000/sample/many/100
→ {"success": true, "message": "100 samples generated", "results": [...]}
```

### Get Branches for Company
```bash
GET http://localhost:8000/branches/Microsoft
→ {"success": true, "branches": [{"code": "ms00", "name": "HQ", ...}, ...]}
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/test_backend.py -v
```

Expected output:
```
test_backend.py::test_health PASSED
test_backend.py::test_sample_one PASSED
test_backend.py::test_sample_many PASSED
test_backend.py::test_branches_for_company PASSED

====== 4 passed in 0.23s ======
```

### Test Search Function
```bash
python -c "from utils import load_data, search_companies; data = load_data('companies.json'); print(search_companies(data, 'Microsoft'))"
```

Expected output:
```
[{'name': 'Microsoft', 'code': 'ms00'}]
```

## 📚 Streamlit Pages

### Page 1: Global Company Navigator
- Hierarchical dropdowns: Continent → Country → State → City
- Real-time selection display
- Integration with companies.json structure

### Page 2: Quantum Simulator
- Single sample quantum operation
- Monte Carlo simulation (100 samples)
- Statistical analysis: mean, variance, standard deviation
- Distribution visualization (bar chart)

### Page 3: Company Browser
- Company search functionality
- Search results with expandable details
- Selected company analysis with branch information
- Quantum distribution visualization
- Global statistics (continents, sectors, countries)

## 🔐 Security Features

- **Rate Limiting**: Per-API-key request throttling (default: 60 calls/minute)
- **Authentication**: Optional API key validation
- **Thread Safety**: Q# operations in dedicated worker thread
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for all API inputs

## 📈 Performance

- **Worker Thread Pattern**: All Q# operations execute serially on single thread (thread-safe)
- **Bounded Queue**: Max 64 pending operations, returns 429 when full
- **Connection Pooling**: SQLAlchemy with PostgreSQL connection pool
- **In-Memory Cache**: MongoDB connection reused across requests

## 🐛 Troubleshooting

### Streamlit Page 3 - Search Not Working
**Issue**: AttributeError with company search
**Solution**: Fixed in utils.py - companies are dict keys, not list items
```python
# CORRECT approach:
for company_name, company_info in data.get("companies", {}).items():
    branches = company_info.get("branches", {})
```

### Backend Q# Error
**Issue**: "qsharp module not found"
**Solution**: 
```bash
pip install qsharp==1.22.0
```

### PostgreSQL Connection Error
**Issue**: "could not connect to server"
**Solution**:
1. Verify PostgreSQL is running
2. Check DATABASE_URL in .env
3. Ensure database and user exist:
```bash
psql -U postgres
CREATE USER avalyos WITH PASSWORD 'avalyos_password';
CREATE DATABASE avalyos_db OWNER avalyos;
```

### MongoDB Connection Error
**Issue**: "error connecting to mongodb"
**Solution**:
1. Verify MongoDB is running
2. Check MONGODB_URI in .env
3. Test connection:
```bash
mongosh --eval "db.adminCommand('ping')"
```

## 📝 Development Notes

### Q# Integration
The backend uses Microsoft's Q# quantum programming language:
- **Operations**: `SampleBranch()`, `GetSampleBranches(n)`
- **Safety**: All Q# calls execute in dedicated worker thread to avoid thread-safety panics
- **Queue**: Bounded task queue with backpressure (returns 429 when full)

### Database Schema

**PostgreSQL Tables**:
- `user_session`: User login/logout tracking
- `simulation_result`: Cached quantum simulation results
- `user_action`: User interactions (search, select, navigate)
- `company_analytics`: Company/branch statistics

**MongoDB Collections**:
- `companies`: Company master data
- `branches`: Branch-level information
- `simulations`: Quantum simulation cache
- `distributions`: Probability distributions

## 🚢 Deployment

For production deployment:

1. **Environment**: Set all variables in `.env`
2. **Databases**: Set up managed PostgreSQL and MongoDB services
3. **Backend**: Run with Gunicorn
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker aval_backend:app
   ```
4. **Frontend**: Run with Streamlit in headless mode
   ```bash
   streamlit run app.py --server.headless true
   ```
5. **Reverse Proxy**: Use Nginx for HTTPS and load balancing

## 📞 Support

For issues, consult:
- Backend logs: Check console output from `uvicorn`
- Streamlit logs: Check browser console (F12)
- Database logs: PostgreSQL/MongoDB log files
- Test suite: Run `pytest tests/` for validation

## 📄 License

Developed as part of AVALYOS quantum analytics project.

## 🎯 Roadmap

- [ ] Neo4j relationships for company hierarchies
- [ ] Advanced quantum algorithms (VQE, QAOA)
- [ ] Real-time simulation caching
- [ ] Multi-user authentication and permissions
- [ ] Advanced analytics dashboard
- [ ] Export results to CSV/PDF
- [ ] REST API client library

---

**Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
