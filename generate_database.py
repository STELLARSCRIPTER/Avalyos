"""
Generate comprehensive hierarchical database for AVALYOS
Structure: Continents → Countries → States → Companies → Branches

This script generates a complete JSON database with realistic company data.
"""

import json
import os
from typing import Dict, List, Any
import random


# ============================================================================
# CONTINENT, COUNTRY, STATE DATA
# ============================================================================

GEOGRAPHY_DATA = {
    "Asia": {
        "India": {
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
            "Karnataka": ["Bangalore", "Mysuru", "Mangalore", "Belgaum"],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Aurangabad"],
            "Telangana": ["Hyderabad", "Secunderabad", "Warangal", "Nizamabad"],
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
            "Uttar Pradesh": ["Delhi", "Noida", "Lucknow", "Kanpur"],
        },
        "China": {
            "Shanghai": ["Shanghai", "Pudong", "Huangpu", "Minhang"],
            "Beijing": ["Beijing", "Chaoyang", "Haidian", "Dongcheng"],
            "Guangdong": ["Shenzhen", "Guangzhou", "Foshan", "Zhuhai"],
            "Zhejiang": ["Hangzhou", "Ningbo", "Jiaxing", "Huzhou"],
        },
        "Japan": {
            "Tokyo": ["Tokyo", "Shibuya", "Shinjuku", "Minato"],
            "Osaka": ["Osaka", "Kobe", "Kyoto", "Kobe"],
            "Kanagawa": ["Yokohama", "Kawasaki", "Sagamihara"],
        },
        "Singapore": {
            "Central": ["Singapore", "Marina Bay", "Raffles"],
            "East": ["Changi", "Bedok", "Pasir Ris"],
            "West": ["Jurong", "Clementi", "Bukit Batok"],
        },
        "South Korea": {
            "Seoul": ["Seoul", "Gangnam", "Songpa", "Jung"],
            "Gyeonggi": ["Suwon", "Incheon", "Seongnam"],
            "Busan": ["Busan", "Haeundae", "Seo-gu"],
        },
    },
    "Europe": {
        "United Kingdom": {
            "England": ["London", "Manchester", "Birmingham", "Liverpool"],
            "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee"],
            "Wales": ["Cardiff", "Swansea", "Newport"],
        },
        "Germany": {
            "Berlin": ["Berlin", "Charlottenburg", "Kreuzberg"],
            "Bavaria": ["Munich", "Nuremberg", "Augsburg"],
            "North Rhine": ["Cologne", "Düsseldorf", "Dortmund"],
            "Hamburg": ["Hamburg", "Altona", "Wandsbek"],
        },
        "France": {
            "Île-de-France": ["Paris", "Versailles", "Boulogne"],
            "Provence": ["Marseille", "Aix-en-Provence", "Nice"],
            "Auvergne": ["Lyon", "Saint-Étienne", "Grenoble"],
        },
        "Netherlands": {
            "North Holland": ["Amsterdam", "Haarlem", "Zaandam"],
            "South Holland": ["Rotterdam", "The Hague", "Delft"],
        },
        "Switzerland": {
            "Zurich": ["Zurich", "Winterthur"],
            "Geneva": ["Geneva", "Lausanne", "Montreux"],
            "Basel": ["Basel", "Liestal"],
        },
    },
    "North America": {
        "United States": {
            "California": ["San Francisco", "Los Angeles", "San Diego", "Sacramento"],
            "New York": ["New York City", "Buffalo", "Rochester"],
            "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
            "Washington": ["Seattle", "Redmond", "Tacoma"],
        },
        "Canada": {
            "Ontario": ["Toronto", "Ottawa", "Hamilton"],
            "British Columbia": ["Vancouver", "Victoria", "Surrey"],
            "Quebec": ["Montreal", "Quebec City"],
        },
        "Mexico": {
            "Mexico City": ["Mexico City", "Benito Juárez"],
            "State of Mexico": ["Ecatepec", "Naucalpan"],
        },
    },
    "South America": {
        "Brazil": {
            "São Paulo": ["São Paulo", "Santos", "Campinas"],
            "Rio de Janeiro": ["Rio de Janeiro", "Niterói"],
            "Minas Gerais": ["Belo Horizonte", "Uberlândia"],
        },
        "Argentina": {
            "Buenos Aires": ["Buenos Aires", "La Plata"],
            "Córdoba": ["Córdoba", "Rosario"],
        },
        "Chile": {
            "Metropolitana": ["Santiago", "Puente Alto", "San Bernardo"],
            "Valparaíso": ["Valparaíso", "Viña del Mar"],
        },
    },
    "Africa": {
        "South Africa": {
            "Gauteng": ["Johannesburg", "Pretoria", "Soweto"],
            "Western Cape": ["Cape Town", "Stellenbosch"],
        },
        "Nigeria": {
            "Lagos": ["Lagos", "Victoria Island"],
            "Federal Capital": ["Abuja", "Gwagwalada"],
        },
        "Egypt": {
            "Cairo": ["Cairo", "Giza", "Helwan"],
            "Alexandria": ["Alexandria", "Aboukir"],
        },
    },
    "Oceania": {
        "Australia": {
            "New South Wales": ["Sydney", "Newcastle", "Wollongong"],
            "Victoria": ["Melbourne", "Geelong", "Ballarat"],
            "Queensland": ["Brisbane", "Gold Coast", "Sunshine Coast"],
        },
        "New Zealand": {
            "Auckland": ["Auckland", "Manukau"],
            "Wellington": ["Wellington", "Hutt Valley"],
        },
    },
}

# ============================================================================
# COMPANY DEFINITIONS
# ============================================================================

COMPANIES = {
    "Microsoft": {
        "code": "ms",
        "sector": "Technology",
        "subsector": "Cloud Computing",
        "description": "Global technology leader in cloud, AI, and enterprise software",
    },
    "Google": {
        "code": "gg",
        "sector": "Technology",
        "subsector": "Search & Advertising",
        "description": "World leader in search, advertising, and AI research",
    },
    "Amazon": {
        "code": "az",
        "sector": "Technology",
        "subsector": "Cloud & Retail",
        "description": "E-commerce and cloud computing giant",
    },
    "Apple": {
        "code": "ap",
        "sector": "Technology",
        "subsector": "Consumer Electronics",
        "description": "Premium consumer electronics and software company",
    },
    "Meta": {
        "code": "fb",
        "sector": "Technology",
        "subsector": "Social Media",
        "description": "Social media and metaverse platform leader",
    },
    "Tesla": {
        "code": "ts",
        "sector": "Automotive",
        "subsector": "Electric Vehicles",
        "description": "Electric vehicle and renewable energy innovator",
    },
    "Toyota": {
        "code": "ty",
        "sector": "Automotive",
        "subsector": "Vehicle Manufacturing",
        "description": "World's largest automotive manufacturer",
    },
    "BMW": {
        "code": "bm",
        "sector": "Automotive",
        "subsector": "Luxury Vehicles",
        "description": "Luxury vehicle manufacturer and innovator",
    },
    "Volkswagen": {
        "code": "vw",
        "sector": "Automotive",
        "subsector": "Vehicle Manufacturing",
        "description": "Major European automotive group",
    },
    "Siemens": {
        "code": "sb",
        "sector": "Industrial",
        "subsector": "Conglomerate",
        "description": "Diversified industrial manufacturing company",
    },
    "Philips": {
        "code": "ph",
        "sector": "Healthcare",
        "subsector": "Medical Devices",
        "description": "Healthcare technology and consumer electronics",
    },
    "BASF": {
        "code": "bf",
        "sector": "Chemicals",
        "subsector": "Chemical Manufacturing",
        "description": "World's largest chemical producer",
    },
    "ASML": {
        "code": "as",
        "sector": "Technology",
        "subsector": "Semiconductor Equipment",
        "description": "Leading semiconductor equipment manufacturer",
    },
    "Samsung": {
        "code": "sg",
        "sector": "Technology",
        "subsector": "Electronics",
        "description": "Korean electronics and semiconductor giant",
    },
    "TSMC": {
        "code": "tm",
        "sector": "Technology",
        "subsector": "Semiconductor Manufacturing",
        "description": "World's leading chip foundry",
    },
    "Intel": {
        "code": "in",
        "sector": "Technology",
        "subsector": "Semiconductors",
        "description": "Microprocessor and semiconductor leader",
    },
    "NVIDIA": {
        "code": "nv",
        "sector": "Technology",
        "subsector": "AI Processors",
        "description": "AI and GPU computing leader",
    },
    "Pfizer": {
        "code": "pf",
        "sector": "Healthcare",
        "subsector": "Pharmaceuticals",
        "description": "Global pharmaceutical company",
    },
    "Johnson & Johnson": {
        "code": "jj",
        "sector": "Healthcare",
        "subsector": "Pharmaceuticals & Medical Devices",
        "description": "Diversified healthcare company",
    },
    "Roche": {
        "code": "rh",
        "sector": "Healthcare",
        "subsector": "Pharmaceuticals",
        "description": "Swiss pharmaceutical and diagnostics company",
    },
    "Unilever": {
        "code": "ul",
        "sector": "Consumer Goods",
        "subsector": "Personal Care",
        "description": "Global consumer goods company",
    },
    "Nestlé": {
        "code": "nl",
        "sector": "Food & Beverage",
        "subsector": "Food Manufacturing",
        "description": "World's largest food and beverage company",
    },
    "Coca-Cola": {
        "code": "ko",
        "sector": "Food & Beverage",
        "subsector": "Beverages",
        "description": "Global beverage leader",
    },
    "Tata Consultancy Services": {
        "code": "tcs",
        "sector": "Technology",
        "subsector": "IT Services",
        "description": "Indian IT services and consulting leader",
    },
    "Infosys": {
        "code": "infy",
        "sector": "Technology",
        "subsector": "IT Services",
        "description": "Indian IT services and digital transformation company",
    },
    "Wipro": {
        "code": "wip",
        "sector": "Technology",
        "subsector": "IT Services",
        "description": "Indian IT services company",
    },
    "Alibaba": {
        "code": "baba",
        "sector": "Technology",
        "subsector": "E-commerce",
        "description": "Chinese e-commerce and cloud leader",
    },
    "Tencent": {
        "code": "tce",
        "sector": "Technology",
        "subsector": "Internet Services",
        "description": "Chinese technology and entertainment giant",
    },
    "Huawei": {
        "code": "hw",
        "sector": "Technology",
        "subsector": "Telecom Equipment",
        "description": "Chinese telecommunications equipment company",
    },
}

# ============================================================================
# EMPLOYEE COUNTS BY COMPANY
# ============================================================================

EMPLOYEE_COUNTS = {
    "Microsoft": [12000, 8500, 5500, 4200, 2800, 6500],
    "Google": [18000, 50000, 9000, 5500, 4200, 3500],
    "Amazon": [15000, 45000, 8000, 6000, 3500, 2800],
    "Apple": [8000, 32000, 4500, 3200, 2100, 1800],
    "Meta": [6500, 28000, 3500, 2800, 1500, 1200],
    "Tesla": [5000, 22000, 2800, 1500, 900, 700],
    "Toyota": [12000, 42000, 8500, 5500, 3200, 2100],
    "BMW": [7500, 28000, 5200, 3500, 2100, 1600],
    "Volkswagen": [9000, 35000, 6500, 4200, 2500, 1800],
    "Siemens": [8000, 32000, 5500, 3500, 2200, 1600],
    "Philips": [5500, 22000, 3800, 2500, 1500, 1200],
    "BASF": [6000, 24000, 4200, 2800, 1800, 1400],
    "ASML": [3000, 12000, 1800, 1200, 800, 600],
    "Samsung": [11000, 44000, 7500, 5000, 3000, 2000],
    "TSMC": [8500, 34000, 5500, 3500, 2100, 1500],
    "Intel": [7000, 28000, 4500, 3000, 1800, 1300],
    "NVIDIA": [5500, 22000, 3200, 2100, 1300, 1000],
    "Pfizer": [4500, 18000, 2800, 1800, 1100, 900],
    "Johnson & Johnson": [5000, 20000, 3200, 2100, 1300, 1000],
    "Roche": [4200, 16800, 2400, 1600, 1000, 800],
    "Unilever": [4000, 16000, 2200, 1500, 1000, 750],
    "Nestlé": [5500, 22000, 3500, 2300, 1400, 1100],
    "Coca-Cola": [3000, 12000, 1800, 1200, 800, 600],
    "Tata Consultancy Services": [15000, 60000, 9000, 5500, 3200, 2100],
    "Infosys": [12000, 48000, 7000, 4200, 2500, 1800],
    "Wipro": [10000, 40000, 5500, 3500, 2100, 1500],
    "Alibaba": [9000, 36000, 5500, 3500, 2100, 1500],
    "Tencent": [8000, 32000, 4500, 3000, 1800, 1300],
    "Huawei": [7000, 28000, 4000, 2500, 1500, 1100],
}


# ============================================================================
# DATABASE GENERATION
# ============================================================================

def generate_companies_database() -> Dict[str, Any]:
    """
    Generate the complete hierarchical database.
    Structure:
    {
        "continents": {
            "Asia": {
                "countries": {
                    "India": {
                        "states": {
                            "Tamil Nadu": ["Chennai", "Coimbatore", ...],
                            ...
                        }
                    },
                    ...
                }
            },
            ...
        },
        "companies": {
            "Microsoft": {
                "code": "ms",
                "sector": "Technology",
                "branches": {
                    "ms01": {
                        "code": "ms01",
                        "name": "Microsoft India",
                        "continent": "Asia",
                        "country": "India",
                        "state": "Telangana",
                        "city": "Hyderabad",
                        "employees": 12000,
                        ...
                    },
                    ...
                }
            },
            ...
        }
    }
    """
    
    database = {
        "continents": {},
        "companies": {},
        "metadata": {
            "generated": True,
            "version": "1.0",
            "total_companies": len(COMPANIES),
            "total_countries": sum(
                len(countries) for countries in GEOGRAPHY_DATA.values()
            ),
        }
    }
    
    # Add geography data
    for continent, countries in GEOGRAPHY_DATA.items():
        database["continents"][continent] = {
            "countries": {
                country: {"states": states}
                for country, states in countries.items()
            }
        }
    
    # Add companies with branches
    branch_counter = {}
    
    for company_name, company_info in COMPANIES.items():
        company_code = company_info["code"]
        branch_counter[company_name] = 0
        
        database["companies"][company_name] = {
            "code": company_code,
            "sector": company_info["sector"],
            "subsector": company_info["subsector"],
            "description": company_info["description"],
            "branches": {},
        }
        
        # Distribute branches across geographies
        branch_assignments = distribute_branches(
            company_name, company_code, GEOGRAPHY_DATA, EMPLOYEE_COUNTS
        )
        
        for branch_data in branch_assignments:
            branch_id = branch_data["code"]
            database["companies"][company_name]["branches"][branch_id] = branch_data
    
    return database


def distribute_branches(
    company_name: str,
    company_code: str,
    geography: Dict[str, Any],
    employee_counts: Dict[str, List[int]],
) -> List[Dict[str, Any]]:
    """
    Distribute company branches across continents and countries.
    Each company gets 5-8 branches strategically placed.
    """
    
    branches = []
    employee_list = employee_counts.get(company_name, [5000, 15000])
    num_branches = len(employee_list)
    
    branch_num = 1
    continents_list = list(geography.keys())
    
    # Seed random for reproducibility per company
    random.seed(hash(company_name) % 2**32)
    
    # Distribute branches
    selected_locations = []
    
    for continent in continents_list:
        countries = geography[continent]
        for country, states_dict in countries.items():
            for state, cities_list in states_dict.items():
                city = random.choice(cities_list)
                selected_locations.append({
                    "continent": continent,
                    "country": country,
                    "state": state,
                    "city": city,
                })
                
                if len(selected_locations) >= num_branches:
                    break
            if len(selected_locations) >= num_branches:
                break
        if len(selected_locations) >= num_branches:
            break
    
    # Ensure we have enough locations
    while len(selected_locations) < num_branches:
        continent = random.choice(continents_list)
        country = random.choice(list(geography[continent].keys()))
        state = random.choice(list(geography[continent][country].keys()))
        city = random.choice(geography[continent][country][state])
        selected_locations.append({
            "continent": continent,
            "country": country,
            "state": state,
            "city": city,
        })
    
    # Create branch records
    for i, location in enumerate(selected_locations[:num_branches]):
        branch_code = f"{company_code}{branch_num:02d}"
        branch_name = f"{company_name} - {location['city']}"
        employees = employee_list[i] if i < len(employee_list) else 5000
        
        branches.append({
            "code": branch_code,
            "name": branch_name,
            "continent": location["continent"],
            "country": location["country"],
            "state": location["state"],
            "city": location["city"],
            "employees": employees,
            "sector": COMPANIES[company_name]["sector"],
            "subsector": COMPANIES[company_name]["subsector"],
            "description": f"{company_name} branch in {location['city']}, {location['country']}",
        })
        
        branch_num += 1
    
    return branches


def save_database(database: Dict[str, Any], filepath: str = "companies.json") -> None:
    """Save the database to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    print(f"✅ Database saved to {filepath}")
    print(f"   - Total companies: {len(database['companies'])}")
    print(f"   - Total branches: {sum(len(c.get('branches', {})) for c in database['companies'].values())}")
    print(f"   - Total continents: {len(database['continents'])}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🔄 Generating hierarchical company database...")
    database = generate_companies_database()
    save_database(database)
    print("\n✨ Database generation complete!")
