import psycopg2
from django.conf import settings

# Get database settings from Django
DATABASES = settings.DATABASES['default']

try:
    # Connect to the database
    conn = psycopg2.connect(
        dbname='postgres',  # Connect to the default 'postgres' database
        user=DATABASES['USER'],
        password=DATABASES['PASSWORD'],
        host=DATABASES['HOST'],
        port=DATABASES['PORT']
    )
    conn.autocommit = True
    
    # Get a cursor
    with conn.cursor() as cur:
        # Terminate all connections to the test database
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'test_neondb'
            AND pid <> pg_backend_pid();
        """)
        print(f"Terminated {cur.rowcount} connections to test_neondb")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
