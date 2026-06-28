"""
Page 3: Company Browser - Search and Analyze Companies
"""

import streamlit as st
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from utils import (
    load_data,
    search_companies,
    get_all_companies,
    generate_distribution,
    display_company_card,
)
from database_models import log_user_action, log_simulation_result

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Company Browser",
    page_icon="🔍",
    layout="wide",
)

# ============================================================================
# LOAD DATA
# ============================================================================

try:
    data = load_data("companies.json")
except FileNotFoundError:
    st.error("❌ Error: companies.json not found.")
    st.stop()

# ============================================================================
# PAGE TITLE
# ============================================================================

st.title("🔍 Company Intelligence Browser")
st.markdown("Search, discover, and analyze companies worldwide.")
st.markdown("---")

# ============================================================================
# SESSION STATE
# ============================================================================

if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

# ============================================================================
# SEARCH BAR
# ============================================================================

st.subheader("🔎 Search Companies")

search_query = st.text_input(
    "Search companies by name...",
    placeholder="e.g., Tata, Microsoft, BMW...",
    help="Enter a company name to search across all continents and countries",
)

# ============================================================================
# SEARCH RESULTS
# ============================================================================

if search_query:
    results = search_companies(data, search_query)
    # Log search action (best-effort)
    try:
        log_user_action(action_type="search", target=search_query, details={"results": len(results)})
    except Exception:
        logger.exception("Failed to log search action for query=%s", search_query)
    
    if results:
        st.success(f"✅ Found {len(results)} matching company/companies")
        st.markdown("---")
        
        # Display results as clickable cards
        st.subheader("📋 Search Results")
        
        for i, company in enumerate(results):
            company_name = company.get("name", "Unknown")
            code = company.get("code", "—")
            
            # Get branches for this company
            company_full_data = data.get("companies", {}).get(company_name, {})
            branches = company_full_data.get("branches", {})
            num_branches = len(branches)
            
            # Create an expandable result
            with st.expander(
                f"🏢 {company_name} ({num_branches} branches) | Code: {code}",
                expanded=(i == 0 if len(results) <= 3 else False),
            ):
                col1, col2 = st.columns([0.6, 0.4])
                
                with col1:
                    st.markdown("#### Company Profile")
                    if branches:
                        # Get info from first branch
                        first_branch = list(branches.values())[0]
                        st.write(f"**Country:** {first_branch.get('country', '—')}")
                        st.write(f"**Continent:** {first_branch.get('continent', '—')}")
                        st.write(f"**Sector:** {first_branch.get('sector', '—')}")
                        st.write(f"**Subsector:** {first_branch.get('subsector', '—')}")
                    else:
                        st.write("No branch information available")
                
                with col2:
                    st.markdown("#### Quick Stats")
                    st.metric("Total Branches", num_branches)
                    st.metric("Code", code)
                    if branches:
                        total_employees = sum(b.get("employees", 0) for b in branches.values())
                        st.metric("Total Employees", f"{total_employees:,}")
                
                # Selection button
                if st.button(
                    "📌 Select for Analysis",
                    key=f"select_{i}",
                    use_container_width=True,
                ):
                    st.session_state.selected_company = {
                        "name": company_name,
                        "code": code,
                        "branches": branches
                    }
                    st.success(f"Selected: {company_name}")
                    # Log selection
                    try:
                        log_user_action(action_type="select", target=company_name, details={"code": code, "num_branches": num_branches})
                    except Exception:
                        logger.exception("Failed to log selection for company=%s", company_name)
    else:
        st.warning(f"❌ No companies found matching '{search_query}'")

st.markdown("---")

# ============================================================================
# SELECTED COMPANY ANALYSIS
# ============================================================================

if st.session_state.selected_company:
    company = st.session_state.selected_company
    company_name = company.get("name", "Unknown")
    code = company.get("code", "—")
    branches = company.get("branches", {})
    
    st.subheader(f"📊 Analysis: {company_name}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Company", company_name)
        st.metric("Code", code)
        if branches:
            first_branch = list(branches.values())[0]
            st.metric("Sector", first_branch.get("sector", "—"))
    
    with col2:
        if branches:
            first_branch = list(branches.values())[0]
            st.metric("Country", first_branch.get("country", "—"))
            st.metric("State", first_branch.get("state", "—"))
        total_employees = sum(b.get("employees", 0) for b in branches.values())
        st.metric("Total Employees", f"{total_employees:,}")
    
    with col3:
        st.metric("Total Branches", len(branches))
        if branches:
            first_branch = list(branches.values())[0]
            st.metric("Continent", first_branch.get("continent", "—"))
            st.metric("Subsector", first_branch.get("subsector", "—"))
    
    st.markdown("---")
    
    # ============================================================================
    # QUANTUM-WEIGHTED DISTRIBUTION
    # ============================================================================
    
    st.subheader("⚛️ Quantum-Weighted Distribution")
    st.markdown(
        "Simulated quantum-weighted probability distribution for company branches."
    )
    
    # Use actual branches
    num_branches = len(branches)
    if num_branches == 0:
        st.warning("No branches found for this company")
    else:
        branch_names = list(branches.keys())
        
        # Generate distribution
        weights, weight_array = generate_distribution(num_branches)
        
        # Create dataframe for visualization
        dist_df = pd.DataFrame({
            "Branch": branch_names,
            "Probability": weights,
        })
        
        # Display distribution chart
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            st.markdown("#### Distribution Chart")
            st.bar_chart(data=dist_df.set_index("Branch"), use_container_width=True)
        
        with col2:
            st.markdown("#### Statistics")
            st.metric("Mean Probability", f"{np.mean(weights):.6f}")
            st.metric("Std Dev", f"{np.std(weights):.6f}")
            st.metric("Max Probability", f"{max(weights):.6f}")
            st.metric("Min Probability", f"{min(weights):.6f}")
        
        st.markdown("---")
        # Log distribution generation as a simulated result (best-effort)
        try:
            # store a lightweight summary
            log_user_action(action_type="distribution", target=company_name, details={"num_branches": num_branches})
            log_simulation_result(
                simulation_type="distribution_sim",
                company=company_name,
                branch="",
                n_samples=num_branches,
                results={"weights": [float(w) for w in weights]},
            )
        except Exception:
            logger.exception("Failed to log distribution simulation for company=%s", company_name)
        
        # Distribution table
        with st.expander("📊 Detailed Distribution Table"):
            st.dataframe(
                dist_df.assign(**{"Probability (%)": (dist_df["Probability"] * 100).round(2)}),
                use_container_width=True,
                hide_index=True,
            )
        
        st.markdown("---")
        
        # Branches table
        with st.expander("🏢 All Branches"):
            branches_list = []
            for branch_code, branch_data in branches.items():
                branches_list.append({
                    "Code": branch_code,
                    "Name": branch_data.get("name", "—"),
                    "City": branch_data.get("city", "—"),
                    "State": branch_data.get("state", "—"),
                    "Country": branch_data.get("country", "—"),
                    "Employees": branch_data.get("employees", 0),
                })
            branches_df = pd.DataFrame(branches_list)
            st.dataframe(branches_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Full company data (JSON view)
        with st.expander("📋 Full Company Data (JSON)"):
            st.json(company)

else:
    with st.container():
        st.info("👆 **Search for a company** and select it to view detailed analysis and quantum distribution.")

st.markdown("---")

# ============================================================================
# GLOBAL COMPANY STATISTICS
# ============================================================================

st.subheader("📈 Global Company Statistics")

all_companies = get_all_companies(data)

# Company count
st.metric("Total Companies", len(all_companies))

# Get detailed stats from branches
companies_by_continent = {}
companies_by_sector = {}
companies_by_country = {}
total_employees = 0
total_branches = 0

for company_name, company_data in data.get("companies", {}).items():
    branches = company_data.get("branches", {})
    for branch_code, branch_data in branches.items():
        continent = branch_data.get("continent", "Unknown")
        sector = branch_data.get("sector", "Unknown")
        country = branch_data.get("country", "Unknown")
        employees = branch_data.get("employees", 0)
        
        companies_by_continent[continent] = companies_by_continent.get(continent, 0) + 1
        companies_by_sector[sector] = companies_by_sector.get(sector, 0) + 1
        companies_by_country[country] = companies_by_country.get(country, 0) + 1
        total_employees += employees
        total_branches += 1

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Branches", total_branches)
with col2:
    st.metric("Total Employees", f"{total_employees:,}")
with col3:
    st.metric("Avg Employees/Branch", f"{int(total_employees / max(1, total_branches)):,}")
with col4:
    st.metric("Continents Covered", len(companies_by_continent))

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Branches by Continent")
    continent_df = pd.DataFrame(
        list(companies_by_continent.items()),
        columns=["Continent", "Count"],
    ).sort_values("Count", ascending=False)
    st.bar_chart(data=continent_df.set_index("Continent"), use_container_width=True)

with col2:
    st.markdown("#### Branches by Sector")
    sector_df = pd.DataFrame(
        list(companies_by_sector.items()),
        columns=["Sector", "Count"],
    ).sort_values("Count", ascending=False)
    st.bar_chart(data=sector_df.set_index("Sector"), use_container_width=True)

st.markdown("---")

st.subheader("🌍 Branches by Top Countries")
country_df = pd.DataFrame(
    list(companies_by_country.items()),
    columns=["Country", "Branches"],
).sort_values("Branches", ascending=False).head(10)
st.bar_chart(data=country_df.set_index("Country"), use_container_width=True)

st.markdown("---")

# ============================================================================
# HELP & DOCUMENTATION
# ============================================================================

with st.expander("❓ Help & Features"):
    st.markdown(
        """
        ### Features:
        
        **🔎 Search**
        - Search companies by name across all continents and countries
        - Results show company name, country, and sector
        
        **📌 Select Company**
        - Click "Select for Analysis" to view detailed information
        - Displays location, employees, code, and sector information
        
        **⚛️ Quantum Distribution**
        - Simulated quantum-weighted probability distribution
        - Shows likely branch locations based on quantum weighting
        - Visualized as bar chart and probability table
        
        **📊 Global Statistics**
        - Company count by continent and sector
        - Employee count statistics
        - Useful for understanding global business distribution
        
        ### Tips:
        
        - Start with a partial company name (e.g., "Tata" instead of "Tata Consultancy")
        - Search is case-insensitive
        - Select a company to see its quantum distribution
        - Check global statistics to identify business trends
        """
    )
