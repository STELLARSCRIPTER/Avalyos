"""
Page 1: Hierarchical Selection UI - Global Company Navigator
"""

import streamlit as st
from utils import (
    load_data,
    get_continents,
    get_countries,
    get_states,
    get_cities,
    get_companies_in_state,
    display_hierarchy_card,
)
from database_models import log_user_action
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Global Company Navigator",
    page_icon="🌐",
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

st.title("🌐 Global Company Navigator")
st.markdown("Navigate through the hierarchical structure of global companies.")
st.markdown("---")

# ============================================================================
# HIERARCHICAL SELECTION
# ============================================================================

st.subheader("📍 Hierarchical Selection")

col1, col2, col3, col4 = st.columns(4)

# Continent Selection
with col1:
    continents = get_continents(data)
    selected_continent = st.selectbox(
        "🌎 Continent",
        options=[""] + continents,
        index=0,
        help="Select a continent to begin navigation",
    )

# Country Selection (depends on continent)
with col2:
    countries = []
    if selected_continent:
        countries = get_countries(data, selected_continent)
    
    selected_country = st.selectbox(
        "🏙️ Country",
        options=[""] + countries,
        index=0,
        help="Select a country within the chosen continent",
        disabled=not selected_continent,
    )

# State Selection (depends on country)
with col3:
    states = []
    if selected_continent and selected_country:
        states = get_states(data, selected_continent, selected_country)
    
    selected_state = st.selectbox(
        "📍 State/Region",
        options=[""] + states,
        index=0,
        help="Select a state or region",
        disabled=not selected_country,
    )

# City Selection (depends on state)
with col4:
    cities = []
    if selected_continent and selected_country and selected_state:
        cities = get_cities(data, selected_continent, selected_country, selected_state)
    
    selected_city = st.selectbox(
        "🏢 City",
        options=[""] + cities,
        index=0,
        help="Select a city within the chosen state",
        disabled=not selected_state,
    )

st.markdown("---")

# ============================================================================
# DISPLAY SELECTED HIERARCHY
# ============================================================================

st.subheader("🎯 Selected Hierarchy")

if selected_continent and selected_country and selected_state and selected_city:
    display_hierarchy_card(selected_continent, selected_country, selected_state, selected_city)
    
    # Fetch companies in this location
    companies = get_companies_in_state(data, selected_continent, selected_country, selected_state)
    # Log navigation action
    try:
        log_user_action(
            action_type="navigate",
            target=f"{selected_continent}/{selected_country}/{selected_state}/{selected_city}",
            details={"company_count": len(companies)},
        )
    except Exception:
        # Logging should not break the UI
        logger.exception("Failed to log navigation action for %s/%s/%s/%s", selected_continent, selected_country, selected_state, selected_city)
    
    if companies:
        st.markdown("---")
        st.subheader(f"🏢 Companies in {selected_state}, {selected_country}")
        
        # Display companies as expandable cards
        for company in companies:
            with st.expander(
                f"🏭 {company.get('company', 'Unknown')} - {company.get('code', 'N/A')}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Code:** {company.get('code', '—')}")
                    st.write(f"**Company:** {company.get('company', '—')}")
                    st.write(f"**Sector:** {company.get('sector', '—')}")
                    st.write(f"**Subsector:** {company.get('subsector', '—')}")
                with col2:
                    st.write(f"**Employees:** {company.get('employees', '—'):,}")
                    st.write(f"**Continent:** {company.get('continent', '—')}")
                    st.write(f"**Country:** {company.get('country', '—')}")
                    st.write(f"**State:** {company.get('state', '—')}")
else:
    with st.container():
        st.info(
            "👉 **Select all fields above** (Continent → Country → State → City) to view the company hierarchy."
        )

# ============================================================================
# STATISTICS SECTION
# ============================================================================

st.markdown("---")
st.subheader("📊 Navigation Statistics")

col1, col2, col3 = st.columns(3)

continents = get_continents(data)
countries_total = 0
for continent in continents:
    countries_total += len(get_countries(data, continent))

total_companies = len(data.get("companies", []))

with col1:
    st.metric("Total Continents", len(continents))
with col2:
    st.metric("Total Countries", countries_total)
with col3:
    st.metric("Total Companies", total_companies)

st.markdown("---")

# Help section
with st.expander("❓ Help & Documentation"):
    st.markdown(
        """
        ### How to Use:
        
        1. **Select Continent** — Choose a continental region
        2. **Select Country** — The dropdown will populate based on your continent choice
        3. **Select State** — Choose a state or region within your country
        4. **Select City** — Pick a specific city
        5. **View Companies** — The system will display all companies in that state
        
        ### Dynamic Filtering:
        - Each dropdown only shows valid options based on previous selections
        - Dropdowns are disabled until a parent value is selected
        - The hierarchy follows: Continent → Country → State → City
        
        ### Expandable Cards:
        - Click on company names to expand and see detailed information
        - Information includes code, sector, number of employees, and more
        """
    )
