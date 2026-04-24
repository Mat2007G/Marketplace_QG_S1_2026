from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class Proveedor(tk.Frame):

    db_name = "database.db"

    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_proveedores()

    def widgets(self):

        self.labelframe = tk.LabelFrame(self, text="Proveedores", font="sans 20 bold", bg="#C6D9E3")
        self.labelframe.place(x=20, y=20, width=250, height=560)

        tk.Label(self.labelframe, text="Nombre:", bg="#C6D9E3").place(x=10, y=20)
        self.nombre = ttk.Entry(self.labelframe)
        self.nombre.place(x=10, y=50, width=220)

        tk.Label(self.labelframe, text="NIT:", bg="#C6D9E3").place(x=10, y=90)
        self.nit = ttk.Entry(self.labelframe)
        self.nit.place(x=10, y=120, width=220)

        tk.Label(self.labelframe, text="Teléfono:", bg="#C6D9E3").place(x=10, y=160)
        self.telefono = ttk.Entry(self.labelframe)
        self.telefono.place(x=10, y=190, width=220)

        tk.Label(self.labelframe, text="Dirección:", bg="#C6D9E3").place(x=10, y=230)
        self.direccion = ttk.Entry(self.labelframe)
        self.direccion.place(x=10, y=260, width=220)

        tk.Label(self.labelframe, text="Correo:", bg="#C6D9E3").place(x=10, y=300)
        self.correo = ttk.Entry(self.labelframe)
        self.correo.place(x=10, y=330, width=220)

        tk.Button(self.labelframe, text="Registrar", command=self.registrar).place(x=10, y=380, width=220)
        tk.Button(self.labelframe, text="Modificar", command=self.modificar).place(x=10, y=430, width=220)

        # ====== TABLA ======
        treFrame = Frame(self)
        treFrame.place(x=280, y=20, width=800, height=560)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)

        self.tre = ttk.Treeview(
            treFrame,
            yscrollcommand=scrol_y.set,
            xscrollcommand=scrol_x.set,
            columns=("ID", "Nombre", "NIT", "Teléfono", "Dirección", "Correo"),
            show="headings"
        )
        self.tre.pack(expand=True, fill=BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        self.tre.heading("ID", text="ID")
        self.tre.heading("Nombre", text="Nombre")
        self.tre.heading("NIT", text="NIT")
        self.tre.heading("Teléfono", text="Teléfono")
        self.tre.heading("Dirección", text="Dirección")
        self.tre.heading("Correo", text="Correo")

    def registrar(self):

        if not self.nombre.get() or not self.nit.get():
            messagebox.showerror("Error", "Nombre y NIT son obligatorios")
            return

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO proveedores (nombre, nit, telefono, direccion, correo) VALUES (?, ?, ?, ?, ?)",
            (self.nombre.get(), self.nit.get(), self.telefono.get(), self.direccion.get(), self.correo.get())
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Proveedor registrado")

        self.limpiar_campos()
        self.cargar_proveedores()

    def cargar_proveedores(self):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for item in self.tre.get_children():
            self.tre.delete(item)

        cursor.execute("SELECT * FROM proveedores")

        for row in cursor.fetchall():
            self.tre.insert("", "end", values=row)

        conn.close()

    def limpiar_campos(self):
        self.nombre.delete(0, END)
        self.nit.delete(0, END)
        self.telefono.delete(0, END)
        self.direccion.delete(0, END)
        self.correo.delete(0, END)

    def modificar(self):

        if not self.tre.selection():
            messagebox.showerror("Error", "Selecciona un proveedor")
            return

        item = self.tre.selection()[0]
        datos = self.tre.item(item, "values")

        id_proveedor = datos[0]
        nombre_actual = datos[1]
        nit_actual = datos[2]
        telefono_actual = datos[3]
        direccion_actual = datos[4]
        correo_actual = datos[5]

        top = Toplevel(self)
        top.title("Modificar proveedor")
        top.geometry("400x400")
        top.config(bg="#C6D9E3")

        tk.Label(top, text="Nombre:", bg="#C6D9E3").pack()
        entry_nombre = tk.Entry(top)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack()

        tk.Label(top, text="NIT:", bg="#C6D9E3").pack()
        entry_nit = tk.Entry(top)
        entry_nit.insert(0, nit_actual)
        entry_nit.pack()

        tk.Label(top, text="Teléfono:", bg="#C6D9E3").pack()
        entry_telefono = tk.Entry(top)
        entry_telefono.insert(0, telefono_actual)
        entry_telefono.pack()

        tk.Label(top, text="Dirección:", bg="#C6D9E3").pack()
        entry_direccion = tk.Entry(top)
        entry_direccion.insert(0, direccion_actual)
        entry_direccion.pack()

        tk.Label(top, text="Correo:", bg="#C6D9E3").pack()
        entry_correo = tk.Entry(top)
        entry_correo.insert(0, correo_actual)
        entry_correo.pack()

        def guardar():
            nuevo_nombre = entry_nombre.get()
            nuevo_nit = entry_nit.get()
            nuevo_tel = entry_telefono.get()
            nueva_dir = entry_direccion.get()
            nuevo_correo = entry_correo.get()

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE proveedores 
                SET nombre=?, nit=?, telefono=?, direccion=?, correo=? 
                WHERE id=?
            """, (nuevo_nombre, nuevo_nit, nuevo_tel, nueva_dir, nuevo_correo, id_proveedor))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Proveedor actualizado")

            self.cargar_proveedores()
            top.destroy()

        tk.Button(top, text="Guardar cambios", command=guardar).pack(pady=20)