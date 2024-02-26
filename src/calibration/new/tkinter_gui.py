## Example tkinter GUI file

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo


#  multiprocessing to spawn calibration program
# from multiprocessing import Queue, Process, Pool
import multiprocessing as mp
from queue import Empty as QEmpty

import os
import time


def f(q: mp.Queue):
    for i in range(10):
        print("THREAD SLEEP #", i)
        time.sleep(0.3)
        if i % 5 == 0:
            q.put(["hello", i])


### HANDLE CLICK BUTTONS ###
# calibrate
def do_calibration():
    print("RUNNING CALIBRATION")
    q = mp.Queue()
    p = mp.Process(target=f, args=(q,))
    p.start()
    time.sleep(1)
    # v = None
    # try:
    #     v = q.get_nowait()
    # except QEmpty:
    #     print("QUEUE EMPTY")
    # else:
    #     print("QUEUE VALUE:", v)
    # p.join()


def do_select_project_dir(project_dir_var: tk.StringVar):
    print("Selecting project directory")
    dirname = filedialog.askdirectory()
    project_dir_var.set(dirname)


def do_select_output_dir(output_dir_var: tk.StringVar):
    print("Selecting output directory")
    dirname = filedialog.askdirectory()
    output_dir_var.set(dirname)


def do_select_intrinsics_dir(intrinsics_dir_var: tk.StringVar):
    print("Selecting intrinsics directory")
    dirname = filedialog.askdirectory()
    intrinsics_dir_var.set(dirname)


class MainApplication(tk.Frame):
    def __init__(self):
        # print("MASTER IS", parent)
        # super().__init__(parent)  # same as Frame.__init__
        super().__init__()

        ### create all variables ###
        self.project_dir_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value="")
        self.intrinsics_dir_var = tk.StringVar(value="")

        ### create all components ###
        # select project field
        self.project_entry_label = tk.Label(text="Select the project directory")
        self.project_entry_label.pack()
        self.project_entry = ttk.Entry(textvariable=self.project_dir_var)
        self.project_entry.pack()
        self.project_browse_button = ttk.Button(
            text="Browse",
            command=lambda: do_select_project_dir(self.project_dir_var),
        )
        self.project_browse_button.pack()

        # select output field
        self.output_entry_label = tk.Label(text="Select calibration output directory")
        self.output_entry_label.pack()
        self.output_entry = ttk.Entry(textvariable=self.output_dir_var)
        self.output_entry.pack()
        self.output_browse_btuton = ttk.Button(
            text="Browse",
            command=lambda: do_select_output_dir(self.output_dir_var),
        )
        self.output_browse_btuton.pack()

        # select intrinsics field
        self.intrinsics_entry_label = tk.Label(
            text="Select calibration output directory"
        )
        self.intrinsics_entry_label.pack()
        self.intrinsics_entry = ttk.Entry(textvariable=self.intrinsics_dir_var)
        self.intrinsics_entry.pack()
        self.intrinsics_browse_button = ttk.Button(
            text="Browse",
            command=lambda: do_select_intrinsics_dir(self.intrinsics_dir_var),
        )
        self.intrinsics_browse_button.pack()

        # calibrate button
        self.calibrate_button = tk.Button(text="Calibrate", command=do_calibration)
        self.calibrate_button.pack()

    def print_contents(self):
        print(
            f"Hi the values of things are: project_dir: {self.project_dir_var.get()}, output_dir: {self.output_dir_var.get()}, intrinsics_dir: {self.intrinsics_dir_var.get()}"
        )


x = 0


def heartbeat(root):
    def inner():
        global x
        x += 1
        print(f"Tick {x}")
        if x < 100:
            root.after(1000, heartbeat(root))

    return inner


def main():
    # set default multiprocessing start method - ONLY RUN ONCE
    mp.set_start_method("spawn")

    root = tk.Tk()
    root.title("DANNCE Calibration GUI")
    root.minsize(500, 500)
    _app = MainApplication()
    heartbeat(root)()
    root.mainloop()


if __name__ == "__main__":
    main()
