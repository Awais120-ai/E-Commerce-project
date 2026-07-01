import sqlite3

def inspect_db():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", tables)
    for table_name_tup in tables:
        table_name = table_name_tup[0]
        if table_name.startswith("sqlite_"):
            continue
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"\nColumns in {table_name}:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    conn.close()

if __name__ == "__main__":
    inspect_db()
