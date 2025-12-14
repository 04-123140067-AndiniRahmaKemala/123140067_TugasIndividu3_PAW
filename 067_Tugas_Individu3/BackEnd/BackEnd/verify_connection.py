"""
Verify PostgreSQL connection and check tables
"""
from sqlalchemy import create_engine, inspect

DB_USER = "postgres"
DB_PASSWORD = "123140197"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "product_review_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    print("Testing PostgreSQL connection...")
    print(f"Connecting to: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}\n")
    
    engine = create_engine(connection_string)
    inspector = inspect(engine)
    
    # Test connection
    with engine.connect() as conn:
        print("✅ Database connection successful!\n")
    
    # Check tables
    tables = inspector.get_table_names()
    print(f"📊 Tables in database: {len(tables)}")
    for table in tables:
        print(f"   - {table}")
        
        # Get columns
        columns = inspector.get_columns(table)
        print(f"     Columns: {', '.join([col['name'] for col in columns])}")
    
    # Count records
    if 'reviews' in tables:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT COUNT(*) FROM reviews"))
            count = result.scalar()
            print(f"\n📝 Total reviews in database: {count}")
    
    print("\n✅ Database is connected and ready!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nPossible issues:")
    print("1. PostgreSQL service not running")
    print("2. Incorrect password")
    print("3. Database does not exist")
