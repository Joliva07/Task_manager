import tkinter as tk
from tkinter import messagebox
import threading
import time
import queue

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("925x400")

        self.process_queue_1 = queue.Queue()
        self.process_queue_2 = queue.Queue()
        self.processes_1 = []
        self.processes_2 = []
        self.lock_1 = threading.Lock()
        self.lock_2 = threading.Lock()

        self.frame_1 = tk.Frame(self.root)
        self.frame_1.pack(side=tk.LEFT, padx=10, pady=10)

        self.frame_2 = tk.Frame(self.root)
        self.frame_2.pack(side=tk.RIGHT, padx=10, pady=10)

        self.label_1 = tk.Label(self.frame_1, text="Procesos (FIFO)")
        self.label_1.pack()

        self.listbox_1 = tk.Listbox(self.frame_1, width=30, height=15)
        self.listbox_1.pack()

        self.label_2 = tk.Label(self.frame_2, text="Procesos (LIFO)")
        self.label_2.pack()

        self.listbox_2 = tk.Listbox(self.frame_2, width=30, height=15)
        self.listbox_2.pack()

        self.process_name_entry = tk.Entry(self.root, width=20)
        self.process_name_entry.pack(side=tk.LEFT, padx=5)
        self.process_time_entry = tk.Entry(self.root, width=10)
        self.process_time_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_button = tk.Button(self.root, text="Agregar", command=self.add_process)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.root, text="Eliminar", command=self.remove_process)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.fifo_button = tk.Button(self.root, text="FIFO", command=self.run_fifo)
        self.fifo_button.pack(side=tk.LEFT, padx=5)

        self.lifo_button = tk.Button(self.root, text="LIFO", command=self.run_lifo)
        self.lifo_button.pack(side=tk.LEFT, padx=5)

        self.compare_button = tk.Button(self.root, text="Comparacion", command=self.run_comparison)
        self.compare_button.pack(side=tk.LEFT, padx=5)

    def add_process(self):
        process_name = self.process_name_entry.get()
        process_time = self.process_time_entry.get()
        if process_name and process_time:
            self.process_queue_1.put((process_name, int(process_time)))
            self.process_queue_2.put((process_name, int(process_time)))
            self.lock_1.acquire()
            self.lock_2.acquire()
            self.processes_1.append((process_name, int(process_time)))
            self.processes_2.insert(0, (process_name, int(process_time)))
            self.update_listbox(self.listbox_1, self.processes_1)
            self.update_listbox(self.listbox_2, self.processes_2)
            self.lock_1.release()
            self.lock_2.release()
            self.process_name_entry.delete(0, tk.END)
            self.process_time_entry.delete(0, tk.END)

    def remove_process(self):
        if self.listbox_1.curselection():
            index = self.listbox_1.curselection()[0]
            self.lock_1.acquire()
            self.listbox_1.delete(index)
            del self.processes_1[index]
            self.lock_1.release()
        elif self.listbox_2.curselection():
            index = self.listbox_2.curselection()[0]
            self.lock_2.acquire()
            self.listbox_2.delete(index)
            del self.processes_2[index]
            self.lock_2.release()
        else:
            messagebox.showwarning("Atención", "Selecciona un proceso para eliminar.")

    def run_fifo(self):
        if not self.process_queue_1.empty():
            threading.Thread(target=self.run_algorithm, args=(self.process_queue_1, self.listbox_1, self.processes_1, self.lock_1, "FIFO")).start()

    def run_lifo(self):
        if not self.process_queue_2.empty():
            threading.Thread(target=self.run_algorithm, args=(self.process_queue_2, self.listbox_2, self.processes_2, self.lock_2, "LIFO")).start()

    def run_comparison(self):
        if not self.process_queue_1.empty() and not self.process_queue_2.empty():
            threading.Thread(target=self.run_algorithm, args=(self.process_queue_1, self.listbox_1, self.processes_1, self.lock_1, "FIFO")).start()
            threading.Thread(target=self.run_algorithm, args=(self.process_queue_2, self.listbox_2, self.processes_2, self.lock_2, "LIFO")).start()

    def run_algorithm(self, process_queue, listbox, processes, lock, algorithm):
        while not process_queue.empty():
            process = process_queue.get()
            process_name, process_time = process
            time.sleep(process_time)
            lock.acquire()
            if algorithm == "FIFO":
                del processes[0]
            elif algorithm == "LIFO":
                del processes[-1]
            self.update_listbox(listbox, processes)
            lock.release()

    def update_listbox(self, listbox, processes):
        listbox.delete(0, tk.END)
        for item in processes:
            listbox.insert(tk.END, f"{item[0]} - {item[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
