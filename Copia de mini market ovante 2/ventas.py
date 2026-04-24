import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import sys
import os


class Ventas(tk.Frame):
    db_name = "database.db"

    def __init__(self, padre):
        super().__init__(padre)

        # Obtener número de factura correctamente
        self.numero_factura = self.obtener_numero_factura_actual()
        self.productos_seleccionados = []
        
        # Inicializar timer para filtrado
        self.timer_producto = None

        self.widgets()
        self.cargar_productos()
        self.cargar_clientes()

    def cargar_clientes(self):
        """Carga los clientes desde la base de datos"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT DISTINCT cliente FROM ventas UNION SELECT 'Cliente Mostrador'")
            clientes = [row[0] for row in c.fetchall()]
            self.entry_cliente['values'] = clientes
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando clientes:", e)

    def obtener_numero_factura_actual(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            c.execute("SELECT MAX(factura) FROM ventas")
            last_invoice_number = c.fetchone()[0]

            conn.close()

            return last_invoice_number + 1 if last_invoice_number else 1

        except sqlite3.Error as e:
            print("Error obteniendo el numero de factura actual:", e)
            return 1
        
    def cargar_productos(self):   
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT articulo FROM articulos WHERE estado='Activo'")
            self.products = [product[0] for product in c.fetchall()]
            self.entry_producto["values"] = self.products
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando productos:", e)  
            
    def filtrar_productos(self, event):
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.5, self._filter_products)
        self.timer_producto.start()
        
    def _filter_products(self):
        typed = self.entry_producto.get()
        
        if typed == '':
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]
            
        if data:
            self.entry_producto['values'] = data
            self.entry_producto.event_generate('<Down>') 
        else:
            self.entry_producto['values'] = ['No se encontraron resultados'] 
            self.entry_producto.event_generate('<Down>')      
            self.entry_producto.delete(0, tk.END)
            
    def actualizar_detalle_producto(self, event=None):
        """Actualiza el stock cuando se selecciona un producto"""
        producto = self.entry_producto.get()
        
        if not producto:
            return
            
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock, precio FROM articulos WHERE articulo=?", (producto,))
            resultado = c.fetchone()
            if resultado:
                stock, precio = resultado
                self.label_stock.config(text=f"Stock: {stock}")
                self.label_precio_valor.config(text=f"$ {precio:,.0f}".replace(",", "."))
            conn.close()
        except sqlite3.Error as e:
            print("Error al obtener el stock:", e)
            
    def agregar_articulos(self):
        cliente = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()
        
        if not cliente:
            messagebox.showerror("Error", "Por favor seleccione un cliente.")
            return
            
        if not producto:
            messagebox.showerror("Error", "Por favor seleccione un producto.")
            return
        
        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida.")
            return  
        
        cantidad = int(cantidad)
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (producto,))
            resultado = c.fetchone()
            
            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado.")
                return 
            
            precio, costo, stock = resultado
            
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                return
                
            total = precio * cantidad   
            total_cop = "{:,.0f}".format(total).replace(",", ".")
            precio_formateado = "{:,.0f}".format(precio).replace(",", ".")
            
            self.tre.insert("", "end", values=(
                self.numero_factura, 
                cliente, 
                producto,
                precio_formateado, 
                cantidad, 
                total_cop
            ))
            
            self.productos_seleccionados.append((
                self.numero_factura, 
                cliente, 
                producto, 
                precio, 
                cantidad, 
                total, 
                costo
            ))
            
            conn.close()
            
            self.entry_producto.set('')
            self.entry_cantidad.delete(0, 'end')
            self.label_stock.config(text="Stock:")
            self.label_precio_valor.config(text="$ 0")
            
        except sqlite3.Error as e:
            print("Error al agregar articulo", e)
            
        self.calcular_precio_total()
        
    def calcular_precio_total(self):
        total_pagar = 0
        for item in self.tre.get_children():
            valor = self.tre.item(item)["values"][-1]
            # Limpiar formato para convertir a número
            valor_limpio = valor.replace(".", "").replace(",", "").strip()
            if valor_limpio and valor_limpio.isdigit():
                total_pagar += float(valor_limpio)
        
        total_pagar_cop = "{:,.0f}".format(total_pagar).replace(",", ".")
        self.label_precio_total.config(text=f"Precio a pagar: $ {total_pagar_cop}")
               
    def realizar_pago(self):
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos seleccionados para realizar el pago.")
            return
            
        total_venta = 0
        for item in self.productos_seleccionados:
            total_venta += float(item[5])
        
        total_formateado = "{:,.0f}".format(total_venta).replace(",", ".")
        
        ventana_pago = tk.Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg="#C6D9E3")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()
        ventana_pago.focus_set()
        ventana_pago.lift()
        
        label_titulo = tk.Label(ventana_pago, text="Realizar pago", font="sans 30 bold", bg="#C6D9E3")
        label_titulo.place(x=70, y=10)
        
        label_total = tk.Label(ventana_pago, text=f"Total a pagar: $ {total_formateado}", font="sans 14 bold", bg="#C6D9E3")
        label_total.place(x=80, y=100)
        
        label_monto = tk.Label(ventana_pago, text="Ingrese el monto pagado:", font="sans 14 bold", bg="#C6D9E3")
        label_monto.place(x=80, y=160)
        
        self.entry_monto = ttk.Entry(ventana_pago, font="sans 14 bold")
        self.entry_monto.place(x=80, y=210, width=240, height=40)
        
        button_confirmar_pago = tk.Button(
            ventana_pago, 
            text="Confirmar pago", 
            font="sans 14 bold", 
            command=lambda: self.procesar_pago(self.entry_monto.get(), ventana_pago, total_venta)
        )
        button_confirmar_pago.place(x=80, y=270, width=240, height=40)
        
    def procesar_pago(self, cantidad_pagada, ventana_pago, total_ventas):
        try:
            cantidad_pagada = float(cantidad_pagada.replace(".", "").replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido")
            return
            
        if cantidad_pagada < total_ventas:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return
        
        cambio = cantidad_pagada - total_ventas
        
        total_formateado = "{:,.0f}".format(total_ventas).replace(",", ".")
        cambio_formateado = "{:,.0f}".format(cambio).replace(",", ".")
        cantidad_formateada = "{:,.0f}".format(cantidad_pagada).replace(",", ".")
        
        mensaje = f"Total: $ {total_formateado}\nCantidad pagada: $ {cantidad_formateada}\nCambio: $ {cambio_formateado}"
        messagebox.showinfo("Pago realizado", mensaje)
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d") 
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.execute(
                    """INSERT INTO ventas 
                       (factura, cliente, articulo, precio, cantidad, total, costo, fecha, hora) 
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (factura, cliente, producto, precio, cantidad, total, costo * cantidad, fecha_actual, hora_actual)
                )
                
                c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo = ?", (cantidad, producto))
               
            conn.commit()
            self.generar_factura_pdf(total_ventas, cliente)
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar la venta: {e}") 
            return
            
        self.numero_factura += 1
        self.label_numero_factura.config(text=str(self.numero_factura))  
        
        self.productos_seleccionados = []
        self.limpiar_campos()
        
        ventana_pago.destroy()
        
    def limpiar_campos(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.label_precio_total.config(text="Precio a pagar: $ 0")
        self.entry_producto.set('')
        self.entry_cantidad.delete(0, 'end')
        self.label_stock.config(text="Stock:")
        self.label_precio_valor.config(text="$ 0")
    
    def eliminar_articulo(self):
        item_seleccionado = self.tre.selection()
        if not item_seleccionado:
            messagebox.showerror("Error", "No hay ningún artículo seleccionado")
            return 
        
        item_id = item_seleccionado[0]
        valores_item = self.tre.item(item_id)["values"]
        producto = valores_item[2]
        
        self.tre.delete(item_id)
        
        # Eliminar de productos_seleccionados
        self.productos_seleccionados = [
            p for p in self.productos_seleccionados if p[2] != producto
        ]
        
        self.calcular_precio_total()    
        
    def editar_articulo(self):
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor seleccione un artículo para editar")
            return
        
        item_values = self.tre.item(selected_item[0], 'values')   
        if not item_values:
            return
        
        current_producto = item_values[2]
        current_cantidad = int(item_values[4])
        
        new_cantidad = simpledialog.askinteger(
            "Editar artículo", 
            "Ingrese la nueva cantidad:", 
            initialvalue=current_cantidad,
            minvalue=1
        )
        
        if new_cantidad is not None and new_cantidad > 0:
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (current_producto,))
                resultado = c.fetchone()
                
                if resultado:
                    precio, costo, stock = resultado
                    
                    # Verificar stock disponible (considerando lo ya agregado)
                    stock_actual = stock
                    for p in self.productos_seleccionados:
                        if p[2] == current_producto:
                            stock_actual += p[4]  # Sumar lo que ya estaba en la venta
                    
                    if new_cantidad > stock_actual:
                        messagebox.showerror(
                            "Error", 
                            f"Stock insuficiente. Stock disponible: {stock_actual}"
                        )
                        conn.close()
                        return
                    
                    total = precio * new_cantidad
                    total_cop = "{:,.0f}".format(total).replace(",", ".")
                    precio_formateado = "{:,.0f}".format(precio).replace(",", ".")
                    
                    self.tre.item(
                        selected_item[0], 
                        values=(
                            self.numero_factura, 
                            self.entry_cliente.get(), 
                            current_producto, 
                            precio_formateado, 
                            new_cantidad,
                            total_cop
                        )
                    )
                    
                    # Actualizar en productos_seleccionados
                    for idx, producto in enumerate(self.productos_seleccionados):
                        if producto[2] == current_producto:
                            self.productos_seleccionados[idx] = (
                                self.numero_factura, 
                                self.entry_cliente.get(), 
                                current_producto, 
                                precio, 
                                new_cantidad, 
                                total, 
                                costo
                            )
                            break
                        
                conn.close()
                self.calcular_precio_total()
                
            except sqlite3.Error as e: 
                print("Error al editar el artículo: ", e)
                messagebox.showerror("Error", f"Error al editar: {e}")
    
    def ver_ventas_realizadas(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM ventas ORDER BY fecha DESC, hora DESC")
            ventas = c.fetchall()
            conn.close()
            
            ventana_ventas = tk.Toplevel(self)
            ventana_ventas.title("Ventas Realizadas") 
            ventana_ventas.geometry("1100x650+120+20") 
            ventana_ventas.configure(bg="#C6D9E3")
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set() 
            ventana_ventas.focus_set()
            ventana_ventas.lift()
            
            def filtrar_ventas():
                factura_a_buscar = entry_factura.get().strip()
                cliente_a_buscar = entry_cliente_filtro.get().strip()
                
                # Limpiar tree
                for item in tree.get_children():
                    tree.delete(item)
                    
                ventas_filtradas = []
                for venta in ventas:
                    factura_ok = not factura_a_buscar or str(venta[0]) == factura_a_buscar
                    cliente_ok = not cliente_a_buscar or cliente_a_buscar.lower() in venta[1].lower()
                    
                    if factura_ok and cliente_ok:
                        ventas_filtradas.append(venta)
                
                for venta in ventas_filtradas:
                    venta_lista = list(venta)
                    # Formatear precios (columnas 3 y 5)
                    venta_lista[3] = "{:,.0f}".format(venta_lista[3]).replace(",", ".")  # precio
                    venta_lista[5] = "{:,.0f}".format(venta_lista[5]).replace(",", ".")  # total
                    # Formatear fecha (columna 7)
                    if isinstance(venta_lista[7], str):
                        try:
                            fecha_obj = datetime.datetime.strptime(venta_lista[7], "%Y-%m-%d")
                            venta_lista[7] = fecha_obj.strftime("%d-%m-%Y")
                        except ValueError:
                            pass
                    tree.insert("", "end", values=venta_lista)
            
            label_ventas_realizadas = tk.Label(
                ventana_ventas, 
                text="Ventas realizadas", 
                font="sans 26 bold", 
                bg="#C6D9E3"
            )   
            label_ventas_realizadas.place(x=350, y=20)     
            
            filtro_frame = tk.Frame(ventana_ventas, bg="#C6D9E3")
            filtro_frame.place(x=20, y=60, width=1060, height=60)
            
            # Filtro por factura
            tk.Label(filtro_frame, text="Factura:", bg="#C6D9E3", font="sans 12 bold").place(x=20, y=15)
            entry_factura = ttk.Entry(filtro_frame, font="sans 12", width=15)
            entry_factura.place(x=90, y=10, width=100, height=30)
            
            # Filtro por cliente
            tk.Label(filtro_frame, text="Cliente:", bg="#C6D9E3", font="sans 12 bold").place(x=220, y=15)
            entry_cliente_filtro = ttk.Entry(filtro_frame, font="sans 12", width=20)
            entry_cliente_filtro.place(x=290, y=10, width=150, height=30)
            
            btn_filtrar = tk.Button(
                filtro_frame, 
                text="Filtrar", 
                font="sans 12 bold",
                bg="#4CAF50",
                fg="white",
                command=filtrar_ventas
            )
            btn_filtrar.place(x=470, y=10, width=100, height=30)
            
            # Botón para mostrar todas
            btn_mostrar_todas = tk.Button(
                filtro_frame,
                text="Mostrar todas",
                font="sans 12 bold",
                bg="#2196F3",
                fg="white",
                command=lambda: [entry_factura.delete(0, 'end'), 
                                entry_cliente_filtro.delete(0, 'end'), 
                                filtrar_ventas()]
            )
            btn_mostrar_todas.place(x=580, y=10, width=120, height=30)
            
            tree_frame = tk.Frame(ventana_ventas, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)
            
            scrol_y = ttk.Scrollbar(tree_frame)
            scrol_y.pack(side=RIGHT, fill=Y)
            
            scrol_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
            scrol_x.pack(side=BOTTOM, fill=X)
            
            tree = ttk.Treeview(
                tree_frame, 
                columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"), 
                show="headings",
                height=20
            )
            tree.pack(expand=True, fill=BOTH)
            
            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)
            
            tree.heading("Factura", text="Factura")
            tree.heading("Cliente", text="Cliente")
            tree.heading("Producto", text="Producto")
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha")
            tree.heading("Hora", text="Hora")
            
            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=150, anchor="center")
            tree.column("Producto", width=200, anchor="center")
            tree.column("Precio", width=100, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=100, anchor="center")
            tree.column("Fecha", width=100, anchor="center")
            tree.column("Hora", width=80, anchor="center")
            
            for venta in ventas:
                venta_lista = list(venta)
                # Formatear precios
                venta_lista[3] = "{:,.0f}".format(venta_lista[3]).replace(",", ".")  # precio
                venta_lista[5] = "{:,.0f}".format(venta_lista[5]).replace(",", ".")  # total
                # Formatear fecha (columna 7)
                if isinstance(venta_lista[7], str):
                    try:
                        fecha_obj = datetime.datetime.strptime(venta_lista[7], "%Y-%m-%d")
                        venta_lista[7] = fecha_obj.strftime("%d-%m-%Y")
                    except ValueError:
                        pass
                tree.insert("", "end", values=venta_lista)
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener las ventas: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            
    def widgets(self):
        labelframe = tk.LabelFrame(self, font="sans 12 bold", bg="#C6D9E3")
        labelframe.place(x=25, y=30, width=1045, height=180)

        label_cliente = tk.Label(
            labelframe,
            text="Cliente:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        label_cliente.place(x=10, y=11)

        self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)

        label_producto = tk.Label(
            labelframe,
            text="Producto:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        label_producto.place(x=10, y=70)

        self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind('<KeyRelease>', self.filtrar_productos)  
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_detalle_producto)

        label_cantidad = tk.Label(
            labelframe,
            text="Cantidad:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        label_cantidad.place(x=500, y=11)

        self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
        self.entry_cantidad.place(x=610, y=8, width=100, height=40)

        # Label para mostrar precio
        label_precio_texto = tk.Label(
            labelframe,
            text="Precio:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        label_precio_texto.place(x=500, y=50)
        
        self.label_precio_valor = tk.Label(
            labelframe,
            text="$ 0",
            font="sans 14 bold",
            bg="#C6D9E3",
            fg="black"
        )
        self.label_precio_valor.place(x=610, y=50)

        self.label_stock = tk.Label(
            labelframe,
            text="Stock:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        self.label_stock.place(x=500, y=90)

        label_factura = tk.Label(
            labelframe,
            text="Numero de factura:",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        label_factura.place(x=750, y=11)

        self.label_numero_factura = tk.Label(
            labelframe,
            text=f"{self.numero_factura}",
            font="sans 14 bold",
            bg="#C6D9E3"
        )
        self.label_numero_factura.place(x=950, y=11)

        boton_agregar = tk.Button(
            labelframe,
            text="Agregar Articulo",
            font="sans 14 bold",
            command=self.agregar_articulos
        )
        boton_agregar.place(x=90, y=120, width=200, height=40)

        boton_eliminar = tk.Button(
            labelframe,
            text="Eliminar Articulo",
            font="sans 14 bold", 
            command=self.eliminar_articulo
        )
        boton_eliminar.place(x=310, y=120, width=200, height=40)

        boton_editar = tk.Button(
            labelframe,
            text="Editar Articulo",
            font="sans 14 bold", 
            command=self.editar_articulo
        )
        boton_editar.place(x=530, y=120, width=200, height=40)

        boton_limpiar = tk.Button(
            labelframe,
            text="Limpiar lista",
            font="sans 14 bold",
            command=self.limpiar_campos
        )
        boton_limpiar.place(x=750, y=120, width=200, height=40)

        treFrame = tk.Frame(self, bg="white")
        treFrame.place(x=70, y=220, width=900, height=400)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        self.tre = ttk.Treeview(
            treFrame,
            yscrollcommand=scrol_y.set,
            xscrollcommand=scrol_x.set,
            height=15,
            columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"),
            show="headings"
        )

        self.tre.pack(expand=True, fill=BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        self.tre.heading("Factura", text="Factura")
        self.tre.heading("Cliente", text="Cliente")
        self.tre.heading("Producto", text="Producto")
        self.tre.heading("Precio", text="Precio")
        self.tre.heading("Cantidad", text="Cantidad")
        self.tre.heading("Total", text="Total")

        self.tre.column("Factura", width=70, anchor="center")
        self.tre.column("Cliente", width=200, anchor="center")
        self.tre.column("Producto", width=200, anchor="center")
        self.tre.column("Precio", width=120, anchor="center")
        self.tre.column("Cantidad", width=120, anchor="center")
        self.tre.column("Total", width=150, anchor="center")

        # TOTAL A PAGAR
        self.label_precio_total = tk.Label(
            self,
            text="Precio a Pagar: $ 0",
            font="sans 18 bold",
            bg="#C6D9E3"
        )
        self.label_precio_total.place(x=680, y=590)

        # BOTONES
        boton_pagar = tk.Button(
            self,
            text="Pagar",
            font="sans 14 bold",
            command=self.realizar_pago
        )
        boton_pagar.place(x=70, y=590, width=180, height=40)

        boton_ver_ventas = tk.Button(
            self,
            text="Ver ventas realizadas",
            font="sans 14 bold", 
            command=self.ver_ventas_realizadas
        )
        boton_ver_ventas.place(x=290, y=590, width=280, height=40)
    
    def generar_factura_pdf(self, total_venta, cliente):
        try:
            # Crear directorio facturas si no existe
            if not os.path.exists("facturas"):
                os.makedirs("facturas")
                
            factura_path = f"facturas/Factura_{self.numero_factura}.pdf"
            c = canvas.Canvas(factura_path, pagesize=letter)
            
            empresa_nombre = "Ovante Distribuciones"
            empresa_direccion = "Cra 7#180 - 75,MOD 2 Loc 5 CODABAS-Bogotá"
            empresa_telefono = "+57 3229421445"
            empresa_email = "info@ovante-distribuciones.com"
            empresa_website = "infoboyacá@ovante-distribuciones.com"
            
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300, 750, "FACTURA DE SERVICIOS")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, 710, f"{empresa_nombre}")
            c.setFont("Helvetica", 12)
            c.drawString(50, 690, f"Dirección: {empresa_direccion}")
            c.drawString(50, 670, f"Teléfono: {empresa_telefono}")
            c.drawString(50, 650, f"Email: {empresa_email}")
            c.drawString(50, 630, f"Website: {empresa_website}")
            
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(50, 620, 550, 620)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 600, f"Número de factura: {self.numero_factura}")
            c.drawString(50, 580, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.line(50, 560, 550, 560)
            
            c.drawString(50, 540, f"Cliente: {cliente}")
            c.drawString(50, 520, "Descripción de productos:")
            
            y_offset = 500
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y_offset, "Producto")
            c.drawString(270, y_offset, "Cantidad")
            c.drawString(370, y_offset, "Precio")
            c.drawString(470, y_offset, "Total")
            
            c.line(50, y_offset - 10, 550, y_offset - 10)
            y_offset -= 30
            c.setFont("Helvetica", 12)
            
            for item in self.productos_seleccionados:
                factura, cliente_item, producto, precio, cantidad, total, costo = item
                # Truncar nombre del producto si es muy largo
                producto_mostrar = producto[:30] + "..." if len(producto) > 30 else producto
                c.drawString(70, y_offset, producto_mostrar)
                c.drawString(270, y_offset, str(cantidad))
                c.drawString(370, y_offset, "${:,.0f}".format(precio).replace(",", "."))
                c.drawString(470, y_offset, "${:,.0f}".format(total).replace(",", "."))
                y_offset -= 20
                
            c.line(50, y_offset, 550, y_offset)
            y_offset -= 20 
            
            c.setFont("Helvetica-Bold", 14) 
            c.setFillColor(colors.darkblue)
            c.drawString(50, y_offset, f"Total a pagar: $ {total_venta:,.0f}".replace(",", ".")) 
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            
            y_offset -= 20
            c.line(50, y_offset, 550, y_offset)
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(150, y_offset - 60, "¡Gracias por tu compra, vuelve pronto!") 
            
            y_offset -= 100
            c.setFont("Helvetica", 10)
            c.drawString(50, y_offset, "Términos y condiciones:")
            c.drawString(50, y_offset - 20, "1. Los productos comprados no tienen devolución.")
            c.drawString(50, y_offset - 40, "2. Conserve esta factura como comprobante de su compra.")
            c.drawString(50, y_offset - 60, "3. Para más información, visite nuestro sitio web o contacte a servicio al cliente.")
            
            c.save()
            messagebox.showinfo("Factura generada", f"Se ha generado la factura en: {factura_path}")
            
            # Abrir el PDF automáticamente según el sistema operativo
            if sys.platform == "win32":
                os.startfile(os.path.abspath(factura_path))
            else:
                # Para Linux/Mac
                import subprocess
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", factura_path])
                else:  # Linux
                    subprocess.run(["xdg-open", factura_path])
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")
                
                
                
        