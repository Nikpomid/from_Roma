import os
import shutil
import time
import winreg
import win32file
import win32gui
import win32con

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfilename


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OVPNConfigCreator")

        self.setPath = "settings.cfg"

        # Определение параметров окна
        self.geometry("500x400")
        self.resizable(False, False)

        # Создание и расположение виджетов на форме
        self.pathLbl = tk.Label(self, text="Выберите папку для сохранения конфигурационных файлов:")
        self.pathLbl.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.pathTxt = tk.Entry(self, width=40)
        self.pathTxt.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.pathBtn = tk.Button(self, text="Выбрать", command=self.select_path)
        self.pathBtn.grid(row=1, column=1, padx=10, pady=5)

        self.keyLbl = tk.Label(self, text="Выберите файл с закрытым ключом:")
        self.keyLbl.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.keyTxt = tk.Entry(self, width=40)
        self.keyTxt.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.keyBtn = tk.Button(self, text="Выбрать", command=self.select_key)
        self.keyBtn.grid(row=3, column=1, padx=10, pady=5)

        self.crtLbl = tk.Label(self, text="Выберите файл с сертификатом:")
        self.crtLbl.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.crtTxt = tk.Entry(self, width=40)
        self.crtTxt.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.crtBtn = tk.Button(self, text="Выбрать", command=self.select_crt)
        self.crtBtn.grid(row=5, column=1, padx=10, pady=5)

        self.startBtn = tk.Button(self, text="Запустить", command=self.start_stop)
        self.startBtn.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.closeBtn = tk.Button(self, text="Закрыть", command=self.close)
        self.closeBtn.grid(row=6, column=1, padx=10, pady=10, sticky="e")

        # Инициализация переменных
        self.form2 = None
        self.folder_to_watch = ""
        self.private_folder = ""
        self.key_file = ""
        self.crt_file = ""
        self.config_file = ""

        self.load_settings()

    def load_settings(self):
        if os.path.isfile(self.setPath):
            with open(self.setPath, "r") as f:
                settings = f.read().splitlines()
            if len(settings) == 4:
                self.pathTxt.insert(0, settings[0])
                self.keyTxt.insert(0, settings[1])
                self.crtTxt.insert(0, settings[2])
                if settings[3] == "True":
                    self.startBtn.config(text="Остановить")
                    self.watch_folder()
        else:
            self.pathTxt.insert(0, os.getcwd())



    def select_key(self):
        """Вызывается при нажатии на кнопку "Выбрать" для выбора файла закрытого ключа"""
        key_file = filedialog.askopenfilename(filetypes=[("PEM файлы", "*.pem")])
        if key_file:
            self.keyTxt.delete(0, tk.END)
            self.keyTxt.insert(0, key_file)
            self.key_file = key_file

    def select_crt(self):
        """Вызывается при нажатии на кнопку "Выбрать" для выбора файла сертификата"""
        crt_file = filedialog.askopenfilename(filetypes=[("CRT файлы", "*.crt")])
        if crt_file:
            self.crtTxt.delete(0, tk.END)
            self.crtTxt.insert(0, crt_file)
            self.crt_file = crt_file

    def close(self):
        self.master.destroy()

    def select_path(self):
        path = filedialog.askdirectory()
        self.pathVar.set(path)

    def save_settings(self):
        """Сохраняет настройки в файл settings.cfg"""
        with open(self.setPath, "w") as f:
            f.write(self.pathTxt.get() + "\n")
            f.write(self.keyTxt.get() + "\n")
            f.write(self.crtTxt.get() + "\n")
            f.write(self.private_folder + "\n")
            f.write(self.folder_to_watch + "\n")

    def start_stop(self):
        """Запускает/останавливает мониторинг папки"""
        if self.startBtn["text"] == "Запустить":
            # Проверка наличия необходимых файлов
            if not all([self.folder_to_watch, self.private_folder, self.key_file, self.crt_file, self.config_file]):
                messagebox.showerror("Ошибка", "Необходимо выбрать все файлы и папки!")
                return
            # Запуск мониторинга папки
            self.startBtn["text"] = "Остановить"
            self.watch_folder()
        else:
            # Остановка мониторинга папки
            self.startBtn["text"] = "Запустить"
            self.stop_watching()

    class Watcher:
        """
        A class to watch for file changes in a directory
        """

        def __init__(self, folder_to_watch, private_folder, key_file, crt_file, config_file):
            self.folder_to_watch = folder_to_watch
            self.private_folder = private_folder
            self.key_file = key_file
            self.crt_file = crt_file
            self.config_file = config_file

            self.hDir = win32file.CreateFile(
                folder_to_watch,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )

        def watch(self):
            """
            Watch for file changes in the directory
            """
            results = win32file.ReadDirectoryChangesW(
                self.hDir,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                None,
                None
            )

            for action, file in results:
                full_filename = os.path.join(self.folder_to_watch, file)

                if action == FILE_ACTION_MODIFIED and full_filename == self.config_file:
                    self.update_config()
                    messagebox.showinfo("OVPNConfigCreator", "Конфигурационный файл обновлен")

        def update_config(self):
            """
            Update the configuration file with the current private key and certificate file
            """
            with open(self.config_file, "r") as f:
                config_data = f.read()

            with open(self.key_file, "r") as f:
                key_data = f.read()

            with open(self.crt_file, "r") as f:
                crt_data = f.read()

            # Replace the private key and certificate placeholders in the configuration file with actual data
            config_data = config_data.replace("<PRIVATE_KEY>", key_data)
            config_data = config_data.replace("<CERTIFICATE>", crt_data)

            # Write the updated configuration file back to disk
            with open(self.config_file, "w") as f:
                f.write(config_data)

            # Copy the private key and certificate files to the OpenVPN config directory
            shutil.copy2(self.key_file, self.private_folder)
            shutil.copy2(self.crt_file, self.private_folder)

    def stop_watching(self):
        """Останавливает мониторинг папки"""
        pass

    def stop_watching(self):
        """Останавливает мониторинг папки"""
        # очистка переменных
        self.folder_to_watch = ""
        self.private_folder = ""
        self.key_file = ""
        self.crt_file = ""
        self.config_file = ""

        # закрытие дескриптора отслеживания
        win32file.FindCloseChangeNotification(self.change_handle)

        # удаление хука на событие окна
        win32gui.UnhookWindowsHookEx(self.hook)

        # вывод сообщения об остановке мониторинга
        messagebox.showinfo("Остановка мониторинга", "Мониторинг папки остановлен.")


if __name__ == "__main__":
    app = App()
    app.mainloop()



