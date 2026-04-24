import sqlite3

print("🔧 ARREGLANDO TABLA VENTAS...")
print("="*50)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Ver qué columnas existen en ventas
cursor.execute("PRAGMA table_info(ventas)")
columnas_ventas = [col[1] for col in cursor.fetchall()]
print(f"📋 Columnas actuales en ventas: {columnas_ventas}")
print("-"*50)

# Agregar columna pedido_id a ventas si no existe
if 'pedido_id' not in columnas_ventas:
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN pedido_id INTEGER DEFAULT NULL")
        print("✅ Columna 'pedido_id' agregada a ventas")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("ℹ️ Columna 'pedido_id' ya existe en ventas")

conn.commit()
conn.close()

print("="*50)
print("✅ ¡TABLA VENTAS ARREGLADA!")