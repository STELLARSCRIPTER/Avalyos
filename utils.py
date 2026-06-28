"""
Utility functions for AVALYOS Streamlit Application
"""
import json
import os
from typing import Dict, List, Any, Optional
import requests
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA LOADING & TRANSFORMATION
# ============================================================================

def load_data(filepath: str = "companies.json") -> Dict[str, Any]:
    """Load hierarchical company data from JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_continents(data: Dict[str, Any]) -> List[str]:
    """Get list of continents from data."""
    if "continents" in data:
        return sorted(list(data["continents"].keys()))
    return []


def get_countries(data: Dict[str, Any], continent: str) -> List[str]:
    """Get countries for a given continent."""
    try:
        if "continents" in data and continent in data["continents"]:
            countries = data["continents"][continent].get("countries", {})
            return sorted(list(countries.keys()))
    except Exception:
        logger.exception("get_countries failed for continent=%s", continent)
    return []


def get_states(data: Dict[str, Any], continent: str, country: str) -> List[str]:
    """Get states for a given continent and country."""
    try:
        if (
            "continents" in data
            and continent in data["continents"]
            and "countries" in data["continents"][continent]
        ):
            countries = data["continents"][continent]["countries"]
            if country in countries and "states" in countries[country]:
                states = countries[country]["states"]
                return sorted(list(states.keys()))
    except Exception:
        logger.exception("get_states failed for continent=%s country=%s", continent, country)
    return []


def get_cities(
    data: Dict[str, Any], continent: str, country: str, state: str
) -> List[str]:
    """Get cities for a given continent, country, and state."""
    try:
        if (
            "continents" in data
            and continent in data["continents"]
            and "countries" in data["continents"][continent]
        ):
            countries = data["continents"][continent]["countries"]
            if country in countries and "states" in countries[country]:
                states = countries[country]["states"]
                if state in states:
                    cities = states[state]
                    return sorted(list(cities)) if isinstance(cities, list) else []
    except Exception:
        logger.exception("get_cities failed for %s/%s/%s", continent, country, state)
    return []


# ============================================================================
# COMPANY SEARCH & RETRIEVAL
# ============================================================================

def get_all_companies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all branch records from the hierarchical companies dataset."""
    companies: List[Dict[str, Any]] = []
    if "companies" not in data:
        return companies

    for company_name, company_data in data["companies"].items():
        if not isinstance(company_data, dict):
            continue
        nested = company_data.get("branches")
        if isinstance(nested, dict):
            for branch in nested.values():
                if not isinstance(branch, dict):
                    continue
                companies.append({
                    "name": company_name,
                    "company": company_name,
                    "code": branch.get("code", company_data.get("code", "")),
                    "continent": branch.get("continent", ""),
                    "country": branch.get("country", ""),
                    "state": branch.get("state", ""),
                    "city": branch.get("city", ""),
                    "sector": branch.get("sector", company_data.get("sector", "")),
                    "subsector": branch.get("subsector", company_data.get("subsector", "")),
                    "employees": branch.get("employees", 0),
                    "branch_name": branch.get("name", ""),
                })
        else:
            companies.append({
                "name": company_name,
                "company": company_name,
                "code": company_data.get("code", ""),
                "continent": company_data.get("continent", ""),
                "country": company_data.get("country", ""),
                "state": company_data.get("state", ""),
                "city": company_data.get("city", ""),
                "sector": company_data.get("sector", ""),
                "subsector": company_data.get("subsector", ""),
                "employees": company_data.get("employees", 0),
                "branch_name": company_data.get("name", ""),
            })
    return companies


def search_companies(data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """Search for companies by name across all hierarchies."""
    companies = get_all_companies(data)
    query_lower = query.lower()
    results = []

    for company in companies:
        company_name = str(company.get("name", "")).lower()
        if query_lower in company_name:
            results.append(company)

    return results


def get_company_by_hierarchy(
    data: Dict[str, Any], continent: str, country: str, state: str, city: str
) -> Optional[Dict[str, Any]]:
    """Get company information by full hierarchy."""
    companies = get_all_companies(data)
    for company in companies:
        if (
            company.get("continent") == continent
            and company.get("country") == country
            and company.get("state") == state
            and company.get("city") == city
        ):
            return company
    return None


def get_companies_in_state(
    data: Dict[str, Any], continent: str, country: str, state: str
) -> List[Dict[str, Any]]:
    """Get all companies in a specific state."""
    companies = get_all_companies(data)
    results = []
    for company in companies:
        if (
            company.get("continent") == continent
            and company.get("country") == country
            and company.get("state") == state
        ):
            results.append(company)
    return results


# ============================================================================
# BACKEND API CALLS
# ============================================================================

def call_backend_health(base_url: str = "http://localhost:8000") -> bool:
    """Check backend health."""
    # Try a small set of common local endpoints and a TCP port check as a fallback.
    import socket

    candidates = [base_url.rstrip('/')]
    # also try 127.0.0.1 variant
    if base_url.startswith("http://localhost"):
        candidates.append(base_url.replace('localhost', '127.0.0.1').rstrip('/'))

    for candidate in candidates:
        # HTTP check
        try:
            response = requests.get(f"{candidate}/", timeout=2)
            if response.status_code == 200:
                return True
        except Exception:
            # fallthrough to TCP port check below
            pass

        # TCP port probe (host:port)
        try:
            parts = candidate.split('//')[-1].split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 80
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((host, port))
            s.close()
            # port is open; assume backend reachable
            return True
        except Exception:
            continue

    logger.info("call_backend_health: backend unreachable (candidates=%s)", candidates)
    return False


def call_backend_sample(base_url: str = "http://localhost:8000") -> Optional[Dict]:
    """Call backend to sample one branch."""
    try:
        response = requests.get(f"{base_url}/sample", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        logger.exception("call_backend_sample failed against %s/sample", base_url)
    return None


def call_backend_sample_many(
    n: int, base_url: str = "http://localhost:8000"
) -> Optional[Dict]:
    """Call backend to sample many branches."""
    try:
        response = requests.get(f"{base_url}/sample/many/{n}", timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception:
        logger.exception("call_backend_sample_many failed against %s/sample/many/%s", base_url, n)
    return None


def call_backend_branches(
    company: str, base_url: str = "http://localhost:8000"
) -> Optional[List[Dict]]:
    """Call backend to get branches for a company."""
    try:
        response = requests.get(f"{base_url}/branches/{company}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        logger.exception("call_backend_branches failed against %s/branches/%s", base_url, company)
    return None


# ============================================================================
# QUANTUM SIMULATION (Dummy/Local)
# ============================================================================

def quantum_sample_once(branch_name: str) -> Dict[str, Any]:
    """Simulate a quantum sample for a single branch (dummy)."""
    import random

    return {
        "branch": branch_name,
        "quantum_value": random.random(),
        "timestamp": str(__import__("datetime").datetime.now()),
    }


def run_monte_carlo_simulation(n_samples: int = 100) -> Dict[str, Any]:
    """Run a Monte Carlo simulation with n_samples."""
    import numpy as np

    samples = np.random.random(n_samples)
    return {
        "samples": samples.tolist(),
        "mean": float(np.mean(samples)),
        "variance": float(np.var(samples)),
        "std_dev": float(np.std(samples)),
        "min": float(np.min(samples)),
        "max": float(np.max(samples)),
    }


def generate_distribution(n_items: int) -> tuple:
    """Generate a fake quantum-weighted distribution."""
    import numpy as np

    weights = np.abs(np.random.randn(n_items))
    weights = weights / weights.sum()
    return weights.tolist(), weights


# ============================================================================
# UI HELPERS
# ============================================================================

def display_hierarchy_card(continent: str, country: str, state: str, city: str):
    """Display a formatted hierarchy card."""
    import streamlit as st
    with st.container():
        st.markdown("### 📍 Selected Hierarchy")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Continent", continent or "—")
            st.metric("State", state or "—")
        with col2:
            st.metric("Country", country or "—")
            st.metric("City", city or "—")


def display_company_card(company: Dict[str, Any]):
    """Display a company profile card."""
    import streamlit as st
    with st.container():
        st.markdown(f"### 🏢 {company.get('company', 'Unknown')}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Continent:** {company.get('continent', '—')}")
            st.write(f"**State:** {company.get('state', '—')}")
            st.write(f"**Sector:** {company.get('sector', '—')}")
        with col2:
            st.write(f"**Country:** {company.get('country', '—')}")
            st.write(f"**Employees:** {company.get('employees', '—')}")
            st.write(f"**SubSector:** {company.get('subsector', '—')}")
