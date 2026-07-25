import sqlite3

def run_fix():
    print("Fixing admin role in database...")
    conn = sqlite3.connect('instance/momken.db')
    try:
        cursor = conn.execute('SELECT email, role FROM users')
        print("Current users:")
        for row in cursor:
            print(row)
            
        print("\nUpdating admin@momken.com to role 'admin'...")
        conn.execute('UPDATE users SET role="admin" WHERE email="admin@momken.com"')
        conn.commit()
        print("Successfully updated!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_fix()
