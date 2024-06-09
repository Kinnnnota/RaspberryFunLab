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
        self.folder_options = self.load_specific_env_vars()  # 加载特定配置文件
        

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

    def setting(self,close_button=False):
        """创建一个无计时器的设定画面，需手动关闭"""
        self.folder_options = self.load_specific_env_vars()
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.geometry('400x300')
        print("创建设定相关的组件")
        for folder_path, var in self.folder_options.items():
            check = ttk.Checkbutton(self.settings_window, text=folder_path, variable=var)
            check.pack(anchor='w')

        confirm_button = ttk.Button(self.settings_window, text="确认", command=self.confirm_and_close)
        confirm_button.pack(pady=10)
        
        if not close_button:
            close_button = ttk.Button(self.settings_window, text="关闭", command=self.settings_window.destroy)
            close_button.pack(pady=20)
        else:
            # 或者可以不显示关闭按钮
            # close_button.pack_forget()
            pass
        print("设定画面已创建，无自动关闭")
        
    def save_settings(self):
        """保存文件夹路径和复选框状态到配置文件"""
        config = configparser.ConfigParser()
        config.optionxform = str
        config['Folders'] = {folder_path: str(var.get()) for folder_path, var in self.folder_options.items()}
        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)
        print("配置文件已保存到:", self.config_file_path)

    def confirm_and_close(self):
        """保存设置并关闭窗口"""
        self.save_settings()
        self.settings_window.destroy()
        os.execv(sys.executable, ['python'] + sys.argv)

    def load_specific_env_vars(self):
        """加载特定的配置文件，包括未选中的复选框，如果全部未选中，则使用默认路径"""
        folder_options = {}
        imgs_default_path = "./output_image"
        config = configparser.ConfigParser()
        config.optionxform = str
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)
            if 'Folders' in config:
                for folder_path, state in config['Folders'].items():
                    is_true = state == 'True'
                    folder_options[folder_path] = tk.BooleanVar(value=is_true)
            else:
                # 如果配置文件中没有Folders段落，使用默认值
                folder_options[imgs_default_path] = tk.BooleanVar(value=True)
        return folder_options
    

    def get_selected_folders(self):
        """返回选中的文件夹路径列表"""
        return [path for path, var in self.folder_options.items() if var.get()]
    
    def update_folders_in_config(self):
        """检查/mnt/myshare文件夹并更新配置文件"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)
        if 'Folders' not in config:
            config['Folders'] = {}

        # 检查/mnt/myshare文件夹下的文件夹,回头写进配置文件吧
        share_folder_path = '/mnt/myshare'
        if os.path.exists(share_folder_path) and os.path.isdir(share_folder_path):
            for folder_name in os.listdir(share_folder_path):
                folder_path = os.path.join(share_folder_path, folder_name)
                if os.path.isdir(folder_path):
                    config['Folders'][folder_name] = folder_path

        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)
        print("配置文件已更新:", self.config_file_path)

    def show_warning(self):
        """显示警告画面，如果没有读取到任何图像文件"""
        # 创建一个顶层窗口
        self.warning_window = tk.Toplevel(self.root)
        
        self.warning_window.geometry('300x200')  # 设置窗口大小
        self.warning_window.title('警告')  # 设置窗口标题

        # 在窗口中添加警告信息
        warning_label = ttk.Label(self.warning_window , text="没有读取到任何图像文件", font=('Arial', 12))
        warning_label.pack(pady=20)  # 增加垂直间距

        # 添加一个按钮，点击后关闭警告窗口并打开设置窗口
        confirm_button = ttk.Button(self.warning_window , text="确定", command=lambda: [self.warning_window.destroy(), self.setting(disable_close_button=True)])
        confirm_button.pack(pady=20)
        print("警告画面已创建")
        self.warning_window.grab_set()  # 抓取所有到这个窗口的事件
        self.warning_window.transient(self.root)
        self.warning_window.update_idletasks()



