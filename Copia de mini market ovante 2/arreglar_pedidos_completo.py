import sqlite3

print("🔧 ARREGLANDO TABLA PEDIDOS COMPLETAMENTE...")
print("="*50)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Ver qué columnas existen actualmente
cursor.execute("PRAGMA table_info(pedidos)")
columnas = [col[1] for col in cursor.fetchall()]
print(f"📋 Columnas actuales: {columnas}")
print("-"*50)

# Lista de columnas que necesitamos
columnas_necesarias = [
    ('total', 'REAL DEFAULT 0'),
    ('observaciones', 'TEXT'),
    ('venta_id', 'INTEGER DEFAULT NULL'),
    ('fecha_aprobacion', 'TEXT')
]

for columna, tipo in columnas_necesarias:
    if columna not in columnas:
        try:
            cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {columna} {tipo}")
            print(f"✅ Columna '{columna}' agregada")
        except Exception as e:
            print(f"❌ Error al agregar '{columna}': {e}")
    else:
        print(f"ℹ️ Columna '{columna}' ya existe")

conn.commit()
conn.close()

print("="*50)
print("✅ ¡TABLA PEDIDOS ARREGLADA!")
print("Ahora puedes ejecutar tu aplicación normalmente.")