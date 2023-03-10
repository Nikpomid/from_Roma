import tkinter as tk
from tkinter import ttk

import tkinter as tk

class Server:
    def __init__(self, name, address):
        self.name = name
        self.address = address

class Form2(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Выберите сервер")
        self.geometry("300x200")
        self.resizable(False, False)

        self.servers = self.load_servers_from_file("servers.txt")
        self.comboBox = tk.ttk.Combobox(self, values=[server.name for server in self.servers], state="readonly")
        self.comboBox.current(0)
        self.comboBox.pack(pady=10, padx=5)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
        self.ok_button.pack(side=tk.RIGHT, padx=5, pady=10)

    def load_servers_from_file(self, filename):
        servers = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                name, address = line.rsplit(' ', maxsplit=1)
                servers.append(Server(name, address))

        return servers

    def on_ok(self):
        server = self.servers[self.comboBox.current()]
        self.result = server.address
        self.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    form2 = Form2(root)
    form2.mainloop()
    print(form2.result)

