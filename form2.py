import os
import json
import datetime
import shutil
from tkinter import *
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from window import ObserverWindow


class MyHandler(FileSystemEventHandler):
    def __init__(self, window):
        self.window = window

    def on_modified(self, event):
        self.window.create_config()


class Application:
    def __init__(self, master=None):
        self.master = master
        self.observer_window = ObserverWindow(self.master)
        self.event_handler = MyHandler(self.observer_window)
        self.observer = Observer()
        self.settings = None
        self.settings_file = "settings.cfg"
        self.observer = None


        self.pathLbl = Label(self.master, text="Путь к папке с ключами:")
        self.pathLbl.grid(row=0, column=0)
        self.pathTxt = Entry(self.master)
        self.pathTxt.grid(row=0, column=1)
        self.pathBtn = Button(self.master, text="Выбрать", command=self.select_key_path)
        self.pathBtn.grid(row=0, column=2)

        self.issuedLbl = Label(self.master, text="Путь к папке с выданными сертификатами:")
        self.issuedLbl.grid(row=1, column=0)
        self.issuedTxt = Entry(self.master)
        self.issuedTxt.grid(row=1, column=1)
        self.issuedBtn = Button(self.master, text="Выбрать", command=self.select_issued_path)
        self.issuedBtn.grid(row=1, column=2)

        self.keyLbl = Label(self.master, text="Название файла с ключом:")
        self.keyLbl.grid(row=2, column=0)
        self.keyTxt = Entry(self.master)
        self.keyTxt.grid(row=2, column=1)
        self.issuedBtn = Button(self.master, text="Выбрать", command=self.select_ser_path)
        self.issuedBtn.grid(row=2, column=2)

        self.saveBtn = Button(self.master, text="Сохранить", command=self.update_settings)
        self.saveBtn.grid(row=3, column=0)

        self.startBtn = Button(self.master, text="Начать наблюдение", command=self.start_observer)
        self.startBtn.grid(row=3, column=1)

        self.stopBtn = Button(self.master, text="Остановить наблюдение", command=self.stop_observer)
        self.stopBtn.grid(row=3, column=2)

        self.load_settings()

    def select_key_path(self):
        path = filedialog.askdirectory()
        self.pathTxt.delete(0, END)
        self.pathTxt.insert(0, path)

    def select_ser_path(self):
        path = filedialog.askopenfilename(filetypes=[("OpenVPN files", "*.ovpn")])
        self.keyTxt.delete(0, END)  # <--- Исправление
        self.keyTxt.insert(0, path)

    def select_issued_path(self):
        path = filedialog.askdirectory()
        self.issuedTxt.delete(0, END)
        self.issuedTxt.insert(0, path)

    def start_observer(self):
        if self.observer:
            return

        key_path = self.pathTxt.get()
        if not os.path.exists(key_path):
            messagebox.showerror("Ошибка", "Папка с ключами не найдена.")
            return

        event_handler = MyHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, key_path, recursive=True)
        self.observer.start()
        messagebox.showinfo("Информация", "Наблюдение за папкой с выданными сертификатами началось.")

    def stop_observer(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            messagebox.showinfo("Информация", "Наблюдение за папкой с выданными сертификатами закончилась.")

    def create_config(self):
        issued_path = self.issuedTxt.get()
        key_name = self.keyTxt.get()

        if not os.path.exists(issued_path):
            messagebox.showerror("Ошибка", "Папка с выданными сертификатами не найдена.")
            return

        if not key_name:
            messagebox.showerror("Ошибка", "Не указано имя файла с ключом.")
            return

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        config_folder = os.path.join(issued_path, "config")
        config_path = os.path.join(config_folder, f"{current_time}.json")
        os.makedirs(config_folder, exist_ok=True)

        config = {
            "key_name": key_name,
            "issued_path": issued_path,
            "issued_time": current_time
        }

        with open(config_path, "w") as f:
            json.dump(config, f)

    def update_settings(self):
        key_path = self.pathTxt.get()
        issued_path = self.issuedTxt.get()
        key_name = self.keyTxt.get()

        if not os.path.exists(key_path):
            messagebox.showerror("Ошибка", "Папка с ключами не найдена.")
            return

        if not os.path.exists(issued_path):
            messagebox.showerror("Ошибка", "Папка с выданными сертификатами не найдена.")
            return

        if not key_name:
            messagebox.showerror("Ошибка", "Не указано имя файла с ключом.")
            return

        settings = {
            "key_path": key_path,
            "issued_path": issued_path,
            "key_name": key_name
        }

        with open(self.settings_file, "w") as f:
            json.dump(settings, f)
            messagebox.showinfo("Информация", "Настройки сохранены.")

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            self.settings = {
                "key_path": "",
                "issued_path": "",
                "key_name": ""
            }
            return

        with open(self.settings_file, "r") as f:
            self.settings = json.load(f)

        self.pathTxt.insert(0, self.settings["key_path"])
        self.issuedTxt.insert(0, self.settings["issued_path"])
        self.keyTxt.insert(0, self.settings["key_name"])

    def watch_folder(path):
        config_path = "config.cfg"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                last_path = f.readline().strip()
            if path == last_path:
                print("Path is the same as before")
                return
        else:
            last_path = ""

        with open(config_path, "w") as f:
            f.write(path)

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".key"):
                    key_path = os.path.join(root, file)
                    crt_path = os.path.join(root, file.replace(".key", ".crt"))
                    ovpn_path = os.path.join(root, file.replace(".key", ".ovpn"))
                    if os.path.exists(crt_path) and os.path.exists(key_path):
                        with open(key_path, "r") as f:
                            key = f.read()
                        with open(crt_path, "r") as f:
                            crt = f.read()
                        with open(ovpn_path, "w") as f:
                            f.write("remote\n")
                            f.write("key\n")
                            f.write(key)
                            f.write("\n")
                            f.write(crt)


if __name__ == "__main__":
    root = Tk()
    root.title("Наблюдение за папкой с выданными сертификатами")
    app = Application(master=root)
    root.mainloop()

