import json
import os
import pickle
import threading
import time
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, ttk
from tkinter.simpledialog import askstring
import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import Image, ImageGrab


class OperationList:
    def __init__(self, root, parent, list_name="NewOperation"):

        self.file_path = "NewOperation.data"  #默认的读取文件位置

        self.pstart = None
        self.pend = None
        self.chosen_index = None
        self.path_position = None
        self.root = root
        self.parent = parent
        self.notebook = self.parent.main.notebook
        self.scroll_time = None
        self.wait_time = None
        self.key_position = None
        self.click_position = None

        self.setting_window = tk.Toplevel(self.root)
        self.setting_window.title("操作设置")
        self.setting_window.lift()
        self.setting_window.focus_set()
        self.setting_window.geometry("400x300")

        self.list_name = list_name
        self.file_name = f"{list_name}.data"

        self.operations = self.load_operations()
        if not self.operations:
            print("新建NewOperation")
            self.add_default_operations()

        self.add_operation_button = tk.Button(self.setting_window, text="添加操作",
                                              command=self.show_add_operation_options)
        self.add_operation_button.pack(pady=5)

        self.modify_operation_button = tk.Button(self.setting_window, text="修改操作",
                                                 command=self.modify_selected_operation)
        self.modify_operation_button.pack(pady=5)

        self.delete_operation_button = tk.Button(self.setting_window, text="删除操作",
                                                 command=self.delete_selected_operation)
        self.delete_operation_button.pack(pady=5)

        self.operation_listbox = tk.Listbox(self.setting_window, selectmode="single", height=5, width=40)

        self.operation_listbox.pack(pady=5)

        self.populate_operation_list()

        self.op_bar = tk.Menu(self.setting_window)

        self.op_menu = tk.Menu(self.op_bar, tearoff=0)
        self.op_menu.add_command(label="保存操作列表", command=self.save_all_operations)
        self.op_menu.add_command(label="读取操作列表", command=self.load_all_operations)

        self.op_bar.add_cascade(label="操作列表", menu=self.op_menu)

        self.setting_window.config(menu=self.op_bar)

    def save_all_operations(self):
        file_path = filedialog.asksaveasfilename(initialdir=os.path.dirname(self.file_path),
                                                 initialfile=os.path.basename(self.file_path),
                                                 title="保存操作列表", defaultextension=".data",
                                                 filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        self.file_path = file_path
        if file_path:
            with open(file_path, 'wb') as file:
                pickle.dump(self.operations, file)
            with open(file_path, 'rb') as file:
                self.operations = pickle.load(file)
                self.populate_operation_list()
                self.set_file_path(file_path)
                self.setting_window.lift()
                self.setting_window.focus_set()
                self.parent.operation_full_filename = file_path
                self.parent.operation_filename = os.path.basename(file_path)
                self.parent.save_default_script(self.parent.file_path)

    def save_default_operations(self, file_path):
        self.file_path = file_path
        if file_path:
            with open(file_path, 'wb') as file:
                pickle.dump(self.operations, file)
            with open(file_path, 'rb') as file:
                self.operations = pickle.load(file)
                self.set_file_path(file_path)
                self.setting_window.lift()
                self.setting_window.focus_set()
                self.parent.operation_full_filename = file_path
                self.parent.operation_filename = os.path.splitext(os.path.basename(file_path))[0]
                self.parent.save_default_script(self.parent.file_path)
                self.parent.load_all_script()

    def load_all_operations(self):
        file_path = filedialog.askopenfilename(initialdir=os.path.dirname(self.file_path),
                                               initialfile=os.path.basename(self.file_path),
                                               title="读取操作列表",
                                               filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        self.file_path = file_path
        if file_path:
            with open(file_path, 'rb') as file:
                self.operations = pickle.load(file)
                self.set_file_path(file_path)
                self.setting_window.lift()
                self.setting_window.focus_set()
                self.parent.operation_full_filename = file_path
                self.parent.operation_filename = os.path.splitext(os.path.basename(file_path))[0]
                self.parent.save_default_script(self.parent.file_path)
                self.parent.load_all_script()

    def destroy_self(self):
        self.setting_window.destroy()

    def show_add_operation_options(self, position=tk.END):
        self.add_options_window = tk.Toplevel(self.setting_window)
        self.add_options_window.title("添加操作选项")
        self.add_options_window.lift()
        self.add_options_window.focus_set()
        self.add_options_window.geometry("400x300")
        left_frame = tk.Frame(self.add_options_window)
        left_frame.pack(side=tk.LEFT, padx=10)

        wait_button = tk.Button(left_frame, text="等待操作",
                                command=lambda: self.add_wait_operation_window(position=position))
        wait_button.pack(pady=5)

        keyboard_button = tk.Button(left_frame, text="键盘操作",
                                    command=lambda: self.add_keyboard_operation_window(position=position))
        keyboard_button.pack(pady=5)

        mouse_button = tk.Button(left_frame, text="鼠标操作",
                                 command=lambda: self.add_mouse_operation_window(position=position))
        mouse_button.pack(pady=5)

        scroll_button = tk.Button(left_frame, text="滚轮操作",
                                  command=lambda: self.add_scroll_operation_window(position=position))
        scroll_button.pack(pady=5)

        # 右边三个按钮
        right_frame = tk.Frame(self.add_options_window)
        right_frame.pack(side=tk.RIGHT, padx=10)

        pathfinding_button = tk.Button(right_frame, text="自动寻路",
                                       command=lambda: self.add_pathfinding_operation_window(position=position))
        pathfinding_button.pack(pady=5)

        continue_scan_button = tk.Button(right_frame, text="拖动操作",
                                      command=lambda: self.add_drag_operation_window(position=position))
        continue_scan_button.pack(pady=5)

        start_scan_button = tk.Button(right_frame, text="开启扫描",
                                      command=lambda: self.add_start_operation_window(position=position))
        start_scan_button.pack(pady=5)

        close_scan_button = tk.Button(right_frame, text="关闭扫描",
                                      command=lambda: self.add_close_operation_window(position=position))
        close_scan_button.pack(pady=5)



    def set_file_path(self, file_path):
        self.file_path = file_path
        list_name = os.path.splitext(os.path.basename(file_path))[0]
        self.list_name = list_name
        self.file_name = f"{list_name}.data"
        self.operations = self.load_operations()
        self.populate_operation_list()

    def load_operations(self):
        try:
            with open(self.file_path, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    def save_operations(self):
        with open(self.file_path, "wb") as file:
            pickle.dump(self.operations, file)

    def add_default_operations(self):
        default_operations = ["键盘操作：按键位置 - p", "等待：400ms", "键盘操作：按键位置 - enter"]
        self.operations = default_operations
        self.save_operations()

    def add_start_operation(self, chosen_index, position):
        self.operation_listbox.insert(position, f"开启：{chosen_index}号扫描")
        self.operations.append(f"开启：{chosen_index}号扫描")
        self.save_operations()

    def add_close_operation(self, chosen_index, position):
        self.operation_listbox.insert(position, f"关闭：{chosen_index}号扫描")
        self.operations.append(f"关闭：{chosen_index}号扫描")
        self.save_operations()

    def add_drag_operation(self, pstart, pend, position):
        self.operation_listbox.insert(position, f"拖动：({pstart},{pend})")
        self.operations.append(f"拖动：({pstart},{pend})")
        self.save_operations()

    def add_pathfinding_operation(self, pathfinding_loc, position):
        self.operation_listbox.insert(position, f"寻路：{pathfinding_loc}")
        self.operations.append(f"寻路：{pathfinding_loc}")
        self.save_operations()

    def add_wait_operation(self, wait_time, position):
        self.operation_listbox.insert(position, f"等待：{wait_time}ms")
        self.operations.append(f"等待：{wait_time}ms")
        self.save_operations()

    def add_scroll_operation(self, scroll_time, position):
        self.operation_listbox.insert(position, f"滚轮：{scroll_time}步")
        self.operations.append(f"滚轮：{scroll_time}步")
        self.save_operations()

    def add_keyboard_operation(self, key_position, position):
        self.operation_listbox.insert(position, f"键盘操作：按键位置 - {key_position}")
        self.operations.append(f"键盘操作：按键位置 - {key_position}")
        self.save_operations()

    def add_mouse_operation(self, click_position, position):
        self.operation_listbox.insert(position, f"鼠标操作：点击位置 - {click_position}")
        self.operations.append(f"鼠标操作：点击位置 - {click_position}")
        self.save_operations()

    def set_close_operation(self, chosen_index, position):
        self.chosen_index = chosen_index
        self.add_close_operation(self.chosen_index, position=position)

    def set_start_operation(self, chosen_index, position):
        self.chosen_index = chosen_index
        self.add_start_operation(self.chosen_index, position=position)

    def set_darg_operation(self, pstart, pend, position):
        self.pstart = pstart
        self.pend = pend
        self.add_drag_operation(self.pstart, self.pend, position=position)

    def set_pathfinding_loc(self, path_position, position):
        self.path_position = path_position
        self.add_pathfinding_operation(self.path_position, position=position)

    def set_wait_time(self, wait_time, position):
        self.wait_time = wait_time
        self.add_wait_operation(self.wait_time, position=position)

    def set_scroll_time(self, scroll_time, position):
        self.scroll_time = scroll_time
        self.add_scroll_operation(self.scroll_time, position=position)

    def set_key_position(self, key_position, position):
        self.key_position = key_position
        self.add_keyboard_operation(self.key_position, position=position)

    def set_click_position(self, click_position, position):
        self.click_position = click_position
        self.add_mouse_operation(self.click_position, position=position)

    def add_close_operation_window(self, position):
        close_window = tk.Toplevel(self.setting_window)
        close_window.title("关闭扫描")
        close_window.geometry("400x300")
        close_window.lift()
        close_window.focus_set()
        self.add_options_window.destroy()

        tab_names = [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]

        close_label = tk.Label(close_window, text="请选择需要操作的标签：")
        close_label.pack(pady=5)

        selected_tab = tk.StringVar(value=tab_names[0])
        tab_combobox = ttk.Combobox(close_window, textvariable=selected_tab, values=tab_names, state="readonly")
        tab_combobox.pack()

        def confirm_selection():
            chosen_index = tab_combobox.current()
            self.set_close_operation(chosen_index, position=position)
            close_window.destroy()

        confirm_button = tk.Button(close_window, text="确定", command=confirm_selection)
        confirm_button.pack(pady=5)

    def add_drag_operation_window(self, position):
        self.setting_window.iconify()
        self.parent.main.iconify()
        pstart = None
        pend = None
        drag_window = tk.Toplevel(self.setting_window)
        drag_window.attributes('-alpha', 0.2)  # Set transparency
        drag_window.attributes('-fullscreen', True)  # Set fullscreen
        drag_window.title("继续扫描")
        drag_window.wm_attributes('-topmost', 1)
        self.add_options_window.destroy()
        canvas = tk.Canvas(drag_window)
        canvas.pack(fill="both", expand=True)

        def record_start_position(event):
            nonlocal pstart  # Use nonlocal to modify the pstart variable in the outer scope
            pstart = (event.x, event.y)

        def draw_drag_line(event):
            canvas.delete("all")
            if pstart is not None:
                canvas.create_line(pstart[0], pstart[1], event.x, event.y, fill='red', width=5)

        def record_end_position(event):
            nonlocal pend
            pend = (event.x, event.y)
            self.set_darg_operation(pstart, pend, position=position)
            self.parent.main.deiconify()
            self.setting_window.deiconify()
            time.sleep(0.2)
            drag_window.destroy()

        drag_window.bind("<Button-1>", record_start_position)  # Record start position
        drag_window.bind("<B1-Motion>", draw_drag_line)  # Draw drag line
        drag_window.bind("<ButtonRelease-1>", record_end_position)  # Record end position

        drag_window.focus_set()

    def add_start_operation_window(self, position):
        start_window = tk.Toplevel(self.setting_window)
        start_window.title("开始扫描")
        start_window.geometry("400x300")
        start_window.lift()
        start_window.focus_set()
        self.add_options_window.destroy()

        tab_names = [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]

        start_label = tk.Label(start_window, text="请选择需要操作的标签：")
        start_label.pack(pady=5)

        selected_tab = tk.StringVar(value=tab_names[0])
        tab_combobox = ttk.Combobox(start_window, textvariable=selected_tab, values=tab_names, state="readonly")
        tab_combobox.pack()

        def confirm_selection():
            chosen_index = tab_combobox.current()
            self.set_start_operation(chosen_index, position=position)
            start_window.destroy()

        confirm_button = tk.Button(start_window, text="确定", command=confirm_selection)
        confirm_button.pack(pady=5)

    def add_pathfinding_operation_window(self, position):
        pathfinding_window = tk.Toplevel(self.setting_window)
        pathfinding_window.title("自动寻路")
        pathfinding_window.geometry("400x300")
        pathfinding_window.lift()
        pathfinding_window.focus_set()
        self.add_options_window.destroy()

        def validate_input(entry):
            if entry.isdigit() or (entry.startswith('-') and entry[1:].isdigit()):
                return True
            else:
                return False

        def handle_confirm_click(x_entry, y_entry):
            if validate_input(x_entry.get()) and validate_input(y_entry.get()):
                x_value = int(x_entry.get())
                y_value = int(y_entry.get())
                self.set_pathfinding_loc((x_value, y_value), position=position)
                pathfinding_window.destroy()

        x_label = tk.Label(pathfinding_window, text="x（正值为＋）：")
        x_label.pack(pady=5)
        x_entry = tk.Entry(pathfinding_window)
        x_entry.pack(pady=5)

        y_label = tk.Label(pathfinding_window, text="y（正值为＋）：")
        y_label.pack(pady=5)
        y_entry = tk.Entry(pathfinding_window)
        y_entry.pack(pady=5)

        pathfinding_button = tk.Button(pathfinding_window, text="确认",
                                       command=lambda: handle_confirm_click(x_entry, y_entry))
        pathfinding_button.pack(pady=5)

    def add_wait_operation_window(self, position):
        wait_window = tk.Toplevel(self.setting_window)
        wait_window.title("等待时间")
        wait_window.geometry("400x300")
        wait_window.lift()
        wait_window.focus_set()
        self.add_options_window.destroy()
        wait_label = tk.Label(wait_window, text="请输入等待时间（毫秒）：")
        wait_label.pack(pady=5)
        wait_entry = tk.Entry(wait_window)
        wait_entry.pack(pady=5)
        wait_button = tk.Button(wait_window, text="确认",
                                command=lambda: [self.set_wait_time(int(wait_entry.get()), position=position),
                                                 wait_window.destroy()])
        wait_button.pack(pady=5)

    def add_scroll_operation_window(self, position):
        scroll_window = tk.Toplevel(self.setting_window)
        scroll_window.title("滚轮操作")
        scroll_window.geometry("400x300")
        scroll_window.lift()
        scroll_window.focus_set()
        self.add_options_window.destroy()
        scroll_label = tk.Label(scroll_window, text="请输入滚轮步数（正数向上）：")
        scroll_label.pack(pady=5)
        scroll_entry = tk.Entry(scroll_window)
        scroll_entry.pack(pady=5)
        scroll_button = tk.Button(scroll_window, text="确认",
                                  command=lambda: [self.set_scroll_time(int(scroll_entry.get()), position=position),
                                                   scroll_window.destroy()])
        scroll_button.pack(pady=5)

    def add_keyboard_operation_window(self, position):
        keyboard_window = tk.Toplevel(self.setting_window)
        keyboard_window.title("键盘操作")
        keyboard_window.geometry("400x300")
        keyboard_window.lift()
        keyboard_window.focus_set()
        self.add_options_window.destroy()
        keyboard_label = tk.Label(keyboard_window, text="请按下一个键：")
        keyboard_label.pack(pady=5)

        def record_key_press(event):
            if event.keysym == "Return":
                self.set_key_position("enter", position=position)
            else:
                self.set_key_position(event.keysym, position=position)
            keyboard_window.destroy()

        keyboard_window.bind("<Key>", record_key_press)

    def add_mouse_operation_window(self, position):
        self.setting_window.iconify()
        self.parent.main.iconify()
        self.add_options_window.destroy()
        mouse_window = tk.Toplevel(self.setting_window)
        mouse_window.attributes('-alpha', 0.3)  # Set transparency
        mouse_window.attributes('-fullscreen', True)  # Set fullscreen
        mouse_window.title("鼠标操作")
        mouse_label = tk.Label(mouse_window, text="请在此窗口点击一个位置：")
        mouse_label.pack(pady=5)
        mouse_window.wm_attributes('-topmost', 1)

        def record_click_position(event):
            click_position = f"({event.x}, {event.y})"
            self.set_click_position(click_position, position=position)
            self.parent.main.deiconify()
            self.setting_window.deiconify()
            time.sleep(0.2)
            mouse_window.destroy()

        mouse_window.bind("<Button-1>", record_click_position)

    def modify_selected_operation(self):
        selected_index = self.operation_listbox.curselection()
        if selected_index:
            new_operation_position = selected_index[0]
            del self.operations[new_operation_position]
            self.show_add_operation_options(position=new_operation_position)
            self.save_operations()
            self.populate_operation_list()

    def delete_selected_operation(self):
        selected_index = self.operation_listbox.curselection()
        if selected_index:
            del self.operations[selected_index[0]]
            self.save_operations()
            self.populate_operation_list()

    def execute_operations(self):
        for operation in self.operations:
            if operation.startswith("等待"):
                wait_time = int(operation.split("：")[1].strip("ms"))
                time.sleep(wait_time / 1000)  # Convert milliseconds to seconds and wait
            elif operation.startswith("寻路"):
                pathfinding_loc = (operation.split("：")[1])
                path = eval(pathfinding_loc)
                max_loc = self.parent.max_loc
                center_x = int((max_loc[0][0] + max_loc[1][0]) / 2)
                center_y = int((max_loc[0][1] + max_loc[1][1]) / 2)
                pyautogui.click(center_x + int(path[0]), center_y + int(path[1]))
            elif operation.startswith("滚轮"):
                scroll_time = int(operation.split("：")[1].strip("步"))
                pyautogui.scroll(scroll_time)  # 执行滚轮
            elif operation.startswith("键盘操作"):
                key_position = operation.split(" - ")[1]
                pyautogui.press(key_position)  # Simulate keyboard press
            elif operation.startswith("鼠标操作"):
                click_position = operation.split(" - ")[1]
                x, y = map(int, click_position.strip("()").split(","))
                pyautogui.click(x, y)
            elif operation.startswith("开启"):
                chosen_index = int(operation.split("：")[1].strip("号扫描"))
                self.notebook.select(chosen_index)  # 选择对应的标签页
                selected_child_frame = self.notebook.nametowidget(self.notebook.select())
                selected_child_frame.start_scanning()
            elif operation.startswith("关闭"):
                chosen_index = int(operation.split("：")[1].strip("号扫描"))
                self.notebook.select(chosen_index)
                selected_child_frame = self.notebook.nametowidget(self.notebook.select())
                selected_child_frame.stop_scanning()
                selected_child_frame.scanning_status_label.config(text="未开始扫描")
            elif operation.startswith("拖动"):
                positions = eval(operation.split("：")[1])  # 获取拖动的坐标信息并转换为元组
                start_pos, end_pos = positions  # 解析起始位置和结束位置的坐标
                pyautogui.moveTo(start_pos[0], start_pos[1])  # 将鼠标移动到起始位置
                pyautogui.dragTo(end_pos[0], end_pos[1], duration=0.4)
    pass

    def populate_operation_list(self):
        self.operation_listbox.delete(0, tk.END)  # Clear the listbox
        for operation in self.operations:
            self.operation_listbox.insert(tk.END, operation)


class ImageScannerApp(ttk.Frame):
    def __init__(self, master, main, list_name="NewScript"):
        super().__init__(master)

        self.image_path = None
        self.start_y = None   #拖动框选的开始位置
        self.start_x = None
        self.end_y = None  # 拖动框选的开始位置
        self.end_x = None
        self.max_loc = None
        self.scan_thread = None
        self.master = master  # 本页面（notebook）的设置
        self.main = main  # 主页面的设置

        # 参数的初始化
        self.operation_full_filename = "NewOperation.data"
        self.file_path = "NewScript.data"
        self.operation_filename = "NewOperation"
        self.list_name = list_name  # 读取文件名称，list_name是默认读取名
        self.file_name = f"{list_name}.data"

        self.max_loops = None

        self.custom_font = tkFont.Font(family="SimHei", size=12, weight="bold")
        style = ttk.Style()
        style.configure("Dashed.TFrame", borderwidth=10, bordercolor="black", relief="solid", padding=5)

        self.scanning = False  # 是否扫描

        self.manual_selection_coordinates = None  # 框选的扫描

        self.grab_photo = False

        # 左侧的部分界面
        left_frame = ttk.Frame(self, style="Dashed.TFrame")
        left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=50)

        self.scanning_status_label = tk.Label(left_frame, text="未开始扫描", fg="red")
        self.scanning_status_label.pack(pady=10, padx=10)

        self.scan_location_label = tk.Label(left_frame, text="扫描位置：未知")  # 新增的Label用于显示扫描位置
        self.scan_location_label.pack(pady=50, padx=10)

        # 中间的部分界面
        middle_frame = ttk.Frame(self, style="Dashed.TFrame")
        middle_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=50)

        self.target_image_path_label = tk.Label(middle_frame, text="目标图片路径:")
        self.target_image_path_label.pack(padx=10, pady=10)

        self.target_image_path = tk.Entry(middle_frame)
        self.target_image_path.pack(padx=10, pady=10)

        self.browse_button = tk.Button(middle_frame, text="浏览图片", command=self.browse_target_image)
        self.browse_button.pack(pady=5)

        self.manual_select_button = tk.Button(middle_frame, text="手动框选", command=self.open_manual_selection_window)
        self.manual_select_button.pack(pady=5)

        self.capture_button = tk.Button(middle_frame, text="一键截图", command=self.start_grab_window)
        self.capture_button.pack(pady=5)

        # 右边的部分界面
        right_frame = ttk.Frame(self, style="Dashed.TFrame")
        right_frame.grid(row=0, column=2, padx=10, pady=10)

        self.current_script_label = tk.Label(right_frame, text=f"当前脚本：{self.file_name}")
        self.current_script_label.pack(padx=10, pady=10)

        self.save_button = tk.Button(right_frame, text="保存脚本", command=self.save_script)
        self.save_button.pack(side="left", pady=10, padx=15)

        self.load_button = tk.Button(right_frame, text="读取脚本", command=self.load_script)
        self.load_button.pack(side="left", pady=10, padx=15)

        right_frame2 = ttk.Frame(self, style="Dashed.TFrame")
        right_frame2.grid(row=1, column=2, padx=10)

        self.current_operation_label = tk.Label(right_frame2, text=f"当前操作：{self.operation_filename}")
        self.current_operation_label.pack(padx=10, pady=10)

        self.operation_settings_button = tk.Button(right_frame2, text="设置操作",
                                                   command=self.open_operation_settings_window)
        self.operation_settings_button.pack(side="left", pady=10, padx=15)

        self.browse_operation_button = tk.Button(right_frame2, text="读取操作", command=self.browse_operation_file)
        self.browse_operation_button.pack(side="left", pady=10, padx=15)

        bottom_frame = ttk.Frame(self, style="Dashed.TFrame")
        bottom_frame.grid(row=2, columnspan=3, pady=(20,10))

        loop_options = ["无限循环", "循环1次", "循环10次"]
        self.loop_var = tk.StringVar()
        self.loop_var.set(loop_options[0])  # 默认为无限循环

        self.start_button = tk.Button(bottom_frame, text="开始扫描", command=self.start_scanning, width=15, height=2, font=self.custom_font)
        self.start_button.pack(side="left", padx=25, pady=10)

        loop_option_menu = tk.OptionMenu(bottom_frame, self.loop_var, *loop_options, command=self.update_max_loops)
        loop_option_menu.pack(side="left", padx=20, pady=10)

        self.stop_button = tk.Button(bottom_frame, text="停止扫描", command=self.stop_scanning, width=15, height=2, font=self.custom_font)
        self.stop_button.pack(side="left", padx=20, pady=10)

        try:
            self.scripts = self.load_ordinary() if self.load_ordinary() else []
            self.load_all_script()
            self.operation_settings_window = OperationList(root, parent=self)
            self.operation_settings_window.set_file_path(self.operation_full_filename)
            self.operation_settings_window.destroy_self()
        except FileNotFoundError:
            pass

    def update_max_loops(self, value):
        if value == "无限循环":
            self.max_loops = None
        elif value == "循环1次":
            self.max_loops = 1
        elif value == "循环10次":
            self.max_loops = 10


    def init_new(self):
        self.operation_settings_window = OperationList(self.master, parent=self)
        self.operation_settings_window.set_file_path(self.operation_full_filename)

    def init_new_destory(self):
        self.operation_settings_window = OperationList(self.master, parent=self)
        self.operation_settings_window.set_file_path(self.operation_full_filename)
        self.operation_settings_window.destroy_self()

    def browse_operation_file(self):
        filename = filedialog.askopenfilename(initialdir=os.path.dirname(self.operation_full_filename),
                                              initialfile=os.path.basename(self.operation_full_filename),
                                              title="操作列表", defaultextension=".data",
                                              filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        if filename:
            file_name = os.path.basename(filename)

            self.operation_full_filename = filename
            self.operation_filename = os.path.splitext(file_name)[0]
            self.current_operation_label.config(text=f"当前操作：{self.operation_filename}")
            self.init_new_destory()

    def save_script(self):
        file_path = filedialog.asksaveasfilename(initialdir=os.path.dirname(self.file_path),
                                                 initialfile=os.path.basename(self.file_path),
                                                 title="保存脚本", defaultextension=".data",
                                                 filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        if file_path:
            data = {
                "target_image_path": self.target_image_path.get(),
                "manual_selection_coordinates": self.manual_selection_coordinates,
                "operation_full_filename": self.operation_full_filename
            }
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    existing_data = pickle.load(file)
            existing_data.update(data)  # 更新已存在的属性或添加新属性
            with open(file_path, 'wb') as file:
                pickle.dump(existing_data, file)

            try:
                with open(file_path, "rb") as file:
                    data = pickle.load(file)
                if isinstance(data, list):  # 检查数据是否是列表类型
                    return data
                elif isinstance(data, dict):  # 检查数据是否是字典类型
                    string_array = [f"{key}: {value}" for key, value in data.items()]
                    self.scripts = string_array
                    self.load_all_script()
            except FileNotFoundError:
                return None

    def save_default_script(self, file_path):
        self.file_name = os.path.basename(file_path)
        self.file_path = file_path
        if file_path:
            data = {
                "target_image_path": self.target_image_path.get(),
                "manual_selection_coordinates": self.manual_selection_coordinates,
                "operation_full_filename": self.operation_full_filename
            }
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    existing_data = pickle.load(file)
            if isinstance(existing_data, dict):  # 检查数据是否是字典类型
                existing_data.update(data)  # 更新已存在的属性或添加新属性
            elif isinstance(existing_data, list):  # 如果数据是列表类型，可以选择合并列表
                existing_data += data  # 更新已存在的属性或添加新属性
            with open(file_path, 'wb') as file:
                pickle.dump(existing_data, file)

            try:
                with open(file_path, "rb") as file:
                    data = pickle.load(file)
                if isinstance(data, list):  # 检查数据是否是列表类型
                    self.scripts = data
                elif isinstance(data, dict):  # 检查数据是否是字典类型
                    string_array = [f"{key}: {value}" for key, value in data.items()]
                    self.scripts = string_array
                self.load_all_script()
            except FileNotFoundError:
                return None

    def save_ordinary(self):
        with open(self.file_path, "wb") as file:
            pickle.dump(self.scripts, file)
            print("scripts")

    def load_script(self):
        file_path = filedialog.askopenfilename(initialdir=os.path.dirname(self.file_path),
                                               initialfile=os.path.basename(self.file_path),
                                               title="读取脚本",
                                               filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        self.file_name = os.path.basename(file_path)
        self.file_path = file_path
        try:
            with open(file_path, "rb") as file:
                data = pickle.load(file)
            if isinstance(data, list):  # 检查数据是否是列表类型
                return data
            elif isinstance(data, dict):  # 检查数据是否是字典类型
                string_array = [f"{key}: {value}" for key, value in data.items()]
                self.scripts = string_array
                self.load_all_script()
        except FileNotFoundError:
            return None

    def load_ordinary(self):
        try:
            with open(self.file_path, "rb") as file:
                data = pickle.load(file)
            if isinstance(data, list):  # 检查数据是否是列表类型
                return data
            elif isinstance(data, dict):  # 检查数据是否是字典类型
                string_array = [f"{key}: {value}" for key, value in data.items()]
                self.scripts = string_array
                return string_array
        except FileNotFoundError:
            return None

    def load_all_script(self):
        self.target_image_path.delete(0, 'end')
        self.current_script_label.config(
            text=f"当前脚本：{self.file_name}")
        for script in self.scripts:
            if script.startswith("target_image_path:"):
                target_image = script.split(": ")[1]
                self.target_image_path.insert(0, target_image)
                self.image_path = target_image
            elif script.startswith("manual_selection_coordinates:"):
                manual_selection = script.split(": ")[1]
                manual_selection = eval(manual_selection)
                self.manual_selection_coordinates = manual_selection
            elif script.startswith("operation_full_filename:"):
                filename = script.split(": ")[1]
                self.operation_full_filename = filename
                self.operation_filename = os.path.splitext(os.path.basename(filename))[0]
                self.current_operation_label.config(text=f"当前操作：{self.operation_filename}")

    def open_operation_settings_window(self):
        self.operation_settings_window = OperationList(self.master, parent=self)
        self.operation_settings_window.set_file_path(self.operation_full_filename)

    @staticmethod
    def take_screenshot():
        screenshot = ImageGrab.grab()
        return screenshot

    @staticmethod
    def load_target_image(path):
        target_image = Image.open(path)
        target_image = np.array(target_image)
        return target_image

    def compare_images_with_template_matching(self, image1, image2):
        # 将图像转换为灰度图
        gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # 使用模板匹配
        result = cv2.matchTemplate(gray_image1, gray_image2, cv2.TM_CCOEFF_NORMED)

        # 获取最大和最小匹配值及其位置
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 设置相似度阈值
        similarity_threshold = 0.75  # 通过调整阈值来判断相似度

        # 判断匹配值是否大于阈值
        if max_val >= similarity_threshold:
            h, w = image2.shape[:2]  # 获取模板图像的高度和宽度
            dx, dy = self.manual_selection_coordinates[0], self.manual_selection_coordinates[1]  # 计算相对偏移量
            top_left = (max_loc[0] + dx, max_loc[1] + dy)  # 最佳匹配位置的左上角坐标
            bottom_right = (top_left[0] + w, top_left[1] + h)  # 最佳匹配位置的右下角坐标
            self.max_loc = (top_left, bottom_right)
            return True  # 图片相似
        else:
            return False  # 图片不相似

    def start_scanning(self,max_loops = None):
        self.scanning = True
        loop_option_value = self.loop_var.get()  # Get the current value from loop_var
        self.update_max_loops(loop_option_value)
        if self.max_loops is not None:
            max_loops = self.max_loops
        x1, y1, x2, y2 = self.manual_selection_coordinates
        self.target_image_path_str = self.target_image_path.get()
        self.target_image = self.load_target_image(self.target_image_path_str)
        self.scanning_status_label.config(text="扫描中")
        self.scan_location_label.config(text=f"({x1}, {y1})\n({x2}, {y2})")
        self.main.iconify()  # 将窗口最小化
        self.scan_thread = threading.Thread(target=self.scan_loop(max_loops = max_loops))
        self.scan_thread.start()

    def stop_scanning(self):
        self.scanning = False
        self.max_loops = None
        if self.scanning is False:
            self.scanning_status_label.after(100, lambda: self.scanning_status_label.config(text="未开始扫描"))
        if self.scan_thread is not None:
            self.scan_thread.join()  # 等待线程结束
            self.scan_thread = None
            self.scanning_status_label.after(100, lambda: self.scanning_status_label.config(text="未开始扫描"))


    def browse_target_image(self):
        self.target_image_path_str = filedialog.askopenfilename(initialdir=os.path.dirname(self.image_path),
                                                                initialfile=os.path.basename(self.image_path),
                                                                title="Select file",
                                                                filetypes=(
                                                                    ("jpeg files", "*.jpg"), ("all files", "*.*")))
        self.target_image_path.delete(0, tk.END)
        self.target_image_path.insert(0, self.target_image_path_str)

    def start_grab_window(self):
        self.grab_photo = True
        self.open_manual_selection_window()

    def open_manual_selection_window(self):
        self.main.iconify()  # 将主窗口最小化

        self.manual_selection_window = tk.Toplevel(self.master)  # 创建一个新的Toplevel窗口
        self.manual_selection_window.attributes('-alpha', 0.3)
        self.manual_selection_window.attributes('-fullscreen', True)
        self.manual_selection_window.title("截图窗口")
        canvas = tk.Canvas(self.manual_selection_window)
        canvas.pack(fill="both", expand=True)

        def on_press_select(event):
            self.start_x = event.x  # 记录鼠标按下时的横坐标
            self.start_y = event.y  # 记录鼠标按下时的纵坐标

        def on_release_select(event):
            self.end_x = event.x  # 记录鼠标释放时的横坐标
            self.end_y = event.y  # 记录鼠标释放时的纵坐标
            self.manual_select_mode = False  # 退出手动框选模式
            self.scan_location_label.config(
                text=f"({self.start_x}, {self.start_y}) \n({self.end_x}, {self.end_y})")
            self.start_button.config(state="normal")  # 恢复“开始扫描”按钮的状态
            self.manual_selection_coordinates = (
                self.start_x, self.start_y, self.end_x, self.end_y)  # Store the coordinates
            self.manual_selection_window.destroy()
            if self.grab_photo:  # 如果需要截图
                x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
                x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
                self.manual_selection_coordinates = (
                    self.start_x-5, self.start_y-5, self.end_x+5, self.end_y+5)
                # 在对应位置产生截图
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                self.grab_photo = False
                # 要求用户选择路径保存截图
                file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
                if file_path:  # 如果用户选择了路径
                    screenshot.save(file_path)  # 保存截图
                    self.target_image_path.delete(0, tk.END)
                    self.target_image_path.insert(0, file_path)

            self.main.deiconify() # 恢复最小化的之前的界面


        def draw_drag_line(event):
            canvas.delete("all")
            if self.start_x is not None:
                canvas.create_line(self.start_x, self.start_y, self.start_x, event.y, fill='black',
                                   width=5)  # Draw line from (start_x,start_y) to (start_x,end_y)
                canvas.create_line(self.start_x, self.start_y, event.x, self.start_y, fill='black',
                                   width=5)  # Draw line from (start_x,start_y) to (end_x,start_y)
                canvas.create_line(self.start_x, event.y, event.x, event.y, fill='black',
                                   width=5)  # Draw line from (start_x,end_y) to (end_x,end_y)
                canvas.create_line(event.x, self.start_y, event.x,  event.y, fill='black',
                                   width=5)  # Draw line from (end_x,start_y) to (end_x,end_y)

        canvas.bind("<Button-1>", on_press_select)  # Record start position
        canvas.bind("<B1-Motion>", draw_drag_line)  # Draw drag line
        canvas.bind("<ButtonRelease-1>", on_release_select)  # Record end position

        self.manual_selection_window.focus_set()



    def scan_loop(self, max_loops):
        if self.scanning and (max_loops is None or max_loops > 0):
            if self.manual_selection_coordinates is not None:
                x1, y1, x2, y2 = self.manual_selection_coordinates
                screenshot = self.take_screenshot()

                region = (x1, y1, x2, y2)
                screen_region = np.array(screenshot.crop(region))

                result = self.compare_images_with_template_matching(screen_region, self.target_image)
                if result:
                    self.operation_settings_window.execute_operations()
                    self.scanning_status_label.config(
                        text="扫描中")
                    self.scan_location_label.config(
                        text=f"({x1}, {y1}) \n ({x1 + self.target_image.shape[1]}, "
                                f"{y1 + self.target_image.shape[0]})")
                else:
                    self.scan_location_label.config(
                        text=f"({x1}, {y1}) \n ({x1 + self.target_image.shape[1]}, "
                                f"{y1 + self.target_image.shape[0]})")
            screenshot.close()

            if max_loops is not None:
                max_loops -= 1

            if max_loops is None or max_loops > 0:
                self.master.after(100, lambda: self.scan_loop(max_loops))
            else:
                self.stop_scanning()


class MainDesk(tk.Tk):
    def __init__(self):
        super().__init__()
        # 数据初始化
        self.keep_scanning = None
        self.entry_operation = None
        self.entry_script = None
        self.entry_location = None
        self.folder_path = None

        # 界面初始化
        self.geometry("610x500")
        self.title("Script_Runner")
        self.lift()
        self.focus_set()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        # 设置未选中标签页的外观

        self.create_menu_bar()  # 创建菜单条
        self.sub_windows = []

        keyboard.on_press_key("esc", self.handle_escape)  # 监听全局的 "Escape" 键按下事件
        keyboard.on_press_key("F1", self.execute_start_scanning)

    def execute_start_scanning(self, event):
        for sub_window in self.sub_windows:
            sub_window.start_scanning()

    def handle_escape(self, event):
        self.keep_scanning = False
        for sub_window in self.sub_windows:
            sub_window.stop_scanning()
        self.focus_force()  # 窗口置顶
        self.state('normal')  # 恢复正常状态
        self.lift()  # 将主窗口放置在其他窗口之上

    def execute_loop_scanning(self):
        self.keep_scanning = True
        while self.keep_scanning:
           for sub_window in self.sub_windows:
               sub_window.max_loops = 1
               sub_window.start_scanning()



    def execute_scanning(self):
        for sub_window in self.sub_windows:
            sub_window.start_scanning()

    def execute_escape(self):
        self.keep_scanning = False
        for sub_window in self.sub_windows:
            sub_window.stop_scanning()
        self.focus_force()  # 窗口置顶
        self.state('normal')  # 恢复正常状态
        self.lift()  # 将主窗口放置在其他窗口之上


    def create_menu_bar(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)

        scan_columns_menu = tk.Menu(file_menu, tearoff=0)
        scan_columns_menu.add_command(label="修改扫描名", command=self.rename_tab)
        scan_columns_menu.add_command(label="保存扫描列", command=self.save_scan_columns)
        scan_columns_menu.add_command(label="导入扫描列", command=self.load_scan_columns)

        scan_menu = tk.Menu(file_menu, tearoff=0)
        scan_menu.add_command(label="全部开启扫描", command=self.execute_scanning)
        scan_menu.add_command(label="循环开启扫描", command=self.execute_loop_scanning)
        scan_menu.add_command(label="关闭全部扫描", command=self.execute_escape)

        file_menu.add_command(label="新扫描", command=self.add_image_scanner_app)
        file_menu.add_command(label="删除扫描", command=self.delete_image_scanner_app)
        file_menu.add_cascade(label="扫描列操作", menu=scan_columns_menu)
        file_menu.add_cascade(label="开启扫描", menu=scan_menu)
        file_menu.add_command(label="一键保存", command=self.save_all)

        menu_bar.add_cascade(label="操作", menu=file_menu)
        self.config(menu=menu_bar)

    def save_all(self):
        save_window = tk.Toplevel(self)
        save_window.title("一键保存")
        save_window.geometry("400x200")
        save_window.lift()
        save_window.focus_set()

        # 脚本
        frame_script = tk.Frame(save_window)
        label_script = tk.Label(frame_script, text="脚本:")
        self.entry_script = tk.Entry(frame_script)
        label_script.pack(side="left")
        self.entry_script.pack(side="left")
        frame_script.pack()

        # 操作
        frame_operation = tk.Frame(save_window)
        label_operation = tk.Label(frame_operation, text="操作:")
        self.entry_operation = tk.Entry(frame_operation)
        label_operation.pack(side="left")
        self.entry_operation.pack(side="left")
        frame_operation.pack()

        # 位置
        frame_location = tk.Frame(save_window)
        label_location = tk.Label(frame_location, text="位置:")
        self.entry_location = tk.Entry(frame_location)
        label_location.pack(side="left")
        self.entry_location.pack(side="left")
        frame_location.pack()

        # 保存位置按钮
        button_save_location = tk.Button(save_window, text="选择保存位置",
                                         command=lambda: self.open_file_manager(window=save_window))
        button_save_location.pack()

        # 确认和取消按钮
        frame_buttons = tk.Frame(save_window)
        button_confirm = tk.Button(frame_buttons, text="确认", command=lambda: self.confirm_save(window=save_window))
        button_cancel = tk.Button(frame_buttons, text="取消", command=save_window.destroy)
        button_confirm.pack(side="left")
        button_cancel.pack(side="right")
        frame_buttons.pack()

    def confirm_save(self, window):
        save_location = self.entry_location.get()
        # 获取扫描列、脚本和操作的内容
        script = self.entry_script.get()
        operation = self.entry_operation.get()

        script_path = os.path.join(save_location, f"{script}.data")
        operation_path = os.path.join(save_location, f"{operation}.data")

        # 调用当前子窗口的保存方法
        current_index = self.notebook.index("current")
        current_sub_window = self.sub_windows[current_index]

        if script:
            current_sub_window.save_default_script(script_path)
        if operation and hasattr(current_sub_window, 'operation_settings_window'):
            current_sub_window.init_new()
            current_sub_window.operation_settings_window.save_default_operations(operation_path)
            current_sub_window.operation_settings_window.destroy_self()

        # 在这里执行确认保存的逻辑
        window.destroy()

    def open_file_manager(self, window):
        window.grab_set()
        self.folder_path = filedialog.askdirectory(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                                   title="选择文件夹")
        if self.folder_path:  # 如果用户选择了文件夹
            self.entry_location.delete(0, tk.END)  # 清空原有内容
            self.entry_location.insert(0, self.folder_path)  #

    def add_image_scanner_app(self):
        sub_window = ImageScannerApp(self.notebook, self)
        self.sub_windows.append(sub_window)

        tab_name = f"Tab {len(self.sub_windows)}"
        new_name = askstring("添加扫描", "请输入扫描名", initialvalue=tab_name)
        if new_name:
            self.notebook.add(sub_window, text=new_name)  # 设置 state 为 "hidden"
        self.notebook.select(sub_window)  # 选中新添加的 tab

    def rename_tab(self):
        current_tab = self.notebook.select()
        if current_tab:
            tab_name = self.notebook.tab(current_tab, "text")
            new_name = askstring("修改扫描名", "请输入新的扫描名", initialvalue=tab_name)
            if new_name:
                self.notebook.tab(current_tab, text=new_name)

    def delete_image_scanner_app(self):
        current_tab = self.notebook.select()
        if current_tab:
            index = self.notebook.index(current_tab)
            sub_window = self.sub_windows[index]
            self.notebook.forget(current_tab)
            sub_window.destroy()

    def save_scan_columns(self):
        file_path = filedialog.asksaveasfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                                 title="保存扫描列",defaultextension=".json",
                                                 filetypes=(("Json", "*.json"), ("All files", "*.*")))
        if file_path:
            data = {}
            for sub_window in self.sub_windows:
                if sub_window.winfo_exists():
                   tab_name = self.notebook.tab(sub_window, "text")
                   file_name = sub_window.file_name
                   read_path = sub_window.file_path
                   data[tab_name] = {"file_name": file_name, "file_path": read_path}

            with open(file_path, "w") as file:
                json.dump(data, file)

    def load_scan_columns(self):
        file_path = filedialog.askopenfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                               title="读取扫描列",
                                               filetypes=(("Json", "*.json"), ("All files", "*.*")))
        if file_path:
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    for tab_name, file_data in data.items():
                        sub_window = ImageScannerApp(self.notebook, self, list_name=file_data["file_name"])
                        sub_window.file_name = file_data["file_name"]  # 设置每个子窗口的file_name
                        sub_window.file_path = file_data["file_path"]  # 设置每个子窗口的file_path
                        sub_window.load_ordinary()
                        sub_window.load_all_script()
                        self.notebook.add(sub_window, text=tab_name)
                        self.sub_windows.append(sub_window)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    root = MainDesk()
    root.mainloop()
