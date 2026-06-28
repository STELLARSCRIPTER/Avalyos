"""
Database Setup & Management Script for AVALYOS

This script helps set up and manage PostgreSQL and MongoDB databases.
"""

import json
import os
import sys


def setup_postgres():
    """
    Setup PostgreSQL database.
    
    Steps:
    1. Create a PostgreSQL user and database
    2. Initialize tables using SQLAlchemy ORM
    3. Set connection string as environment variable
    """
    print("\n" + "=" * 60)
    print("📊 PostgreSQL Setup")
    print("=" * 60)
    
    print("\n📝 Instructions for PostgreSQL setup:")
    print("""
    1. Install PostgreSQL (if not already installed)
       - Windows: Download from https://www.postgresql.org/download/windows/
       - macOS: brew install postgresql@15
       - Linux: sudo apt-get install postgresql postgresql-contrib
    
    2. Start PostgreSQL service
       - Windows: Start PostgreSQL from Services
       - macOS/Linux: brew services start postgresql OR sudo systemctl start postgresql
    
    3. Create database and user:
       psql -U postgres
       
       CREATE USER avalyos WITH PASSWORD 'avalyos_password';
       CREATE DATABASE avalyos_db OWNER avalyos;
       GRANT ALL PRIVILEGES ON DATABASE avalyos_db TO avalyos;
       \\c avalyos_db
       GRANT ALL ON SCHEMA public TO avalyos;
       
    4. Set environment variable:
       Windows (PowerShell):
       $env:DATABASE_URL = "postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db"
       
       Linux/macOS:
       export DATABASE_URL="postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db"
    
    5. Run this script to initialize tables
    """)
    
    response = input("\nHave you completed PostgreSQL setup? (yes/no): ").strip().lower()
    
    if response == "yes":
        try:
            from database_models import init_postgres_db
            init_postgres_db()
            print("✅ PostgreSQL initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing PostgreSQL: {e}")
            return False
    else:
        print("⏭️  Skipping PostgreSQL setup")
        return False


def setup_mongodb():
    """
    Setup MongoDB database.
    
    Steps:
    1. Install MongoDB
    2. Create database and collections
    3. Set connection string as environment variable
    """
    print("\n" + "=" * 60)
    print("🍃 MongoDB Setup")
    print("=" * 60)
    
    print("\n📝 Instructions for MongoDB setup:")
    print("""
    1. Install MongoDB (if not already installed)
       - Windows: Download from https://www.mongodb.com/try/download/community
       - macOS: brew install mongodb-community
       - Linux: Follow official MongoDB installation guide
    
    2. Install MongoDB Python driver:
       pip install pymongo
    
    3. Start MongoDB service
       - Windows: mongod (from MongoDB bin folder)
       - macOS: brew services start mongodb-community
       - Linux: sudo systemctl start mongod
    
    4. Create database and user (optional, MongoDB creates them on first write):
       mongosh
       use avalyos_db
       db.createUser({
         user: "avalyos",
         pwd: "avalyos_password",
         roles: ["readWrite"]
       })
    
    5. Set environment variable:
       Windows (PowerShell):
       $env:MONGODB_URI = "mongodb://avalyos:avalyos_password@localhost:27017/avalyos_db"
       
       Linux/macOS:
       export MONGODB_URI="mongodb://avalyos:avalyos_password@localhost:27017/avalyos_db"
    
    6. Run this script to initialize collections
    """)
    
    response = input("\nHave you completed MongoDB setup? (yes/no): ").strip().lower()
    
    if response == "yes":
        try:
            from database_models import init_mongodb_collections
            init_mongodb_collections()
            print("✅ MongoDB initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing MongoDB: {e}")
            return False
    else:
        print("⏭️  Skipping MongoDB setup")
        return False


def load_companies_to_databases():
    """
    Load company data from companies.json into both databases.
    """
    print("\n" + "=" * 60)
    print("📦 Loading Company Data into Databases")
    print("=" * 60)
    
    # Check if companies.json exists
    if not os.path.exists("companies.json"):
        print("❌ companies.json not found. Generate it first:")
        print("   python generate_database.py")
        return False
    
    print("\n📖 Loading companies.json...")
    
    try:
        with open("companies.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading companies.json: {e}")
        return False
    
    # Load into MongoDB
    print("\n🍃 Loading data into MongoDB...")
    try:
        from database_models import MongoDBManager
        mongo = MongoDBManager()
        
        if mongo.db:
            # Load companies
            companies_data = data.get("companies", {})
            for company_name, company_info in companies_data.items():
                company_doc = {
                    "name": company_name,
                    "code": company_info.get("code"),
                    "sector": company_info.get("sector"),
                    "subsector": company_info.get("subsector"),
                    "description": company_info.get("description"),
                }
                mongo.db.companies.insert_one(company_doc)
                
                # Load branches
                branches = company_info.get("branches", {})
                for branch_code, branch_info in branches.items():
                    branch_doc = {
                        "code": branch_code,
                        "name": branch_info.get("name"),
                        "company_name": company_name,
                        "company_code": company_info.get("code"),
                        "continent": branch_info.get("continent"),
                        "country": branch_info.get("country"),
                        "state": branch_info.get("state"),
                        "city": branch_info.get("city"),
                        "employees": branch_info.get("employees"),
                        "sector": branch_info.get("sector"),
                        "subsector": branch_info.get("subsector"),
                        "description": branch_info.get("description"),
                    }
                    mongo.db.branches.insert_one(branch_doc)
            
            print(f"✅ Loaded {len(companies_data)} companies to MongoDB")
            total_branches = sum(
                len(c.get("branches", {})) for c in companies_data.values()
            )
            print(f"✅ Loaded {total_branches} branches to MongoDB")
        else:
            print("⚠️  MongoDB not available")
    except Exception as e:
        print(f"⚠️  Error loading to MongoDB: {e}")
    
    # Load into PostgreSQL (optional, just store summary)
    print("\n🐘 Loading analytics to PostgreSQL...")
    try:
        from database_models import get_session, CompanyAnalytics
        import uuid
        
        session = get_session()
        companies_data = data.get("companies", {})
        
        for company_name, company_info in companies_data.items():
            branches = company_info.get("branches", {})
            for branch_code, branch_info in branches.items():
                analytics = CompanyAnalytics(
                    id=str(uuid.uuid4()),
                    company_name=company_name,
                    branch_code=branch_code,
                    continent=branch_info.get("continent"),
                    country=branch_info.get("country"),
                    state=branch_info.get("state"),
                    city=branch_info.get("city"),
                    employee_count=branch_info.get("employees"),
                    sector=branch_info.get("sector"),
                )
                session.add(analytics)
        
        session.commit()
        session.close()
        
        total_branches = sum(
            len(c.get("branches", {})) for c in companies_data.values()
        )
        print(f"✅ Loaded {total_branches} analytics records to PostgreSQL")
    except Exception as e:
        print(f"⚠️  Error loading to PostgreSQL: {e}")
    
    return True


def main():
    """Main setup wizard."""
    print("\n" + "=" * 60)
    print("🚀 AVALYOS Database Setup Wizard")
    print("=" * 60)
    
    print("\nThis wizard will help you set up:")
    print("  1. PostgreSQL (user actions & analytics)")
    print("  2. MongoDB (company data)")
    print("  3. Load company data into both databases")
    
    # Step 1: Generate database
    print("\n" + "-" * 60)
    print("STEP 1: Generate Company Database")
    print("-" * 60)
    
    if os.path.exists("companies.json"):
        print("✅ companies.json already exists")
        response = input("Regenerate? (yes/no): ").strip().lower()
        if response == "yes":
            try:
                from generate_database import generate_companies_database, save_database
                print("\n🔄 Generating database...")
                database = generate_companies_database()
                save_database(database)
            except Exception as e:
                print(f"❌ Error generating database: {e}")
    else:
        print("⚠️  companies.json not found")
        response = input("Generate it now? (yes/no): ").strip().lower()
        if response == "yes":
            try:
                from generate_database import generate_companies_database, save_database
                print("\n🔄 Generating database...")
                database = generate_companies_database()
                save_database(database)
            except Exception as e:
                print(f"❌ Error generating database: {e}")
    
    # Step 2: PostgreSQL setup
    print("\n" + "-" * 60)
    print("STEP 2: PostgreSQL Setup")
    print("-" * 60)
    postgres_ok = setup_postgres()
    
    # Step 3: MongoDB setup
    print("\n" + "-" * 60)
    print("STEP 3: MongoDB Setup")
    print("-" * 60)
    mongodb_ok = setup_mongodb()
    
    # Step 4: Load data
    print("\n" + "-" * 60)
    print("STEP 4: Load Data into Databases")
    print("-" * 60)
    
    if postgres_ok or mongodb_ok:
        response = input("\nLoad company data? (yes/no): ").strip().lower()
        if response == "yes":
            load_companies_to_databases()
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Setup Complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Run Streamlit app: streamlit run app.py")
    print("  2. Run FastAPI backend: uvicorn aval_backend:app")
    print("  3. Access Streamlit at: http://localhost:8501")
    print("  4. Access API at: http://localhost:8000")
    
    print("\nEnvironment variables configured:")
    if postgres_ok:
        print("  ✅ DATABASE_URL (PostgreSQL)")
    if mongodb_ok:
        print("  ✅ MONGODB_URI (MongoDB)")
    
    print("\n🎉 AVALYOS is ready to use!")


if __name__ == "__main__":
    main()
