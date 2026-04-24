# actualizar_pedidos.py
import sqlite3

print("🔧 Actualizando base de datos...")

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Agregar columna venta_id (para vincular pedido con venta)
try:
    cursor.execute("ALTER TABLE pedidos ADD COLUMN venta_id INTEGER DEFAULT NULL")
    print("✅ Columna 'venta_id' agregada")
except:
    print("ℹ️ Columna 'venta_id' ya existe")

# Agregar columna fecha_aprobacion
try:
    cursor.execute("ALTER TABLE pedidos ADD COLUMN fecha_aprobacion TEXT")
    print("✅ Columna 'fecha_aprobacion' agregada")
except:
    print("ℹ️ Columna 'fecha_aprobacion' ya existe")

conn.commit()
conn.close()

print("\n✅ Base de datos actualizada correctamente")
print("Ahora puedes reemplazar tu archivo pedidos.py")