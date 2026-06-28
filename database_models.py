"""
Database models and initialization scripts for AVALYOS

Supports:
- PostgreSQL: Store user actions, simulation results, analytics
- MongoDB: Store branch/company hierarchical data
- Neo4j: Store company relationships (optional)
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# ============================================================================
# SQLALCHEMY BASE & SESSION
# ============================================================================

Base = declarative_base()

# PostgreSQL connection string (configure with environment variable)
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://avalyos:avalyos_password@localhost:5432/avalyos_db"
)

# Lazily create SQLAlchemy engine/session to avoid import-time DB driver errors
engine = None
SessionLocal = None


def ensure_postgres_engine() -> bool:
    """Ensure SQLAlchemy engine and sessionmaker are initialized.

    Returns True if engine/session are ready, False otherwise.
    This defers the actual DB driver import (e.g. psycopg2) until an
    operation requires DB access so the module can be imported in
    environments where DB deps aren't installed.
    """
    global engine, SessionLocal
    if engine is not None and SessionLocal is not None:
        return True

    try:
        engine = create_engine(POSTGRES_URL)
        SessionLocal = sessionmaker(bind=engine)
        return True
    except Exception as e:
        # Avoid crashing import; consumer code should handle None returns
        print(f"⚠️  Could not initialize PostgreSQL engine: {e}")
        engine = None
        SessionLocal = None
        return False


# ============================================================================
# POSTGRESQL MODELS
# ============================================================================

class UserSession(Base):
    """Track user sessions and interactions."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    page = Column(String)  # Page name: navigator, simulator, browser
    action = Column(String)  # Action taken
    details = Column(JSON)  # Additional details
    ip_address = Column(String)
    
    def __repr__(self):
        return f"<UserSession {self.id}>"


class SimulationResult(Base):
    """Store quantum simulation results."""
    __tablename__ = "simulation_results"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    simulation_type = Column(String)  # 'monte_carlo', 'single_sample', etc.
    company = Column(String)
    branch = Column(String)
    n_samples = Column(Integer)
    results = Column(JSON)  # {samples: [...], mean, variance, std_dev}
    extra_metadata = Column(JSON)  # Additional metadata
    
    def __repr__(self):
        return f"<SimulationResult {self.id}>"


class UserAction(Base):
    """Log all user actions for analytics."""
    __tablename__ = "user_actions"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    action_type = Column(String)  # 'search', 'select', 'simulate', 'download'
    target = Column(String)  # What was acted upon (company, branch, etc.)
    details = Column(JSON)
    
    def __repr__(self):
        return f"<UserAction {self.action_type} on {self.target}>"


class CompanyAnalytics(Base):
    """Store analytics about companies and branches."""
    __tablename__ = "company_analytics"
    
    id = Column(String, primary_key=True)
    company_name = Column(String)
    branch_code = Column(String)
    continent = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    employee_count = Column(Integer)
    sector = Column(String)
    total_simulations = Column(Integer, default=0)
    avg_simulation_time = Column(Float)
    last_accessed = Column(DateTime)
    extra_metadata = Column(JSON)
    
    def __repr__(self):
        return f"<CompanyAnalytics {self.company_name} - {self.branch_code}>"


# ============================================================================
# MONGODB MODELS (using PyMongo)
# ============================================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://avalyos:avalyos_password@localhost:27017/avalyos_db"
)

MONGODB_COLLECTIONS = {
    "companies": {
        "description": "Company master data with hierarchical structure",
        "indexes": ["code", "sector", "continent", "country"],
    },
    "branches": {
        "description": "Branch-level data with location and employee info",
        "indexes": ["branch_code", "company_name", "continent", "country", "city"],
    },
    "simulations": {
        "description": "Cached simulation results",
        "indexes": ["company_name", "timestamp", "simulation_type"],
    },
    "distributions": {
        "description": "Quantum-weighted probability distributions",
        "indexes": ["company_name", "branch_code", "created_at"],
    },
}


class MongoDBManager:
    """Manager for MongoDB operations."""
    
    def __init__(self, uri: str = MONGODB_URI):
        """Initialize MongoDB connection."""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(uri)
            self.db = self.client.get_default_database()
            print("✅ MongoDB connected")
        except ImportError:
            print("⚠️  PyMongo not installed. Run: pip install pymongo")
            self.client = None
            self.db = None
    
    def insert_company(self, company_data: dict) -> str:
        """Insert or update a company in MongoDB."""
        if not self.db:
            return None
        result = self.db.companies.insert_one(company_data)
        return str(result.inserted_id)
    
    def insert_branch(self, branch_data: dict) -> str:
        """Insert a branch in MongoDB."""
        if not self.db:
            return None
        result = self.db.branches.insert_one(branch_data)
        return str(result.inserted_id)
    
    def store_simulation_result(self, simulation_data: dict) -> str:
        """Store a simulation result."""
        if not self.db:
            return None
        simulation_data["timestamp"] = datetime.utcnow()
        result = self.db.simulations.insert_one(simulation_data)
        return str(result.inserted_id)
    
    def get_company(self, company_name: str) -> dict:
        """Retrieve a company by name."""
        if not self.db:
            return None
        return self.db.companies.find_one({"name": company_name})
    
    def get_branches_for_company(self, company_name: str) -> list:
        """Get all branches for a company."""
        if not self.db:
            return []
        return list(self.db.branches.find({"company_name": company_name}))
    
    def search_companies(self, query: str) -> list:
        """Search for companies by name or sector."""
        if not self.db:
            return []
        return list(
            self.db.companies.find({
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"sector": {"$regex": query, "$options": "i"}},
                ]
            })
        )
    
    def get_simulations_for_company(self, company_name: str, limit: int = 10) -> list:
        """Get recent simulations for a company."""
        if not self.db:
            return []
        return list(
            self.db.simulations.find(
                {"company_name": company_name}
            ).sort("timestamp", -1).limit(limit)
        )


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_postgres_db() -> None:
    """Initialize PostgreSQL database tables."""
    if not ensure_postgres_engine():
        print("⚠️  Skipping PostgreSQL initialization (engine unavailable)")
        return

    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL database initialized")


def init_mongodb_collections() -> None:
    """Initialize MongoDB collections and indexes."""
    mongo = MongoDBManager()
    if not mongo.db:
        print("⚠️  MongoDB not available")
        return
    
    for collection_name, config in MONGODB_COLLECTIONS.items():
        # Create collection if it doesn't exist
        if collection_name not in mongo.db.list_collection_names():
            mongo.db.create_collection(collection_name)
            print(f"✅ Created MongoDB collection: {collection_name}")
        
        # Create indexes
        collection = mongo.db[collection_name]
        for index_field in config.get("indexes", []):
            collection.create_index(index_field)
    
    print("✅ MongoDB collections and indexes initialized")


def init_all_databases() -> None:
    """Initialize all databases."""
    print("\n🔄 Initializing databases...")
    
    try:
        init_postgres_db()
    except Exception as e:
        print(f"⚠️  PostgreSQL initialization error: {e}")
    
    try:
        init_mongodb_collections()
    except Exception as e:
        print(f"⚠️  MongoDB initialization error: {e}")
    
    print("\n✨ Database initialization complete!\n")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_session():
    """Get a new database session."""
    # Ensure engine/sessionmaker are ready
    if not ensure_postgres_engine() or SessionLocal is None:
        return None
    return SessionLocal()


def log_user_action(action_type: str, target: str, user_id: str = None, details: dict = None) -> str:
    """Log a user action to PostgreSQL."""
    import uuid, json
    session = get_session()
    if session is None:
        # Fallback: write to a local JSONL file so actions are not lost
        try:
            os.makedirs("logs", exist_ok=True)
            record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "anonymous",
                "action_type": action_type,
                "target": target,
                "details": details or {}
            }
            with open(os.path.join("logs", "user_actions.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, default=str) + "\n")
            return record["id"]
        except Exception as e:
            print(f"Error writing fallback user action log: {e}")
            return None

    try:
        action = UserAction(
            id=str(uuid.uuid4()),
            user_id=user_id or "anonymous",
            action_type=action_type,
            target=target,
            details=details or {}
        )
        session.add(action)
        session.commit()
        session.close()
        return action.id
    except Exception as e:
        print(f"Error logging action: {e}")
        return None


def log_simulation_result(
    simulation_type: str,
    company: str,
    branch: str,
    n_samples: int,
    results: dict,
    metadata: dict = None
) -> str:
    """Log a simulation result to PostgreSQL."""
    import uuid, json
    session = get_session()
    if session is None:
        # Fallback: write to a local JSONL file so simulation summaries persist
        try:
            os.makedirs("logs", exist_ok=True)
            record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "simulation_type": simulation_type,
                "company": company,
                "branch": branch,
                "n_samples": n_samples,
                "results": results,
                "extra_metadata": metadata or {}
            }
            with open(os.path.join("logs", "simulations.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, default=str) + "\n")
            return record["id"]
        except Exception as e:
            print(f"Error writing fallback simulation log: {e}")
            return None

    try:
        sim = SimulationResult(
            id=str(uuid.uuid4()),
            simulation_type=simulation_type,
            company=company,
            branch=branch,
            n_samples=n_samples,
            results=results,
            extra_metadata=metadata or {}
        )
        session.add(sim)
        session.commit()
        session.close()
        return sim.id
    except Exception as e:
        print(f"Error logging simulation: {e}")
        return None


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 AVALYOS Database Setup")
    print("=" * 50)
    
    # Initialize databases
    init_all_databases()
    
    print("\n📝 Configuration:")
    print(f"   PostgreSQL: {POSTGRES_URL.split('@')[1] if '@' in POSTGRES_URL else POSTGRES_URL}")
    print(f"   MongoDB: {MONGODB_URI.split('@')[1] if '@' in MONGODB_URI else MONGODB_URI}")
    print("\n✨ Ready to use!")
