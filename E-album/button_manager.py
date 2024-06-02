import tkinter as tk
from tkinter import ttk
import sys
import os
import configparser

class ButtonManager:
    def __init__(self, root):
        self.root = root
        self.temp_window = None
        self.settings_window = None
        self.config_file_path = os.path.join(os.path.expanduser('~/E-album'), 'config.ini')  # 配置文件路径
        self.folder_options = self.load_specific_env_vars()  # 加载特定环境变量
        

    def display_temp_buttons(self):
        """显示一个带有按钮的临时画面，几秒后自动关闭"""
        print("创建一个顶层窗口来承载按钮")
        self.temp_window = tk.Toplevel(self.root)
        self.temp_window.geometry('480x320')  # 设置窗口大小
        print("创建几个示例按钮")
        button1 = ttk.Button(self.temp_window, text="停止运行", command=self.close_application)
        button1.pack(pady=5)
        button2 = ttk.Button(self.temp_window, text="设定", command=self.setting)  # 修改此处，传递函数引用
        button2.pack(pady=5)
        print("设置计时器，几秒后关闭窗口")
        self.root.after(5000, self.temp_window.destroy)  # 5秒后关闭
        print("关闭窗口")

    def close_application(self):
        """关闭当前Python运行"""
        sys.exit()

    def setting(self):
        """创建一个无计时器的设定画面，需手动关闭"""
        print("创建一个设定画面")
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.geometry('400x300')  # 设定窗口的大小
        print("创建设定相关的组件")
        for folder_path, var in self.folder_options.items():
            check = ttk.Checkbutton(self.settings_window, text=folder_path, variable=var)
            check.pack(anchor='w')

        confirm_button = ttk.Button(self.settings_window, text="确认", command=self.confirm_and_close)
        confirm_button.pack(pady=10)

        close_button = ttk.Button(self.settings_window, text="关闭", command=self.settings_window.destroy)
        close_button.pack(pady=20)  # 添加关闭按钮
        print("设定画面已创建，无自动关闭")
        
    def save_settings(self):
        """保存选中的文件夹路径到配置文件"""
        selected_folders = [path for path, var in self.folder_options.items() if var.get()]
        config = configparser.ConfigParser()
        config['Folders'] = {f'FOLDER{i}': folder for i, folder in enumerate(selected_folders, start=1)}
        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)
        print("环境变量已保存到:", self.config_file_path)

    def confirm_and_close(self):
        """保存设置并关闭窗口"""
        self.save_settings()
        self.settings_window.destroy()

    def load_specific_env_vars(self):
        """加载特定的环境变量"""
        folder_options = {}
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)
            if 'Folders' in config:
                for key, value in config['Folders'].items():
                    folder_options[value] = tk.BooleanVar(value=True)
        else:
            # 如果文件不存在，使用默认值
            folder_options = {
                "./input_image": tk.BooleanVar(),
                "./output_image": tk.BooleanVar(),
            }
        return folder_options
    
    def update_specific_env_var(self, key, value): #用于更改计时，之后详细修改
        """更新配置文件中的某个变量"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)
        if 'Folders' not in config:
            config['Folders'] = {}
        config['Folders'][key] = value
        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)
        print(f"环境变量 {key} 已更新为: {value}")

    def get_selected_folders(self):
        """返回选中的文件夹路径列表"""
        return [path for path, var in self.folder_options.items() if var.get()]