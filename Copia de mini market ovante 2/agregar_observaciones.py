import sqlite3

print("🔧 Agregando columna 'observaciones' a la tabla pedidos...")

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE pedidos ADD COLUMN observaciones TEXT")
    print("✅ Columna 'observaciones' agregada correctamente")
except sqlite3.OperationalError as e:
    print(f"ℹ️ {e}")

conn.commit()
conn.close()

print("✅ Listo. Ahora puedes ejecutar tu aplicación.")