import psycopg2

try:
    conn = psycopg2.connect(
        dbname='library_db',
        user='postgres',
        password='olamizzy66',
        host='localhost'
    )
    print("Connection successful")
except Exception as e:
    print("Error connecting to database:", e)
finally:
    if conn:
        conn.close()
