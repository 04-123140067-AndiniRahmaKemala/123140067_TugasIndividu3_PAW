"""
Quick database setup script with default values
"""
from sqlalchemy import create_engine
from BackEnd.models.meta import Base
from BackEnd.models.review import Review

# Default PostgreSQL connection (update if needed)
DB_USER = "postgres"
DB_PASSWORD = "123140197"  # Update with your password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "product_review_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    print(f"Connecting to database...")
    engine = create_engine(connection_string)
    
    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    print("\n✓ Database setup complete!")
    print(f"\nConnection string for development.ini:")
    print(f"sqlalchemy.url = {connection_string}")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    print("\nMake sure:")
    print("1. PostgreSQL is running")
    print("2. Database 'product_review_db' exists")
    print("3. Update DB_PASSWORD in this script")
