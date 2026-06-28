"""
AVALYOS - Company Structure Management System
Manages companies → branches → countries → states → cities
Connects financial sectors and subsectors
"""

import json
import os
from typing import Dict, List, Optional, Any


# ============================================================================
# DATA LOADING
# ============================================================================

def load_companies() -> Dict[str, Any]:
    """
    Load companies data from JSON file.
    
    Returns:
        Dictionary containing all companies and their branches.
    
    Raises:
        FileNotFoundError: If companies.json is not found.
        json.JSONDecodeError: If JSON is malformed.
    """
    file_path = "companies.json"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: {file_path} not found in current directory.")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extract companies from the new hierarchical structure
        if "companies" in data:
            return data["companies"]
        return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error parsing JSON: {str(e)}", e.doc, e.pos)


# ============================================================================
# SEARCH FUNCTIONS
# ============================================================================

def search_company(companies: Dict, name: str) -> Optional[Dict]:
    """
    Search for a company by name (case-insensitive).
    
    Args:
        companies: The companies dictionary
        name: Company name to search for
    
    Returns:
        Company object if found, None otherwise
    """
    name_lower = name.lower().strip()
    
    for company_name, company_data in companies.items():
        if company_name.lower() == name_lower:
            print(f"\n{'='*70}")
            print(f"COMPANY FOUND: {company_name}")
            print(f"Code: {company_data['code']}")
            print(f"{'='*70}")
            print(f"\nBranches ({len(company_data['branches'])}):")
            print("-" * 70)
            
            for branch_code, branch_info in company_data['branches'].items():
                print(f"  • {branch_code}: {branch_info['name']}")
                print(f"    Location: {branch_info['city']}, {branch_info['country']}")
                print(f"    Employees: {branch_info['employees']}")
                print(f"    Sector: {branch_info['sector']} → {branch_info['subsector']}")
            
            print("-" * 70)
            return company_data
    
    print(f"\n  Company '{name}' not found.")
    return None


def search_by_sector(companies: Dict, sector: str) -> List[Dict]:
    """
    Find all companies operating in a specific sector.
    
    Args:
        companies: The companies dictionary
        sector: Sector name to search for
    
    Returns:
        List of branches matching the sector
    """
    sector_lower = sector.lower().strip()
    matching_branches = []
    
    for company_name, company_data in companies.items():
        for branch_code, branch_info in company_data['branches'].items():
            if branch_info['sector'].lower() == sector_lower:
                matching_branches.append({
                    'company': company_name,
                    'company_code': company_data['code'],
                    'branch_code': branch_code,
                    'branch_info': branch_info
                })
    
    if not matching_branches:
        print(f"\n⚠️  No branches found in sector '{sector}'.")
        return []
    
    print(f"\n{'='*70}")
    print(f"BRANCHES IN SECTOR: {sector.upper()}")
    print(f"{'='*70}")
    print(f"Total matches: {len(matching_branches)}\n")
    
    for item in matching_branches:
        print(f"Company: {item['company']} ({item['company_code']})")
        print(f"  Branch: {item['branch_code']} - {item['branch_info']['name']}")
        print(f"  Location: {item['branch_info']['city']}, {item['branch_info']['country']}")
        print(f"  Subsector: {item['branch_info']['subsector']}")
        print(f"  Employees: {item['branch_info']['employees']}")
        print()
    
    return matching_branches


def branch_details(companies: Dict, company_name: str, branch_code: str) -> Optional[Dict]:
    """
    Get detailed information about a specific branch.
    
    Args:
        companies: The companies dictionary
        company_name: Name of the company
        branch_code: Branch code (e.g., 'ms01')
    
    Returns:
        Branch details dictionary if found, None otherwise
    """
    company_name_lower = company_name.lower().strip()
    
    for company, company_data in companies.items():
        if company.lower() == company_name_lower:
            if branch_code in company_data['branches']:
                branch_info = company_data['branches'][branch_code]
                
                print(f"\n{'='*70}")
                print(f"BRANCH DETAILS")
                print(f"{'='*70}")
                print(f"Company: {company} ({company_data['code']})")
                print(f"Branch Code: {branch_code}")
                print(f"Branch Name: {branch_info['name']}")
                print(f"{'='*70}\n")
                
                print(f"Location Information:")
                print(f"  Continent: {branch_info['continent']}")
                print(f"  Country: {branch_info['country']}")
                if branch_info['state']:
                    print(f"  State: {branch_info['state']}")
                print(f"  City: {branch_info['city']}")
                
                print(f"\nOrganization Details:")
                print(f"  Employees: {branch_info['employees']}")
                
                print(f"\nIndustry Details:")
                print(f"  Sector: {branch_info['sector']}")
                print(f"  Subsector: {branch_info['subsector']}")
                
                print(f"\nDescription:")
                print(f"  {branch_info['description']}")
                print(f"\n{'='*70}\n")
                
                return branch_info
            else:
                print(f"\n⚠️  Branch code '{branch_code}' not found in {company}.")
                return None
    
    print(f"\n⚠️  Company '{company_name}' not found.")
    return None


# ============================================================================
# GEOGRAPHIC FUNCTIONS
# ============================================================================

def list_continents(companies: Dict) -> List[str]:
    """
    List all continents with branches.
    
    Args:
        companies: The companies dictionary
    
    Returns:
        Sorted list of continents
    """
    continents = set()
    
    for company_data in companies.values():
        for branch_info in company_data['branches'].values():
            continents.add(branch_info['continent'])
    
    continents_sorted = sorted(list(continents))
    
    print(f"\n{'='*70}")
    print(f"CONTINENTS WITH BRANCHES")
    print(f"{'='*70}")
    print(f"Total: {len(continents_sorted)}\n")
    
    for i, continent in enumerate(continents_sorted, 1):
        print(f"  {i}. {continent}")
    
    print()
    
    return continents_sorted


def list_countries(companies: Dict, continent: str) -> List[str]:
    """
    List all countries in a specific continent.
    
    Args:
        companies: The companies dictionary
        continent: Continent name
    
    Returns:
        Sorted list of countries
    """
    continent_lower = continent.lower().strip()
    countries = set()
    
    for company_data in companies.values():
        for branch_info in company_data['branches'].values():
            if branch_info['continent'].lower() == continent_lower:
                countries.add(branch_info['country'])
    
    if not countries:
        print(f"\n⚠️  No countries found in continent '{continent}'.")
        return []
    
    countries_sorted = sorted(list(countries))
    
    print(f"\n{'='*70}")
    print(f"COUNTRIES IN {continent.upper()}")
    print(f"{'='*70}")
    print(f"Total: {len(countries_sorted)}\n")
    
    for i, country in enumerate(countries_sorted, 1):
        print(f"  {i}. {country}")
    
    print()
    
    return countries_sorted


def list_states(companies: Dict, country: str) -> List[Optional[str]]:
    """
    List all states in a specific country that have branches.
    
    Args:
        companies: The companies dictionary
        country: Country name
    
    Returns:
        Sorted list of states (None for countries without states)
    """
    country_lower = country.lower().strip()
    states = set()
    
    for company_data in companies.values():
        for branch_info in company_data['branches'].values():
            if branch_info['country'].lower() == country_lower:
                if branch_info['state']:
                    states.add(branch_info['state'])
    
    if not states:
        print(f"\n⚠️  No state information found for '{country}'.")
        return []
    
    states_sorted = sorted(list(states))
    
    print(f"\n{'='*70}")
    print(f"STATES IN {country.upper()}")
    print(f"{'='*70}")
    print(f"Total: {len(states_sorted)}\n")
    
    for i, state in enumerate(states_sorted, 1):
        print(f"  {i}. {state}")
    
    print()
    
    return states_sorted


# ============================================================================
# INTERACTIVE MENU SYSTEM
# ============================================================================

def display_main_menu():
    """Display the main menu options."""
    print(f"\n{'='*70}")
    print(f"AVALYOS - Company Structure Management System")
    print(f"{'='*70}")
    print("\nWhat would you like to do?\n")
    print("  1. Search for a company by name")
    print("  2. Search branches by sector")
    print("  3. List all continents")
    print("  4. View countries in a continent")
    print("  5. View states in a country")
    print("  6. View branch details")
    print("  0. Exit\n")


def get_valid_choice(prompt: str, valid_options: List[str]) -> str:
    """
    Get a valid choice from user input.
    
    Args:
        prompt: Prompt to display
        valid_options: List of valid options
    
    Returns:
        User's valid choice
    """
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_options:
            return choice
        print(f"⚠️  Invalid choice. Please choose from: {', '.join(valid_options)}")


def menu_search_company(companies: Dict):
    """Interactive menu for company search."""
    company_name = input("\nEnter company name: ").strip()
    if not company_name:
        print("⚠️  Company name cannot be empty.")
        return
    
    search_company(companies, company_name)


def menu_search_by_sector(companies: Dict):
    """Interactive menu for sector search."""
    # Gather all unique sectors
    sectors = set()
    for company_data in companies.values():
        for branch_info in company_data['branches'].values():
            sectors.add(branch_info['sector'])
    
    sectors_sorted = sorted(list(sectors))
    
    if not sectors_sorted:
        print("\n⚠️  No sectors found.")
        return
    
    print(f"\nAvailable sectors:")
    for i, sector in enumerate(sectors_sorted, 1):
        print(f"  {i}. {sector}")
    
    try:
        choice = int(input("\nSelect a sector number: ")) - 1
        if 0 <= choice < len(sectors_sorted):
            search_by_sector(companies, sectors_sorted[choice])
        else:
            print("⚠️  Invalid selection.")
    except ValueError:
        print("⚠️  Please enter a valid number.")


def menu_list_continents(companies: Dict):
    """Interactive menu for listing continents."""
    continents = list_continents(companies)
    return continents


def menu_list_countries(companies: Dict):
    """Interactive menu for listing countries in a continent."""
    continents = list_continents(companies)
    
    if not continents:
        return
    
    try:
        choice = int(input("Select a continent number: ")) - 1
        if 0 <= choice < len(continents):
            list_countries(companies, continents[choice])
        else:
            print("⚠️  Invalid selection.")
    except ValueError:
        print("⚠️  Please enter a valid number.")


def menu_list_states(companies: Dict):
    """Interactive menu for listing states in a country."""
    continents = list_continents(companies)
    
    if not continents:
        return
    
    try:
        continent_choice = int(input("Select a continent number: ")) - 1
        if 0 <= continent_choice < len(continents):
            countries = list_countries(companies, continents[continent_choice])
            
            if countries:
                try:
                    country_choice = int(input("Select a country number: ")) - 1
                    if 0 <= country_choice < len(countries):
                        list_states(companies, countries[country_choice])
                    else:
                        print("⚠️  Invalid selection.")
                except ValueError:
                    print("⚠️  Please enter a valid number.")
        else:
            print("⚠️  Invalid selection.")
    except ValueError:
        print("⚠️  Please enter a valid number.")


def menu_view_branch_details(companies: Dict):
    """Interactive menu for viewing branch details."""
    # List all companies
    company_names = sorted(list(companies.keys()))
    
    print(f"\nAvailable companies:")
    for i, company in enumerate(company_names, 1):
        print(f"  {i}. {company}")
    
    try:
        company_choice = int(input("\nSelect a company number: ")) - 1
        if 0 <= company_choice < len(company_names):
            selected_company = company_names[company_choice]
            company_data = companies[selected_company]
            
            # List branches
            branch_codes = sorted(list(company_data['branches'].keys()))
            print(f"\nBranches in {selected_company}:")
            for i, branch_code in enumerate(branch_codes, 1):
                branch_name = company_data['branches'][branch_code]['name']
                print(f"  {i}. {branch_code}: {branch_name}")
            
            try:
                branch_choice = int(input("\nSelect a branch number: ")) - 1
                if 0 <= branch_choice < len(branch_codes):
                    selected_branch = branch_codes[branch_choice]
                    branch_details(companies, selected_company, selected_branch)
                else:
                    print("⚠️  Invalid selection.")
            except ValueError:
                print("⚠️  Please enter a valid number.")
        else:
            print("⚠️  Invalid selection.")
    except ValueError:
        print("⚠️  Please enter a valid number.")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program loop."""
    try:
        # Load companies data
        companies = load_companies()
        print("\n✓ Companies data loaded successfully!")
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"\n❌ {str(e)}")
        print("Please ensure companies.json exists and is valid JSON.")
        return
    
    # Main loop
    while True:
        display_main_menu()
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Thank you for using AVALYOS. Goodbye!\n")
            break
        
        elif choice == "1":
            menu_search_company(companies)
        
        elif choice == "2":
            menu_search_by_sector(companies)
        
        elif choice == "3":
            menu_list_continents(companies)
        
        elif choice == "4":
            menu_list_countries(companies)
        
        elif choice == "5":
            menu_list_states(companies)
        
        elif choice == "6":
            menu_view_branch_details(companies)
        
        else:
            print("⚠️  Invalid choice. Please select a valid option.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
