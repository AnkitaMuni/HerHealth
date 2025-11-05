import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host='localhost',       # Or your DB host
            user='root',            # Your MySQL username
            password='honeymuni2005', # Your MySQL password
            database='herhealth'
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def fetch_query(query, params=None):
    """Helper function to fetch data."""
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True) 
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Error fetching query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()