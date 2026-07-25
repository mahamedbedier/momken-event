import sqlite3

def run_migration():
    print("Connecting to database...")
    conn = sqlite3.connect('instance/momken.db')
    try:
        print("Dropping is_admin column from users table...")
        conn.execute('ALTER TABLE users DROP COLUMN is_admin')
        conn.commit()
        print("Successfully dropped is_admin column!")
    except sqlite3.OperationalError as e:
        print(f"Error (maybe column already dropped or sqlite version too old): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
