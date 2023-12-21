import tkinter as tk
from tkinter import ttk

def open_new_tab():
    new_tab = ttk.Frame(notebook)
    notebook.add(new_tab, text="New Tab")
    label = tk.Label(new_tab, text="This is a new tab")
    label.pack(padx=20, pady=20)

root = tk.Tk()
root.title("Simple Browser")
root.geometry("600x550")

notebook = ttk.Notebook(root, width=600, height=500)
notebook.pack()

button = tk.Button(root, text="New Tab", command=open_new_tab)
button.pack(side=tk.BOTTOM)

root.mainloop()
