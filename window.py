import tkinter as tk

from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self, window):
        self.window = window
        self.observed_objects = []

    def on_modified(self, event):
        self.window.create_config()
        self.add_observed_object(event.src_path)

    def add_observed_object(self, path):
        if path not in self.observed_objects:
            self.observed_objects.append(path)
            self.window.update_observed_objects(self.observed_objects)


class ObserverWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.observed_objects = []

        self.title("Observer")
        self.geometry("400x300")

        self.label = tk.Label(self, text="Observed objects:")
        self.label.pack()

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def update_observed_objects(self, observed_objects):
        self.observed_objects = observed_objects
        self.listbox.delete(0, tk.END)
        for path in self.observed_objects:
            self.listbox.insert(tk.END, path)



