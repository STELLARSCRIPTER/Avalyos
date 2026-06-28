# 🌍 AVALYOS Streamlit Frontend

A quantum-powered global company navigation and analysis platform built with Streamlit.

## 📋 Overview

**AVALYOS** is a multipage Streamlit application that provides:

- **Hierarchical Navigation** — Explore companies by continent → country → state → city
- **Quantum Sampling & Simulations** — Run Monte Carlo tests and quantum sampling
- **Company Intelligence** — Search, discover, and analyze companies worldwide
- **Distribution Analysis** — Quantum-weighted probability distributions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd c:\Users\USER\OneDrive\Desktop\aval_program
pip install -r requirements.txt
```

### 2. Ensure Backend is Running (Optional)

The Streamlit app can run independently, but for full integration with the Q# backend:

```bash
# In another terminal
uvicorn aval_backend:app --host 0.0.0.0 --port 8000
```

### 3. Run Streamlit App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📄 Application Structure

```
aval_program/
├── app.py                          # Main entry point
├── utils.py                        # Utility functions
├── companies.json                  # Hierarchical company dataset
├── requirements.txt                # Python dependencies
│
├── pages/
│   ├── 1_Global_Company_Navigator.py   # Page 1: Hierarchical navigation
│   ├── 2_Quantum_Simulator.py          # Page 2: Quantum simulations
│   └── 3_Company_Browser.py            # Page 3: Company search & analysis
│
└── .streamlit/
    └── config.toml                 # Streamlit configuration
```

## 📖 Pages Overview

### 🌐 Page 1: Global Company Navigator

Navigate through hierarchical company data with cascading dropdowns.

**Features:**
- Dynamic continent → country → state → city selection
- Expandable company cards with detailed information
- Real-time company count statistics
- Navigation hierarchy visualization

**How to Use:**
1. Select a continent from the first dropdown
2. Second dropdown auto-populates with countries in that continent
3. Third dropdown shows states in the selected country
4. Fourth dropdown displays cities in the selected state
5. Companies in that state are displayed below

---

### ⚛️ Page 2: Quantum Simulator Panel

Run quantum sampling and Monte Carlo simulations.

**Features:**

**Single Quantum Sample:**
- Input a branch identifier
- Click "Sample One Branch" to generate a random quantum value
- View result with timestamp

**Monte Carlo Simulation:**
- Adjust number of samples (10-1000)
- Runs random sampling simulation
- Displays statistics:
  - Mean
  - Variance
  - Standard Deviation
  - Min/Max values
- Histogram visualization of distribution

---

### 🔍 Page 3: Company Browser

Search, discover, and analyze companies with quantum distribution analysis.

**Features:**

**Company Search:**
- Text input search across all companies
- Case-insensitive matching
- Results displayed in expandable cards

**Company Profile:**
- Click "Select for Analysis" on any company
- Displays full company details (employees, sector, location, etc.)
- Shows all metadata

**Quantum Distribution:**
- Simulated quantum-weighted probability distribution
- Shows probability for each branch
- Bar chart visualization
- Distribution statistics (mean, std dev, max, min)
- Detailed probability table

**Global Statistics:**
- Company count by continent
- Company count by sector
- Employee statistics (total, average, median, max)

---

## 🔧 Configuration

### Streamlit Settings (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#0066ff"          # Accent color
backgroundColor = "#ffffff"        # Page background
secondaryBackgroundColor = "#f0f2f6"  # Container background
textColor = "#262730"             # Text color
font = "sans serif"               # Font family

[server]
port = 8501                       # Streamlit server port
headless = true                   # Run without browser auto-open
runOnSave = true                  # Reload on file changes
```

### Backend Integration

To connect to the FastAPI backend, ensure:

1. Backend is running at `http://localhost:8000`
2. Backend status is shown in the sidebar
3. Functions in `utils.py` call the backend APIs

---

## 📊 Data Format

The app uses a hierarchical JSON structure in `companies.json`:

```json
{
  "companies": [
    {
      "code": "tcs01",
      "company": "TCS",
      "continent": "Asia",
      "country": "India",
      "state": "Tamil Nadu",
      "sector": "Technology",
      "subsector": "IT Services",
      "employees": 500000
    },
    ...
  ],
  "continents": {
    "Asia": {
      "countries": {
        "India": {
          "states": {
            "Tamil Nadu": ["Chennai", "Coimbatore"],
            ...
          }
        },
        ...
      }
    },
    ...
  }
}
```

---

## 🛠️ Utility Functions (`utils.py`)

### Data Loading & Navigation

- `load_data(filepath)` — Load JSON data
- `get_continents(data)` — Get list of continents
- `get_countries(data, continent)` — Get countries in continent
- `get_states(data, continent, country)` — Get states in country
- `get_cities(data, continent, country, state)` — Get cities in state

### Company Search

- `get_all_companies(data)` — Get all companies
- `search_companies(data, query)` — Search by name
- `get_companies_in_state(data, continent, country, state)` — Get companies in location

### Quantum Simulation

- `quantum_sample_once(branch_name)` — Single quantum sample (dummy)
- `run_monte_carlo_simulation(n_samples)` — Monte Carlo simulation
- `generate_distribution(n_items)` — Generate quantum-weighted distribution

### Backend API Calls

- `call_backend_health(base_url)` — Check backend status
- `call_backend_sample(base_url)` — Sample one branch from backend
- `call_backend_sample_many(n, base_url)` — Sample multiple branches
- `call_backend_branches(company, base_url)` — Get company branches

### UI Helpers

- `display_hierarchy_card(...)` — Display selected hierarchy
- `display_company_card(company)` — Display company profile

---

## 🐛 Troubleshooting

### Streamlit App Won't Start

```bash
# Reinstall Streamlit
pip install --upgrade streamlit

# Check Python version (requires Python 3.8+)
python --version
```

### Backend Connection Issues

If backend status shows 🔴 offline:

1. Start the backend server:
   ```bash
   uvicorn aval_backend:app --host 0.0.0.0 --port 8000
   ```

2. Ensure backend is running at `http://localhost:8000`

3. Check firewall/network settings

### Companies Not Showing

1. Verify `companies.json` exists in the root directory
2. Check file is valid JSON:
   ```bash
   python -m json.tool companies.json
   ```

3. Ensure data structure matches expected format

### Data Display Issues

- Clear Streamlit cache: `streamlit cache clear`
- Restart the app: Stop terminal and run `streamlit run app.py` again

---

## 📦 Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 1.5.0+
- NumPy 1.20.0+
- Requests 2.28.0+

See `requirements.txt` for full list.

---

## 🚀 Advanced Usage

### Custom Theme

Edit `.streamlit/config.toml` to customize colors and fonts:

```toml
[theme]
primaryColor = "#FF0000"          # Change primary color
backgroundColor = "#1a1a1a"       # Dark theme background
font = "monospace"                # Use monospace font
```

### Extend with More Pages

Create new pages in the `pages/` directory following the naming convention:

```
pages/
├── 1_Global_Company_Navigator.py
├── 2_Quantum_Simulator.py
├── 3_Company_Browser.py
├── 4_New_Page.py                # Add new pages here
└── 5_Another_Page.py
```

Streamlit automatically detects and displays them in the sidebar.

### Add Backend Integration

In `utils.py`, extend the backend API functions:

```python
def call_backend_custom(endpoint: str, base_url: str = "http://localhost:8000") -> Optional[Dict]:
    """Call custom backend endpoint."""
    try:
        response = requests.get(f"{base_url}/{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None
```

Then use it in pages:

```python
result = call_backend_custom("your-endpoint")
```

---

## 📝 License

Part of the AVALYOS Quantum Computing + Analytics Platform

---

## 🔗 Related Documentation

- [Backend Documentation](./BACKEND_STATUS.md)
- [Q# Integration Guide](./PYTHON_QSHARP_INTEGRATION.md)
- [Quick Start](./QUICKSTART.md)

---

**Last Updated:** November 27, 2025  
**Version:** 1.0
