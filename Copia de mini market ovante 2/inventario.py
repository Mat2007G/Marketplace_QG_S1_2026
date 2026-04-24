import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import os


class Inventario(tk.Frame):

    def __init__(self, padre):
        super().__init__(padre)

        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()

        self.image_folder = "fotos"
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

        self.timer_articulos = None

        self.widgets()
        self.articulos_combobox()
        self.cargar_articulos()


    def widgets(self):

        canvas_articulos = tk.LabelFrame(self, text="Articulos", font="arial 14 bold", bg="#C6D9E3", fg="#1f1f1f")
        canvas_articulos.place(x=300, y=10, width=780, height=580)

        self.canvas = tk.Canvas(canvas_articulos, bg="#C6D9E3")
        self.scrollbar = tk.Scrollbar(canvas_articulos, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#C6D9E3")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        lblframe_buscar = LabelFrame(self, text="Buscar", font="arial 14 bold", bg="#C6D9E3")
        lblframe_buscar.place(x=10, y=10, width=280, height=80)

        self.comboboxbuscar = ttk.Combobox(lblframe_buscar, font="arial 12")
        self.comboboxbuscar.place(x=5, y=5, width=260, height=40)
        self.comboboxbuscar.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.comboboxbuscar.bind("<KeyRelease>", self.filtrar_articulos)

        lblframe_seleccion = LabelFrame(self, text="Selección", font="arial 14 bold", bg="#C6D9E3")
        lblframe_seleccion.place(x=10, y=95, width=280, height=190)

        self.label1 = tk.Label(lblframe_seleccion, text="Articulo:", font="arial 12", bg="#C6D9E3")
        self.label1.place(x=5, y=5)

        self.label2 = tk.Label(lblframe_seleccion, text="Precio:", font="arial 12", bg="#C6D9E3")
        self.label2.place(x=5, y=40)

        self.label3 = tk.Label(lblframe_seleccion, text="Costo:", font="arial 12", bg="#C6D9E3")
        self.label3.place(x=5, y=70)

        self.label4 = tk.Label(lblframe_seleccion, text="Stock:", font="arial 12", bg="#C6D9E3")
        self.label4.place(x=5, y=100)

        self.label5 = tk.Label(lblframe_seleccion, text="Estado:", font="arial 12", bg="#C6D9E3")
        self.label5.place(x=5, y=130)

        lblframe_botones = LabelFrame(self, text="Opciones", font="arial 14 bold", bg="#C6D9E3")
        lblframe_botones.place(x=10, y=290, width=280, height=300)

        btn1 = tk.Button(lblframe_botones, text="Agregar", font="arial 14 bold", command=self.agregar_articulo)
        btn1.place(x=20, y=20, width=180, height=40)

        btn2 = tk.Button(lblframe_botones, text="Editar", font="arial 14 bold", command=self.editar_articulo)
        btn2.place(x=20, y=80, width=180, height=40)


    def articulos_combobox(self):

        self.cur.execute("SELECT articulo FROM articulos")
        self.articulos = [row[0] for row in self.cur.fetchall()]

        self.comboboxbuscar['values'] = self.articulos


    def on_combobox_select(self, event=None):
        self.actualizar_label()


    def actualizar_label(self, event=None):

        articulo = self.comboboxbuscar.get()

        self.cur.execute(
            "SELECT articulo, precio, costo, stock, estado FROM articulos WHERE articulo=?",
            (articulo,)
        )

        resultado = self.cur.fetchone()

        if resultado:

            articulo, precio, costo, stock, estado = resultado

            self.label1.config(text=f"Articulo: {articulo}")
            self.label2.config(text=f"Precio: ${precio}")
            self.label3.config(text=f"Costo: ${costo}")
            self.label4.config(text=f"Stock: {stock}")
            self.label5.config(text=f"Estado: {estado}")
            if estado.lower() == "activo":
                self.label5.config(fg="green")
            elif estado.lower() == "inactivo":
                self.label5.config(fg="red")
            else:
                self.label5.config(fg="black")


    def filtrar_articulos(self, event):

        if self.timer_articulos:
            self.timer_articulos.cancel()

        self.timer_articulos = threading.Timer(0.5, self._filter_articulos)
        self.timer_articulos.start()


    def _filter_articulos(self):

        typed = self.comboboxbuscar.get()

        if typed == "":
            data = self.articulos
        else:
            data = [item for item in self.articulos if typed.lower() in item.lower()]

        self.comboboxbuscar['values'] = data
        self.cargar_articulos(filtro=typed)


    def cargar_articulos(self, filtro=None):

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = "SELECT articulo, precio, image_path FROM articulos"
        params = []

        if filtro:
            query += " WHERE articulo LIKE ?"
            params.append(f'%{filtro}%')

        self.cur.execute(query, params)
        articulos = self.cur.fetchall()

        # CORREGIDO: Ahora se muestra en UNA SOLA COLUMNA vertical
        row = 0

        for articulo, precio, image_path in articulos:

            # Frame contenedor para cada producto
            frame = tk.Frame(self.scrollable_frame, bg="white", relief="solid", bd=1)
            frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            frame.grid_columnconfigure(0, weight=1)

            # Frame interno para organizar contenido
            frame_interno = tk.Frame(frame, bg="white")
            frame_interno.grid(row=0, column=0, padx=10, pady=10, sticky="w")

            # Imagen (si existe)
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    image = image.resize((80, 80), Image.LANCZOS)
                    img = ImageTk.PhotoImage(image)

                    lbl_img = tk.Label(frame_interno, image=img, bg="white")
                    lbl_img.image = img
                    lbl_img.grid(row=0, column=0, padx=(0, 15))
                except:
                    pass

            # Frame para texto
            frame_texto = tk.Frame(frame_interno, bg="white")
            frame_texto.grid(row=0, column=1, sticky="w")

            tk.Label(frame_texto, text=articulo, bg="white", fg="black", font="arial 12 bold", anchor="w").pack(anchor="w")
            tk.Label(frame_texto, text=f"${precio:,.0f}", bg="white", fg="black", font="arial 11", anchor="w").pack(anchor="w")

            row += 1


    def load_image(self):

        file = filedialog.askopenfilename(filetypes=[("Imagen","*.png *.jpg *.jpeg")])

        if file:
            image = Image.open(file)
            image = image.resize((200,200), Image.LANCZOS)

            self.product_image = ImageTk.PhotoImage(image)
            self.image_path = file

            for widget in self.frameimg.winfo_children():
                widget.destroy()

            label = tk.Label(self.frameimg, image=self.product_image)
            label.pack(expand=True, fill="both")


    def agregar_articulo(self):

        top = Toplevel(self)
        top.title("Agregar Artículo")
        top.geometry("400x450")

        tk.Label(top, text="Articulo").pack()
        entry_articulo = tk.Entry(top)
        entry_articulo.pack()

        tk.Label(top, text="Precio").pack()
        entry_precio = tk.Entry(top)
        entry_precio.pack()

        tk.Label(top, text="Costo").pack()
        entry_costo = tk.Entry(top)
        entry_costo.pack()

        tk.Label(top, text="Stock").pack()
        entry_stock = tk.Entry(top)
        entry_stock.pack()

        tk.Label(top, text="Estado").pack()
        estado = ttk.Combobox(top, values=["Activo","Inactivo"])
        estado.pack()

        image_path = {"path":""}

        def cargar_imagen():

            file = filedialog.askopenfilename(filetypes=[("Imagen","*.png *.jpg *.jpeg")])

            if file:
                image_path["path"] = file
                messagebox.showinfo("Imagen","Imagen cargada")

        tk.Button(top,text="Cargar Imagen",command=cargar_imagen).pack(pady=10)

        def guardar():

            articulo = entry_articulo.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            estado_val = estado.get()

            if not articulo:
                messagebox.showerror("Error","Articulo requerido")
                return

            self.cur.execute(
                "INSERT INTO articulos (articulo,precio,costo,stock,estado,image_path) VALUES (?,?,?,?,?,?)",
                (articulo,precio,costo,stock,estado_val,image_path["path"])
            )

            self.con.commit()

            messagebox.showinfo("Guardado","Articulo agregado")

            self.articulos_combobox()
            self.cargar_articulos()

            top.destroy()

        tk.Button(top,text="Guardar",command=guardar).pack(pady=20)


    def editar_articulo(self):

        selected_item = self.comboboxbuscar.get()

        if not selected_item:
            messagebox.showerror("Error", "Selecciona un articulo para editar")
            return
        
        self.cur.execute("SELECT articulo, precio, costo, stock, estado, image_path FROM articulos WHERE articulo=?", (selected_item,))
        resultado = self.cur.fetchone()
        
        if not resultado:
            messagebox.showerror("Error", "Articulo no encontrado")
            return 
        
        top = tk.Toplevel(self)
        top.title("Editar Articulo")
        top.geometry("700x450+200+50")
        top.config(bg="#C6D9E3")
        
        (articulo, precio, costo, stock, estado, image_path) = resultado
        
        tk.Label(top, text="Articulo:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=20)
        entry_articulo = ttk.Entry(top)
        entry_articulo.place(x=120, y=20, width=250)
        entry_articulo.insert(0, articulo)
        
        tk.Label(top, text="Precio:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=60)
        entry_precio = ttk.Entry(top)
        entry_precio.place(x=120, y=60, width=250)
        entry_precio.insert(0, precio)
        
        tk.Label(top, text="Costo:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=100)
        entry_costo = ttk.Entry(top)
        entry_costo.place(x=120, y=100, width=250)
        entry_costo.insert(0, costo)
        
        tk.Label(top, text="Stock:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=140)
        entry_stock = ttk.Entry(top)
        entry_stock.place(x=120, y=140, width=250)
        entry_stock.insert(0, stock)
        
        tk.Label(top, text="Estado:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=180)
        entry_estado = ttk.Entry(top)
        entry_estado.place(x=120, y=180, width=250)
        entry_estado.insert(0, estado)
        
        self.frameimg = tk.Frame(top, bg="white", highlightbackground="gray", highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)
        
        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((200,200), Image.LANCZOS)
            self.product_image = ImageTk.PhotoImage(image)
            self.image_path = image_path
            tk.Label(self.frameimg, image=self.product_image).pack(expand=True, fill="both")
            
        btnimagen = tk.Button(top, text="Cargar Imagen", font="arial 12 bold", command=self.load_image)
        btnimagen.place(x=470, y=260, width=150, height=40)
        
        def guardar():
            nuevo_articulo = entry_articulo.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
            estado = entry_estado.get()

            if hasattr(self, 'image_path'):
                img = self.image_path
            else:
                img = image_path

            self.cur.execute(
                "UPDATE articulos SET articulo=?, precio=?, costo=?, stock=?, image_path=?, estado=? WHERE articulo=?",
                (nuevo_articulo, precio, costo, stock, img, estado, selected_item)
            )
            self.con.commit()

            self.articulos_combobox()
            self.cargar_articulos()

            top.destroy()

            messagebox.showinfo("Exito", "Articulo editado exitosamente")

        btn_guardar = tk.Button(top, text="Guardar", font="Arial 12 bold", command=guardar)
        btn_guardar.place(x=260, y=260, width=150, height=40)