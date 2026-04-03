import tkinter as tk

HOST_DEFAULT = "192.168.250.101"
PORT_DEFAULT = 9000


class MainWindow(tk.Tk):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.geometry(
            f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.focus_force()

        self.host_val = tk.StringVar(value=HOST_DEFAULT)
        tk.Entry(self, textvariable=self.host_val).pack()

        self.port_val = tk.IntVar(value=PORT_DEFAULT)
        tk.Spinbox(self, textvariable=self.port_val, from_=0, to=65535).pack()

        tk.Button(self, text="connect",
                  command=self.action_connect).pack()

    def action_connect(self):
        print(f"connection to {self.host_val.get()}:{self.port_val.get()}")
