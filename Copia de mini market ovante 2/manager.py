from tkinter import *
from tkinter import ttk 
from login import Login 
from login import Registro
from container import Container 
import sys
import os 

class Manager(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.configure(bg="#C6D9E3")
        self.title("mini market ovante")
        self.geometry("1100x750+120+20")
        self.resizable(False, False)

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.configure(bg="#C6D9E3")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for i in (Login, Registro, Container):
            frame = i(container, self)
            self.frames[i] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Login)
        

        self.style = ttk.Style()
        self.style.theme_use("clam")


    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()


def main():
    app = Manager()
    app.mainloop()

if __name__ == "__main__":
    main()