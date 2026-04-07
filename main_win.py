import tkinter as tk
from api_client import APIClient
from log_interf import LoggerInterface

HOST_DEFAULT = "192.168.250.101"
PORT_DEFAULT = 9000


class Logger(tk.Text, LoggerInterface):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.config(state=tk.DISABLED)

    def clear(self):
        self.config(state=tk.NORMAL)
        self.delete('1.0', tk.END)
        self.config(state=tk.DISABLED)

    def print(self, txt: str):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, "\n"+txt, "\n")
        self.see(tk.END)
        self.config(state=tk.DISABLED)


class MainWindow(tk.Tk):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.geometry(
            f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.focus_force()
        self.title("test communication Unilogics")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = tk.Frame(self, bg='gray2', width=50,
                          height=40, padx=3, pady=3)
        center.grid(row=1, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)

        self.host_val = tk.StringVar(value=HOST_DEFAULT)
        tk.Entry(center, textvariable=self.host_val).pack(anchor=tk.W)

        self.port_val = tk.IntVar(value=PORT_DEFAULT)
        tk.Spinbox(center, textvariable=self.port_val,
                   from_=0, to=65535).pack(anchor=tk.W)

        self.connect_button = tk.Button(center, text="connect",
                                        command=self.action_connect)
        self.connect_button.pack(anchor=tk.W)

        self.info_frame = tk.Frame(center, bg='blue', width=200, height=300)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(self.info_frame, text="clear",
                  command=self.action_clear_console).pack(anchor=tk.W)
        self.logger = Logger(master=self.info_frame)
        self.logger.pack(fill=tk.X)
        self.client = APIClient(logger=self.logger)

    def action_clear_console(self):
        self.logger.clear()

    def action_connect(self):

        if not self.client.connected():
            self.logger.print(
                f"connection to {self.host_val.get()}:{self.port_val.get()}")
            self.client.connect(self.host_val.get(), self.port_val.get())
        else:
            self.logger.print("disconnect")
            self.client.disconnect()
        if self.client.connected():
            self.connect_button.config(text="close")
        else:
            self.connect_button.config(text="connect")
