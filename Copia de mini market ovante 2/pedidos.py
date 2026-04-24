from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

class Pedidos(tk.Frame):
    db_name = "database.db"

    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_clientes()
        self.cargar_productos()
        self.cargar_pedidos()

    def widgets(self):
        # ====== FRAME DE REGISTRO ======
        self.labelframe = tk.LabelFrame(self, text="Registrar Pedido", font="sans 16 bold", bg="#C6D9E3")
        self.labelframe.place(x=20, y=20, width=350, height=560)

        # Cliente
        tk.Label(self.labelframe, text="Cliente:*", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=20)
        self.cliente = ttk.Combobox(self.labelframe, font="sans 11")
        self.cliente.place(x=10, y=50, width=320, height=30)
        
        # Producto
        tk.Label(self.labelframe, text="Producto:*", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=90)
        self.producto = ttk.Combobox(self.labelframe, font="sans 11")
        self.producto.place(x=10, y=120, width=320, height=30)
        self.producto.bind('<<ComboboxSelected>>', self.actualizar_precio)

        # Cantidad
        tk.Label(self.labelframe, text="Cantidad:*", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=160)
        self.cantidad = ttk.Entry(self.labelframe, font="sans 11")
        self.cantidad.place(x=10, y=190, width=320, height=30)
        self.cantidad.bind('<KeyRelease>', self.calcular_total)

        # Precio
        tk.Label(self.labelframe, text="Precio:", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=230)
        self.precio = ttk.Entry(self.labelframe, font="sans 11", state="readonly")
        self.precio.place(x=10, y=260, width=150, height=30)

        # Total
        tk.Label(self.labelframe, text="Total:", font="sans 12 bold", bg="#C6D9E3").place(x=180, y=230)
        self.total = ttk.Entry(self.labelframe, font="sans 11", state="readonly")
        self.total.place(x=180, y=260, width=150, height=30)

        # Fecha
        tk.Label(self.labelframe, text="Fecha:", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=300)
        self.fecha = ttk.Entry(self.labelframe, font="sans 11")
        self.fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.fecha.place(x=10, y=330, width=150, height=30)
        self.fecha.config(state="readonly")

        # Estado
        tk.Label(self.labelframe, text="Estado:", font="sans 12 bold", bg="#C6D9E3").place(x=180, y=300)
        self.estado = ttk.Combobox(self.labelframe, 
                                   values=["Pendiente", "Aprobado", "Rechazado"])
        self.estado.place(x=180, y=330, width=150, height=30)
        self.estado.set("Pendiente")

        # Observaciones
        tk.Label(self.labelframe, text="Observaciones:", font="sans 12 bold", bg="#C6D9E3").place(x=10, y=370)
        self.observaciones = tk.Text(self.labelframe, font="sans 11", height=3, width=35)
        self.observaciones.place(x=10, y=400, width=320, height=60)

        # Botón Registrar
        tk.Button(self.labelframe, text="Registrar Pedido", font="sans 12 bold", bg="#4CAF50", fg="white",
                 command=self.registrar).place(x=10, y=480, width=320, height=40)

        # Botón Refrescar Clientes
        tk.Button(self.labelframe, text="🔄 Refrescar Clientes", font="sans 10 bold", 
                 bg="#FF9800", fg="white", command=self.cargar_clientes).place(x=10, y=525, width=150, height=30)

        # ====== TABLA DE PEDIDOS ======
        treFrame = Frame(self, bg="white")
        treFrame.place(x=380, y=20, width=700, height=500)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        # 👇 MODIFICADO: Eliminada columna "Venta"
        self.tre = ttk.Treeview(
            treFrame,
            yscrollcommand=scrol_y.set,
            xscrollcommand=scrol_x.set,
            columns=("ID", "Cliente", "Producto", "Cantidad", "Total", "Fecha", "Estado"),
            show="headings"
        )
        self.tre.pack(expand=True, fill=BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        self.tre.heading("ID", text="ID")
        self.tre.heading("Cliente", text="Cliente")
        self.tre.heading("Producto", text="Producto")
        self.tre.heading("Cantidad", text="Cantidad")
        self.tre.heading("Total", text="Total")
        self.tre.heading("Fecha", text="Fecha")
        self.tre.heading("Estado", text="Estado")

        self.tre.column("ID", width=50, anchor="center")
        self.tre.column("Cliente", width=150, anchor="center")
        self.tre.column("Producto", width=150, anchor="center")
        self.tre.column("Cantidad", width=80, anchor="center")
        self.tre.column("Total", width=120, anchor="center")
        self.tre.column("Fecha", width=100, anchor="center")
        self.tre.column("Estado", width=100, anchor="center")

        # Botones de acción
        btnFrame = Frame(self, bg="#C6D9E3")
        btnFrame.place(x=380, y=530, width=700, height=50)

        tk.Button(btnFrame, text="✅ Aprobar Pedido", command=self.aprobar_pedido,
                 font="sans 10 bold", bg="#4CAF50", fg="white").pack(side=LEFT, padx=5)
        tk.Button(btnFrame, text="❌ Rechazar", command=self.rechazar_pedido,
                 font="sans 10 bold", bg="#F44336", fg="white").pack(side=LEFT, padx=5)
        tk.Button(btnFrame, text="🔄 Refrescar", command=self.cargar_pedidos,
                 font="sans 10 bold", bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        tk.Button(btnFrame, text="📊 Ver Ventas", command=self.ver_ventas_pedido,
                 font="sans 10 bold", bg="#FF9800", fg="white").pack(side=LEFT, padx=5)

    def cargar_clientes(self):
        """Carga los clientes en el combobox"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM clientes ORDER BY nombre")
            clientes = [row[0] for row in cursor.fetchall()]
            self.cliente['values'] = clientes
            conn.close()
        except Exception as e:
            print(f"Error cargando clientes: {e}")
            self.cliente['values'] = []

    def cargar_productos(self):
        """Carga los productos en el combobox"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT articulo FROM articulos WHERE stock > 0 ORDER BY articulo")
            productos = [row[0] for row in cursor.fetchall()]
            self.producto['values'] = productos
            conn.close()
        except Exception as e:
            print(f"Error cargando productos: {e}")
            self.producto['values'] = []

    def actualizar_precio(self, event=None):
        producto = self.producto.get()
        if not producto:
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT precio FROM articulos WHERE articulo=?", (producto,))
            resultado = cursor.fetchone()
            conn.close()
            if resultado:
                self.precio.config(state="normal")
                self.precio.delete(0, END)
                self.precio.insert(0, f"{resultado[0]:,.0f}".replace(",", "."))
                self.precio.config(state="readonly")
                self.calcular_total()
        except:
            pass

    def calcular_total(self, event=None):
        try:
            cantidad = int(self.cantidad.get() or 0)
            precio_texto = self.precio.get().replace(".", "")
            precio = float(precio_texto) if precio_texto else 0
            total = cantidad * precio
            self.total.config(state="normal")
            self.total.delete(0, END)
            self.total.insert(0, f"{total:,.0f}".replace(",", "."))
            self.total.config(state="readonly")
        except:
            pass

    def registrar(self):
        if not self.cliente.get() or not self.producto.get() or not self.cantidad.get():
            messagebox.showerror("Error", "Cliente, producto y cantidad son obligatorios")
            return

        try:
            cantidad = int(self.cantidad.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
        except:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        # Obtener precio
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT precio FROM articulos WHERE articulo=?", (self.producto.get(),))
            precio = cursor.fetchone()[0]
            total = cantidad * precio
            conn.close()
        except:
            messagebox.showerror("Error", "Error al obtener precio")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO pedidos 
                (cliente, producto, cantidad, fecha, estado, observaciones, total) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.cliente.get(),
                self.producto.get(),
                cantidad,
                self.fecha.get(),
                self.estado.get(),
                self.observaciones.get("1.0", END).strip(),
                total
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "✅ Pedido registrado")
            self.limpiar_campos()
            self.cargar_pedidos()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")

    def cargar_pedidos(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            for item in self.tre.get_children():
                self.tre.delete(item)

            # Cargar TODOS los pedidos
            cursor.execute("""
                SELECT id, cliente, producto, cantidad, total, fecha, estado 
                FROM pedidos 
                ORDER BY 
                    CASE estado 
                        WHEN 'Pendiente' THEN 1
                        WHEN 'Aprobado' THEN 2
                        WHEN 'Rechazado' THEN 3
                        ELSE 4
                    END,
                    fecha DESC
            """)

            for row in cursor.fetchall():
                id, cliente, producto, cantidad, total, fecha, estado = row
                
                total_formateado = f"${total:,.0f}".replace(",", ".") if total else "$0"
                
                # Color según estado
                if estado == "Pendiente":
                    tag = 'pendiente'
                elif estado == "Aprobado":
                    tag = 'aprobado'
                elif estado == "Rechazado":
                    tag = 'rechazado'
                else:
                    tag = ''

                # 👇 MODIFICADO: Eliminado venta_texto
                self.tre.insert("", "end", 
                              values=(id, cliente, producto, cantidad, total_formateado, fecha, estado),
                              tags=(tag,))

            # Configurar colores
            self.tre.tag_configure('pendiente', background='#FFF9C4')  # Amarillo
            self.tre.tag_configure('aprobado', background='#C8E6C9')   # Verde
            self.tre.tag_configure('rechazado', background='#FFCDD2')  # Rojo

            conn.close()
        except sqlite3.Error as e:
            print(f"Error cargando pedidos: {e}")

    def aprobar_pedido(self):
        if not self.tre.selection():
            messagebox.showerror("Error", "Seleccione un pedido")
            return

        item = self.tre.selection()[0]
        valores = self.tre.item(item, "values")
        id_pedido = valores[0]
        estado_actual = valores[6]

        if estado_actual == "Aprobado":
            messagebox.showinfo("Info", "Este pedido ya está aprobado")
            return

        if estado_actual == "Rechazado":
            messagebox.showinfo("Info", "No se puede aprobar un pedido rechazado")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Obtener datos del pedido
            cursor.execute("SELECT cliente, producto, cantidad, total FROM pedidos WHERE id=?", (id_pedido,))
            pedido = cursor.fetchone()
            
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
                
            cliente, producto, cantidad, total = pedido
            
            # Verificar stock
            cursor.execute("SELECT stock FROM articulos WHERE articulo=?", (producto,))
            stock = cursor.fetchone()[0]
            
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {stock}")
                return
            
            # Actualizar estado del pedido
            fecha_aprobacion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE pedidos 
                SET estado='Aprobado', fecha_aprobacion=? 
                WHERE id=?
            """, (fecha_aprobacion, id_pedido))
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "✅ Pedido aprobado")
            self.cargar_pedidos()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")

    def rechazar_pedido(self):
        if not self.tre.selection():
            messagebox.showerror("Error", "Seleccione un pedido")
            return

        item = self.tre.selection()[0]
        id_pedido = self.tre.item(item, "values")[0]

        if messagebox.askyesno("Confirmar", "¿Rechazar este pedido?"):
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("UPDATE pedidos SET estado='Rechazado' WHERE id=?", (id_pedido,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Pedido rechazado")
                self.cargar_pedidos()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error: {e}")

    def ver_ventas_pedido(self):
        if not self.tre.selection():
            messagebox.showerror("Error", "Seleccione un pedido")
            return

        item = self.tre.selection()[0]
        id_pedido = self.tre.item(item, "values")[0]

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Buscar ventas relacionadas con este pedido
            cursor.execute("""
                SELECT factura, fecha, total 
                FROM ventas 
                WHERE pedido_id=? 
                ORDER BY fecha DESC
            """, (id_pedido,))
            
            ventas = cursor.fetchall()
            conn.close()

            if ventas:
                mensaje = "📋 Ventas generadas de este pedido:\n\n"
                for factura, fecha, total in ventas:
                    mensaje += f"Factura #{factura} - {fecha} - ${total:,.0f}\n".replace(",", ".")
                messagebox.showinfo("Ventas del Pedido", mensaje)
            else:
                messagebox.showinfo("Info", "Este pedido aún no tiene ventas generadas")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")

    def limpiar_campos(self):
        self.cliente.set('')
        self.producto.set('')
        self.cantidad.delete(0, END)
        self.precio.config(state="normal")
        self.precio.delete(0, END)
        self.precio.config(state="readonly")
        self.total.config(state="normal")
        self.total.delete(0, END)
        self.total.config(state="readonly")
        self.observaciones.delete("1.0", END)
        self.estado.set("Pendiente")