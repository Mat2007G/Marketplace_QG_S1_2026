from tkinter import *
import tkinter as tk

class Informacion(Frame):

    def __init__(self, padre):
        super().__init__(padre)
        self.config(bg="#a9b7c0")
        self.widgets()

    def widgets(self):

        # ===== TÍTULO =====
        Label(self, text="Información de la Empresa",
              font=("Arial", 18, "bold"),
              bg="#a9b7c0", fg="black").pack(pady=15)

        # ===== DESCRIPCIÓN GENERAL =====
        Label(self,
              text="Consulta información relevante de la empresa de forma rápida.\n"
                   "Usa el buscador para ver los datos.",
              font=("Arial", 11),
              bg="#a9b7c0", fg="black",
              justify="center").pack(pady=10)

        # ===== AYUDA AL USUARIO =====
        Label(self,
              text="Puedes buscar: bogota, boyaca, telefono, correo, empresa",
              bg="#a9b7c0", fg="black").pack(pady=5)

        # ===== BUSCADOR =====
        Label(self, text="Buscar información:",
              bg="#a9b7c0", fg="black").pack()

        self.buscador = Entry(self, width=30)
        self.buscador.pack(pady=5)

        Button(self, text="Consultar", command=self.consultar).pack(pady=10)

        # ===== RESULTADO =====
        self.resultado = Label(self, text="",
                               bg="#a9b7c0", fg="black",
                               font=("Arial", 11),
                               justify="center")
        self.resultado.pack(pady=15)

    # ===== FUNCIÓN =====
    def consultar(self):
        texto = self.buscador.get().lower()

        if "bogota" in texto:
            self.resultado.config(text=
                "BOGOTÁ, D.C\n"
                "Cra. 7 # 180 – 75 Mod 2 Loc 5, CODABAS\n"
                "Tel: 601 6742311 / 601 5750138\n"
                "Tel: 601 6724971 / 316 8348064")

        elif "boyaca" in texto:
            self.resultado.config(text=
                "BOYACÁ\n"
                "Tel: 322 9421445 / 315 3364459\n"
                "Correo: infoboyaca@ovante-distribuciones.com")

        elif "correo" in texto:
            self.resultado.config(text=
                "info@ovante-distribuciones.com")

        elif "telefono" in texto or "tel" in texto:
            self.resultado.config(text=
                "601 6742311 / 316 8348064")

        elif "empresa" in texto or "ovante" in texto:
            self.resultado.config(text=
                "Ovante S.A.S es una empresa dedicada a la distribución\n"
                "de productos, enfocada en brindar un servicio eficiente\n"
                "y facilitar las actividades comerciales de sus clientes.")

        else:
            self.resultado.config(text="No se encontró información.")