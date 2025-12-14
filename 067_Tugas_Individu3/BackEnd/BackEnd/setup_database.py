"""
Setup PostgreSQL database for Product Review Analyzer
"""
import sys
from sqlalchemy import create_engine
from BackEnd.models.meta import Base
from BackEnd.models.review import Review

def setup_database():
    """Create database tables"""
    print("Setting up PostgreSQL database...")
    
    # Prompt for database credentials
    print("\n=== PostgreSQL Configuration ===")
    db_user = input("PostgreSQL username (default: postgres): ").strip() or "postgres"
    db_password = input("PostgreSQL password: ").strip()
    db_host = input("Database host (default: localhost): ").strip() or "localhost"
    db_port = input("Database port (default: 5432): ").strip() or "5432"
    db_name = input("Database name (default: product_review_db): ").strip() or "product_review_db"
    
    # Create connection string
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        print(f"\nConnecting to: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        engine = create_engine(connection_string)
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(engine)
        
        print("\n✓ Database setup complete!")
        print(f"\nAdd this to your development.ini:")
        print(f"sqlalchemy.url = {connection_string}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error setting up database: {str(e)}")
        print("\nMake sure:")
        print("1. PostgreSQL is installed and running")
        print("2. The database exists (create it first if needed)")
        print("3. Your credentials are correct")
        return False

if __name__ == '__main__':
    setup_database()
