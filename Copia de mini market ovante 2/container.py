from tkinter import *
import tkinter as tk
from ventas import Ventas
from inventario import Inventario  # DESCOMENTADO
from clientes import Clientes      # DESCOMENTADO
from pedidos import Pedidos        # DESCOMENTADO
from proveedor import Proveedor    # DESCOMENTADO
from informacion import Informacion # DESCOMENTADO

import sys
import os


class Container(Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador

        self.place(x=0, y=0, width=1100, height=750)

        self.frames = {}
        self.buttons = []

        # PRIMERO: Crear los frames de contenido (detrás)
        for i in (Ventas, Inventario, Clientes, Pedidos, Proveedor, Informacion):
            frame = i(self)
            self.frames[i] = frame

            frame.config(
                bg="#C6D9E3",
                highlightbackground="gray",
                highlightthickness=1
            )

            frame.place(x=0, y=40, width=1100, height=710)

        # SEGUNDO: Crear los botones (encima)
        self.widgets()

        # Mostrar Ventas al inicio
        self.show_frames(Ventas)

    def show_frames(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def ventas(self):
        print("Cambiando a Ventas")  # Para depurar
        self.show_frames(Ventas)

    def inventario(self):
        print("Cambiando a Inventario")  # Para depurar
        self.show_frames(Inventario)

    def clientes(self):
        print("Cambiando a Clientes")  # Para depurar
        self.show_frames(Clientes)

    def pedidos(self):
        print("Cambiando a Pedidos")  # Para depurar
        self.show_frames(Pedidos)

    def proveedor(self):
        print("Cambiando a Proveedor")  # Para depurar
        self.show_frames(Proveedor)

    def informacion(self):
        print("Cambiando a Información")  # Para depurar
        self.show_frames(Informacion)

    def widgets(self):
        # Frame para los botones
        frame2 = tk.Frame(self)
        frame2.place(x=0, y=0, width=1100, height=40)
        frame2.lift()  # Asegurar que los botones estén encima

        self.btn_ventas = Button(
            frame2, fg="black", text="Ventas",
            font="sans 16 bold", command=self.ventas
        )
        self.btn_ventas.place(x=0, y=0, width=184, height=40)

        self.btn_inventario = Button(
            frame2, fg="black", text="Inventario",
            font="sans 16 bold", command=self.inventario
        )
        self.btn_inventario.place(x=184, y=0, width=184, height=40)

        self.btn_clientes = Button(
            frame2, fg="black", text="Clientes",
            font="sans 16 bold", command=self.clientes
        )
        self.btn_clientes.place(x=369, y=0, width=184, height=40)

        self.btn_pedidos = Button(
            frame2, fg="black", text="Pedidos",
            font="sans 16 bold", command=self.pedidos
        )
        self.btn_pedidos.place(x=554, y=0, width=184, height=40)

        self.btn_proveedor = Button(
            frame2, fg="black", text="Proveedor",
            font="sans 16 bold", command=self.proveedor
        )
        self.btn_proveedor.place(x=739, y=0, width=184, height=40)

        self.btn_informacion = Button(
            frame2, fg="black", text="Informacion",
            font="sans 16 bold", command=self.informacion
        )
        self.btn_informacion.place(x=923, y=0, width=184, height=40)

        self.buttons = [
            self.btn_ventas,
            self.btn_inventario,
            self.btn_clientes,
            self.btn_pedidos,
            self.btn_proveedor,
            self.btn_informacion
        ]