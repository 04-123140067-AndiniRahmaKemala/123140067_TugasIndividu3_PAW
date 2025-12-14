"""
Create PostgreSQL database
"""
import psycopg2
from psycopg2 import sql

# PostgreSQL connection details
DB_USER = "postgres"
DB_PASSWORD = "123140197"  # Update with your password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "product_review_db"

try:
    # Connect to default 'postgres' database
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if exists:
        print(f"✓ Database '{DB_NAME}' already exists")
    else:
        # Create database
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME)
        ))
        print(f"✓ Database '{DB_NAME}' created successfully!")
    
    cursor.close()
    conn.close()
    
    print("\nNow run: python quick_setup_db.py")
    
except psycopg2.OperationalError as e:
    print(f"\n✗ Connection Error: {str(e)}")
    print("\nPlease check:")
    print("1. PostgreSQL is running")
    print("2. Username and password are correct")
    print("3. Update DB_PASSWORD in this script if needed")
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
