import os
import pickle
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import imagehash
import keyboard
import numpy as np
import pyautogui
from PIL import Image, ImageGrab, ImageTk


class OperationList:
    def __init__(self, root, list_name="NewOperation"):
        self.root = root

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

        self.operation_listbox = tk.Listbox(self.setting_window, selectmode="single", height=5)

        self.populate_operation_list()
        self.operation_listbox.pack(pady=5)

        self.op_bar = tk.Menu(self.setting_window)

        self.op_menu = tk.Menu(self.op_bar, tearoff=0)
        self.op_menu.add_command(label="保存操作列表", command=self.save_all_operations)
        self.op_menu.add_command(label="读取操作列表", command=self.load_all_operations)

        self.op_bar.add_cascade(label="操作列表", menu=self.op_menu)

        self.setting_window.config(menu=self.op_bar)

    def save_all_operations(self):
        file_path = filedialog.asksaveasfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                                 title="保存操作列表", defaultextension=".data",
                                                 filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        if file_path:
            with open(file_path, 'wb') as file:
                pickle.dump(self.operations, file)

    def load_all_operations(self):
        file_path = filedialog.askopenfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                               title="读取操作列表",
                                               filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        if file_path:
            with open(file_path, 'rb') as file:
                self.operations = pickle.load(file)
                self.populate_operation_list()
                file_name = os.path.basename(file_path)  # Extract the file name without extension
                list_name = os.path.splitext(file_name)[0]
                self.set_list_name(list_name)
                self.setting_window.lift()
                self.setting_window.focus_set()

    def destroy_self(self):
        self.setting_window.destroy()

    def show_add_operation_options(self):
        self.add_options_window = tk.Toplevel(self.setting_window)
        self.add_options_window.title("添加操作选项")
        self.add_options_window.lift()
        self.add_options_window.focus_set()
        self.add_options_window.geometry("400x300")
        wait_button = tk.Button(self.add_options_window, text="等待", command=self.add_wait_operation_window)
        wait_button.pack(pady=5)

        keyboard_button = tk.Button(self.add_options_window, text="键盘操作",
                                    command=self.add_keyboard_operation_window)
        keyboard_button.pack(pady=5)

        mouse_button = tk.Button(self.add_options_window, text="鼠标操作", command=self.add_mouse_operation_window)
        mouse_button.pack(pady=5)
        pass

    def set_list_name(self, list_name):
        self.list_name = list_name
        self.file_name = f"{list_name}.data"
        self.operations = self.load_operations()
        self.populate_operation_list()

    def load_operations(self):
        try:
            with open(self.file_name, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    def save_operations(self):
        with open(self.file_name, "wb") as file:
            pickle.dump(self.operations, file)
            print("save")

    def add_default_operations(self):
        default_operations = ["键盘操作：按键位置 - p", "等待：400ms", "键盘操作：按键位置 - enter"]
        self.operations = default_operations
        self.save_operations()

    def add_wait_operation(self, wait_time):
        self.operation_listbox.insert(tk.END, f"等待：{wait_time}ms")
        self.operations.append(f"等待：{wait_time}ms")
        self.save_operations()

    def add_keyboard_operation(self, key_position):
        self.operation_listbox.insert(tk.END, f"键盘操作：按键位置 - {key_position}")
        self.operations.append(f"键盘操作：按键位置 - {key_position}")
        self.save_operations()

    def add_mouse_operation(self, click_position):
        self.operation_listbox.insert(tk.END, f"鼠标操作：点击位置 - {click_position}")
        self.operations.append(f"鼠标操作：点击位置 - {click_position}")
        self.save_operations()

    def set_wait_time(self, wait_time):
        self.wait_time = wait_time
        self.add_wait_operation(self.wait_time)

    def set_key_position(self, key_position):
        self.key_position = key_position
        self.add_keyboard_operation(self.key_position)

    def set_click_position(self, click_position):
        self.click_position = click_position
        self.add_mouse_operation(self.click_position)

    def add_wait_operation_window(self):
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
                                command=lambda: [self.set_wait_time(int(wait_entry.get())), wait_window.destroy()])
        wait_button.pack(pady=5)

    def add_keyboard_operation_window(self):
        keyboard_window = tk.Toplevel(self.setting_window)
        keyboard_window.title("键盘操作")
        keyboard_window.geometry("400x300")
        keyboard_window.lift()
        keyboard_window.focus_set()
        self.add_options_window.destroy()
        keyboard_label = tk.Label(keyboard_window, text="请按下一个键：")
        keyboard_label.pack(pady=5)

        def record_key_press(event):
            self.set_key_position(event.keysym)
            keyboard_window.destroy()

        keyboard_window.bind("<Key>", record_key_press)

    def add_mouse_operation_window(self):
        self.add_options_window.destroy()
        mouse_window = tk.Toplevel(self.setting_window)
        mouse_window.attributes('-alpha', 0.5)  # Set transparency
        mouse_window.attributes('-fullscreen', True)  # Set fullscreen
        mouse_window.title("鼠标操作")
        mouse_label = tk.Label(mouse_window, text="请在此窗口点击一个位置：")
        mouse_label.pack(pady=5)

        def record_click_position(event):
            click_position = f"({event.x}, {event.y})"
            self.set_click_position(click_position)
            mouse_window.destroy()

        mouse_window.bind("<Button-1>", record_click_position)

    def modify_selected_operation(self):
        selected_index = self.operation_listbox.curselection()
        if selected_index:
            del self.operations[selected_index[0]]
            self.show_add_operation_options()
            self.save_operations()
            self.populate_operation_list()
        pass

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
            elif operation.startswith("键盘操作"):
                key_position = operation.split(" - ")[1]
                pyautogui.press(key_position)  # Simulate keyboard press
            elif operation.startswith("鼠标操作"):
                click_position = operation.split(" - ")[1]
                x, y = map(int, click_position.strip("()").split(","))
                pyautogui.click(x, y)
        pass

    def populate_operation_list(self):
        self.operation_listbox.delete(0, tk.END)  # Clear the listbox
        for operation in self.operations:
            self.operation_listbox.insert(tk.END, operation)


class ImageScannerApp(ttk.Frame):
    def __init__(self, master, main, list_name="NewScript"):
        super().__init__(master)
        self.scan_thread = None
        self.master = master  # 本页面（notebook）的设置
        self.main = main  # 主页面的设置

        # 参数的初始化
        self.file_path = None
        self.operation_filename = "NewOperation"

        self.operation_settings_window = OperationList(root)
        self.operation_settings_window.set_list_name(self.operation_filename)
        self.operation_settings_window.destroy_self()

        self.scanning = False  # 是否扫描

        self.manual_selection_coordinates = None  # 框选的扫描

        self.manual_select_mode = False  # 是否是第一次匹配

        self.list_name = list_name  # 读取文件名称，list_name是默认的名字···
        self.file_name = f"{list_name}.data"

        # 左侧的部分界面
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10)

        self.scanning_status_label = tk.Label(left_frame, text="正在扫描：无", fg="red")
        self.scanning_status_label.pack()

        # 中间的部分界面
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=0, column=1, padx=10)

        self.start_button = tk.Button(middle_frame, text="开始扫描", command=self.start_scanning)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(middle_frame, text="停止扫描", command=self.stop_scanning)
        self.stop_button.pack(pady=10)

        self.target_image_path_label = tk.Label(middle_frame, text="目标图片路径:")
        self.target_image_path_label.pack()

        self.target_image_path = tk.Entry(middle_frame)
        self.target_image_path.pack()

        self.browse_button = tk.Button(middle_frame, text="浏览图片", command=self.browse_target_image)
        self.browse_button.pack(pady=5)

        self.manual_select_button = tk.Button(middle_frame, text="手动框选", command=self.open_manual_selection_window)
        self.manual_select_button.pack(pady=5)

        self.operation_settings_button = tk.Button(middle_frame, text="设置操作",
                                                   command=self.open_operation_settings_window)
        self.operation_settings_button.pack(pady=10)

        # 右边的部分界面
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=2, padx=10)

        self.save_button = tk.Button(right_frame, text="保存脚本", command=self.save_script)
        self.save_button.pack(pady=10)

        self.load_button = tk.Button(right_frame, text="读取脚本", command=self.load_script)
        self.load_button.pack(pady=10)

        self.operation_name_label = tk.Label(right_frame, text="操作列表名:")
        self.operation_name_label.pack()

        self.operation_name_entry = tk.Entry(right_frame)
        self.operation_name_entry.pack()

        self.browse_operation_button = tk.Button(right_frame, text="浏览文件", command=self.browse_operation_file)
        self.browse_operation_button.pack(pady=5)

        keyboard.on_press_key("esc", self.stop_key)

        try:
            self.scripts = self.load_ordinary() if self.load_ordinary() else []
            self.load_all_script()
        except FileNotFoundError:
            pass


    def stop_key(self, event):
        if self.scanning:
            self.stop_scanning()

    def browse_operation_file(self):
        filename = filedialog.askopenfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                              title="操作列表", defaultextension=".data",
                                              filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        if filename:
            file_name = os.path.basename(filename)
            self.operation_name_entry.delete(0, tk.END)
            self.operation_name_entry.insert(0, os.path.splitext(file_name)[0])
            self.operation_filename = os.path.splitext(file_name)[0]

    def save_script(self):
        file_path = filedialog.asksaveasfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                                 title="保存脚本", defaultextension=".data",
                                                 filetypes=(("Data files", "*.data"), ("All files", "*.*")))
        if file_path:
            data = {
                "target_image_path": self.target_image_path.get(),
                "manual_selection_coordinates": self.manual_selection_coordinates,
                "operation_filename": self.operation_filename
            }
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    existing_data = pickle.load(file)
            existing_data.update(data)  # 更新已存在的属性或添加新属性
            with open(file_path, 'wb') as file:
                pickle.dump(existing_data, file)

    def save_ordinary(self):
        with open(self.file_name, "wb") as file:
            pickle.dump(self.scripts, file)
            print("scripts")

    def load_script(self):
        file_path = filedialog.askopenfilename(initialdir="C:/Users/hp/PycharmProjects/ScriptsRunner/",
                                               title="读取脚本",
                                               filetypes=(("Data files", "*.data"), ("All files", "*.*")))
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
            with open(self.file_name, "rb") as file:
                data = pickle.load(file)
            if isinstance(data, list):  # 检查数据是否是列表类型
                return data
            elif isinstance(data, dict):  # 检查数据是否是字典类型
                string_array = [f"{key}: {value}" for key, value in data.items()]
                return string_array
        except FileNotFoundError:
            return None

    def load_all_script(self):
        self.operation_name_entry.delete(0, 'end')
        self.target_image_path.delete(0, 'end')
        for script in self.scripts:
            if script.startswith("target_image_path:"):
                target_image = script.split(": ")[1]
                self.target_image_path.insert(0, target_image)
            elif script.startswith("manual_selection_coordinates:"):
                manual_selection = script.split(": ")[1]
                manual_selection = eval(manual_selection)
                self.manual_selection_coordinates = manual_selection
            elif script.startswith("operation_filename:"):
                filename = script.split(": ")[1]
                self.operation_filename = filename
                self.operation_name_entry.insert(0, filename)

    def open_operation_settings_window(self):
        self.operation_settings_window = OperationList(self.master)
        self.operation_settings_window.set_list_name(self.operation_filename)

    def take_screenshot(self):
        screenshot = ImageGrab.grab()
        return screenshot

    def load_target_image(self, path):
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
        similarity_threshold = 0.80  # 通过调整阈值来判断相似度，具体阈值可以根据实际情况调整

        # 判断匹配值是否大于阈值
        if max_val >= similarity_threshold:
            return True  # 图片相似
        else:
            return False  # 图片不相似

    def start_scanning(self):
        self.scanning = True
        self.target_image_path_str = self.target_image_path.get()
        self.target_image = self.load_target_image(self.target_image_path_str)
        self.main.iconify()  # 将窗口最小化
        self.scan_thread = threading.Thread(target=self.scan_loop())
        self.scan_thread.start()

    def stop_scanning(self):
        self.scanning = False
        print("停止扫描")  # 输出“停止扫描”
        self.scanning_status_label.config(text="停止扫描")
        if self.scan_thread is not None:
            self.scan_thread.join()  # 等待线程结束
        self.scan_thread = None

    def browse_target_image(self):
        self.target_image_path_str = filedialog.askopenfilename(initialdir="C://Users//hp//OneDrive//桌面//limbus",
                                                                title="Select file",
                                                                filetypes=(
                                                                    ("jpeg files", "*.jpg"), ("all files", "*.*")))
        self.target_image_path.delete(0, tk.END)
        self.target_image_path.insert(0, self.target_image_path_str)

    def open_manual_selection_window(self):
        self.main.iconify()  # 将主窗口最小化
        self.manual_selection_window = tk.Toplevel(self.master)  # 创建一个新的Toplevel窗口
        self.manual_selection_window.overrideredirect(True)  # 去除窗口边框
        self.manual_selection_window.attributes("-alpha", 0.1)  # 设置窗口透明度
        self.manual_selection_window.attributes("-topmost", True)  # 窗口置顶
        self.manual_selection_window.geometry(
            f"{self.master.winfo_screenwidth()}x{self.master.winfo_screenheight()}+0+0")  # 设置窗口大小和位置
        self.manual_selection_image = Image.new("RGBA",
                                                (self.master.winfo_screenwidth(), self.master.winfo_screenheight()),
                                                (0, 0, 0, 0))  # 创建透明图像
        self.manual_selection_photo = ImageTk.PhotoImage(self.manual_selection_image)
        self.manual_selection_canvas = tk.Canvas(self.manual_selection_window, width=self.master.winfo_screenwidth(),
                                                 height=self.master.winfo_screenheight(), highlightthickness=0)
        self.manual_selection_canvas.create_image(0, 0, anchor="nw", image=self.manual_selection_photo)
        self.manual_selection_canvas.pack()
        self.manual_selection_window.bind('<ButtonRelease-1>',
                                          self.on_release_select)  # Bind left mouse button release event
        self.manual_selection_window.bind('<ButtonPress-1>', self.on_press_select)  # 绑定鼠标左键按下事件
        self.manual_selection_window.bind('<ButtonRelease-1>', self.on_release_select)  # 绑定鼠标左键释放事

    def on_press_select(self, event):
        self.start_x = event.x  # 记录鼠标按下时的横坐标
        self.start_y = event.y  # 记录鼠标按下时的纵坐标

    def on_release_select(self, event):
        self.end_x = event.x  # 记录鼠标释放时的横坐标
        self.end_y = event.y  # 记录鼠标释放时的纵坐标
        self.main.attributes("-alpha", 1.0)  # 恢复窗口透明度
        self.main.state('normal')  # 恢复窗口大小
        self.manual_select_mode = False  # 退出手动框选模式
        self.scanning_status_label.config(
            text=f"正在扫描：({self.start_x}, {self.start_y}) 到 ({self.end_x}, {self.end_y})")
        self.master.unbind('<Motion>')  # 解绑鼠标移动事件
        self.master.unbind('<ButtonPress-1>')  # 解绑鼠标左键按下事件
        self.master.unbind('<ButtonRelease-1>')  # 解绑鼠标左键释放事件
        self.start_button.config(state="normal")  # 恢复“开始扫描”按钮的状态
        self.manual_selection_coordinates = (
            self.start_x, self.start_y, self.end_x, self.end_y)  # Store the coordinates
        self.main.deiconify()
        self.manual_selection_window.destroy()

    def scan_loop(self):
        if self.scanning:
            if not self.manual_select_mode:
                if self.manual_selection_coordinates is not None:
                    x1, y1, x2, y2 = self.manual_selection_coordinates
                    screenshot = self.take_screenshot()

                    region = (x1, y1, x2, y2)
                    screen_region = np.array(screenshot.crop(region))

                    result = self.compare_images_with_template_matching(screen_region, self.target_image)
                    if result:
                        self.operation_settings_window.execute_operations()
                        print("匹配成功")
                        self.scanning_status_label.config(
                            text=f"匹配成功：({x1}, {y1}) to ({x1 + self.target_image.shape[1]}, {y1 + self.target_image.shape[0]})")
                    else:
                        self.scanning_status_label.config(text="没有符合的区域")
                screenshot.close()
            self.master.after(100, self.scan_loop)


class MainDesk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Script_Runner")
        self.lift()
        self.focus_set()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.create_menu_bar()  # 创建菜单条
        self.sub_windows = []

        keyboard.on_press_key("esc", self.handle_escape)  # 监听全局的 "Escape" 键按下事件

    def create_menu_bar(self):
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="新扫描", command=self.add_image_scanner_app)
        file_menu.add_command(label="删除扫描", command=self.delete_image_scanner_app)
        file_menu.add_command(label="保存扫描列")
        file_menu.add_command(label="导入扫描列")

        menu_bar.add_cascade(label="操作", menu=file_menu)
        self.config(menu=menu_bar)

    def add_image_scanner_app(self):
        sub_window = ImageScannerApp(self.notebook, self)
        self.sub_windows.append(sub_window)

        tab_name = f"Tab {len(self.sub_windows)}"
        self.notebook.add(sub_window, text=tab_name)  # 设置 state 为 "hidden"
        self.notebook.select(sub_window)  # 选中新添加的 tab

    def delete_image_scanner_app(self):
        current_tab = self.notebook.select()
        if current_tab:
            self.notebook.forget(current_tab)

    def handle_escape(self, event):
        self.focus_force()   # 窗口置顶
        self.state('normal')  # 恢复正常状态
        self.lift()  # 将主窗口放置在其他窗口之上


if __name__ == "__main__":
    root = MainDesk()
    root.mainloop()
