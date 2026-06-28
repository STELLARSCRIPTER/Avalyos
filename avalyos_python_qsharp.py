"""
AVALYOS Python-Q# Integration
Demonstrates calling quantum operations from Python using the qsharp package
"""

import qsharp
from typing import Dict, List


def init_quantum_environment():
    """
    Initialize the Q# quantum environment.
    Loads the compiled Q# operations from the project.
    """
    print("🔧 Initializing quantum environment...")
    try:
        # Load Q# operations from the current project
        # The qsharp module automatically discovers .qs files in the project
        qsharp.init(project_root=".")
        print("✓ Quantum environment initialized successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize quantum environment: {e}")
        print("   Make sure the Q# project is properly configured.")
        return False


def sample_branch() -> Dict[str, str]:
    """
    Calls the Q# SampleBranchWeighted() operation and returns the result.
    
    Returns:
        Dictionary containing branch information
    """
    try:
        # Call the Q# operation from Python
        # The operation returns a Branch newtype
        result = qsharp.run("AVALYOS.Quantum.SampleBranchWeighted()", shots=1)
        # With shots=1, result is a single value; extract it from the list
        if isinstance(result, list) and len(result) > 0:
            branch_obj = result[0]
        else:
            branch_obj = result
        
        # Convert Branch object to dictionary
        if hasattr(branch_obj, '__dict__'):
            return branch_obj.__dict__
        elif isinstance(branch_obj, dict):
            return branch_obj
        else:
            # Try to convert to dictionary by accessing tuple elements
            return {
                'Code': getattr(branch_obj, 'Code', str(branch_obj[0]) if len(branch_obj) > 0 else 'N/A'),
                'Company': getattr(branch_obj, 'Company', str(branch_obj[1]) if len(branch_obj) > 1 else 'N/A'),
                'Continent': getattr(branch_obj, 'Continent', str(branch_obj[2]) if len(branch_obj) > 2 else 'N/A'),
                'Country': getattr(branch_obj, 'Country', str(branch_obj[3]) if len(branch_obj) > 3 else 'N/A'),
                'State': getattr(branch_obj, 'State', str(branch_obj[4]) if len(branch_obj) > 4 else 'N/A'),
                'Sector': getattr(branch_obj, 'Sector', str(branch_obj[5]) if len(branch_obj) > 5 else 'N/A'),
                'SubSector': getattr(branch_obj, 'SubSector', str(branch_obj[6]) if len(branch_obj) > 6 else 'N/A'),
                'Employees': str(getattr(branch_obj, 'Employees', str(branch_obj[7]) if len(branch_obj) > 7 else 'N/A'))
            }
    except Exception as e:
        print(f"❌ Error calling Q# operation: {e}")
        return None


def sample_branches_multiple(num_samples: int = 5) -> List[Dict[str, str]]:
    """
    Calls the Q# sampler multiple times to collect branch samples.
    Demonstrates the Monte Carlo sampling approach.
    
    Args:
        num_samples: Number of branches to sample
        
    Returns:
        List of sampled branch dictionaries
    """
    samples = []
    print(f"🎲 Sampling {num_samples} branches using quantum weighting...\n")
    
    for i in range(num_samples):
        branch = sample_branch()
        if branch:
            samples.append(branch)
            print(f"Sample {i+1}:")
            print(f"  Code: {branch.get('Code', 'N/A')}")
            print(f"  Company: {branch.get('Company', 'N/A')}")
            print(f"  Employees: {branch.get('Employees', 'N/A')}")
            print()
    
    return samples


def display_branch_details(branch: Dict[str, str]):
    """
    Displays detailed information about a sampled branch.
    
    Args:
        branch: Branch dictionary from Q# operation
    """
    if not branch:
        print("❌ No branch data to display")
        return
    
    print("=" * 70)
    print("📊 QUANTUM-SAMPLED BRANCH DETAILS")
    print("=" * 70)
    print(f"Code:       {branch.get('Code', 'N/A')}")
    print(f"Company:    {branch.get('Company', 'N/A')}")
    print(f"Continent:  {branch.get('Continent', 'N/A')}")
    print(f"Country:    {branch.get('Country', 'N/A')}")
    print(f"State:      {branch.get('State', 'N/A')}")
    print(f"Sector:     {branch.get('Sector', 'N/A')}")
    print(f"SubSector:  {branch.get('SubSector', 'N/A')}")
    print(f"Employees:  {branch.get('Employees', 'N/A')}")
    print("=" * 70)


def analyze_sampling_distribution(samples: List[Dict[str, str]]):
    """
    Analyzes the distribution of sampled branches.
    Shows which companies were selected most frequently.
    
    Args:
        samples: List of sampled branch dictionaries
    """
    if not samples:
        print("❌ No samples to analyze")
        return
    
    # Count by company
    company_counts = {}
    sector_counts = {}
    
    for branch in samples:
        company = branch.get('Company', 'Unknown')
        sector = branch.get('Sector', 'Unknown')
        
        company_counts[company] = company_counts.get(company, 0) + 1
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    print("\n" + "=" * 70)
    print("📈 SAMPLING DISTRIBUTION ANALYSIS")
    print("=" * 70)
    
    print("\nCompanies sampled:")
    for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(samples)) * 100
        print(f"  {company:<20} {count:>2} times ({percentage:>5.1f}%)")
    
    print("\nSectors sampled:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(samples)) * 100
        print(f"  {sector:<20} {count:>2} times ({percentage:>5.1f}%)")
    
    print("=" * 70)


def main():
    """
    Main function demonstrating Python-Q# integration.
    """
    print("\n" + "=" * 70)
    print("🌍 AVALYOS - Python & Quantum Integration Demo")
    print("=" * 70 + "\n")
    
    # Initialize quantum environment
    if not init_quantum_environment():
        print("⚠️  Continuing without quantum operations (simulation mode)")
        return
    
    print("=" * 70)
    print("DEMO 1: Single Quantum Sample")
    print("=" * 70 + "\n")
    
    # Sample a single branch
    branch = sample_branch()
    if branch:
        display_branch_details(branch)
    
    print("\n" + "=" * 70)
    print("DEMO 2: Multiple Quantum Samples (Monte Carlo)")
    print("=" * 70 + "\n")
    
    # Sample multiple branches to see distribution
    samples = sample_branches_multiple(num_samples=10)
    
    # Analyze the distribution
    if samples:
        analyze_sampling_distribution(samples)
    
    print("\n✓ Python-Q# integration demo completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
