import tkinter as tk
from PIL import Image, ImageTk
import os
from tkinter import ttk 
import time
import configparser
import subprocess 
from random import shuffle
import sys  
from button_manager import ButtonManager  

class PhotoAlbum:
    def __init__(self, root, input_dir, output_dir):
        self.root = root
        self.input_dir = input_dir
        self.output_dirs = output_dir
        self.hide_buttons_id = None
        self.prevent_update = False
        

        self.imgs = []
        for imgs_dir in self.output_dirs:
            self.imgs.extend(self.discover_images(filetype=imgs_dir))  # 收集每个路径下的图片
        self.change_imgs = self.discover_images(filetype=input_dir)
        self.process_images()  # 处理所有图片
        self.index = 0
        self.shuffle_images()  # 洗牌

        self.display_image()  # 显示第一张图片
        self.button_manager = ButtonManager(self.root)
        
        

    def discover_images(self,filetype):
        print("获取图像",filetype)
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']  # 添加你需要支持的文件格式
        files = []
        for root, dirs, filenames in os.walk(filetype): 
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in supported_formats:
                    files.append(os.path.join(root, filename))
        return files
    
    def shuffle_images(self):
        print("洗牌")
        # 随机洗牌图片列表
        shuffle(self.imgs)

    def process_images(self):
        print("处理图像")
        if not self.change_imgs:
            return
        for img_path in self.change_imgs:
            # 计算原始图片相对于input_dir的相对路径
            rel_path = os.path.relpath(img_path, self.input_dir)
            # 构造输出文件的完整路径，保持目录结构
            output_path = os.path.join(self.output_dir, rel_path)
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 检查输出文件是否已存在
            if not os.path.exists(output_path):
                self.resize_image_to_fullscreen_keep_aspect_ratio(img_path, output_path)
                # 成功处理后删除原始文件（如果需要）
                os.remove(img_path)

    def resize_image_to_fullscreen_keep_aspect_ratio(self, image_path, output_path, screen_resolution=(480, 320)):
        with Image.open(image_path) as img:
            img.thumbnail(screen_resolution, Image.Resampling.LANCZOS)
            background = Image.new('RGB', screen_resolution, (0, 0, 0))
            bg_w, bg_h = background.size
            img_w, img_h = img.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            background.paste(img, offset)
            background.save(output_path)

    def display_image(self):
        print("显示图像")
        if self.prevent_update:
            print("结束显示图像,return")
            return
        if self.index >= len(self.imgs):
            self.index = 0  # 重置索引，循环显示图片
            print("重新洗牌")
            self.shuffle_images()  # 每当遍历完一遍图片后，重新洗牌

        if self.imgs[self.index] == None:
            return
        img_path = self.imgs[self.index]
        try:
            print("开始打开图片", img_path)
            img = Image.open(img_path)
            photo = ImageTk.PhotoImage(img)
            print("图像打开成功")
        except Exception as e:
            print("图像打开失败:", e)
            return

        if not hasattr(self, 'canvas'):
            self.canvas = tk.Canvas(self.root, width=img.width, height=img.height)
            self.canvas.pack()
            self.canvas.image = photo  # 存储图片对象以防被垃圾回收器回收
            self.photo_id = self.canvas.create_image(0, 0, anchor="nw", image=photo)  # 创建图像对象并保存其ID
            print("创建图像")
        else:
            # 更新Canvas上的图片
            self.canvas.image = photo
            self.canvas.itemconfig(self.photo_id, image=photo)  # 使用保存的ID来更新图像对象
            print("更新图像")

        # 确保canvas已创建或更新后再绑定点击事件
        self.canvas.bind("<Button-1>", lambda e: self.button_manager.display_temp_buttons())
        print("点击事件绑定成功")

        self.index += 1
        if not self.prevent_update:
            self.root.after(40000, self.display_image)  # 每40秒更换一次图片



    def display_gif(self, gif_path):
        # 初始化GIF动画的帧索引
        if not hasattr(self, 'gif_frame'):
            self.gif_frame = 0

        self.gif = tk.PhotoImage(file=gif_path, format=f"gif -index {self.gif_frame}")

        if not hasattr(self, 'canvas'):
            self.canvas = tk.Canvas(self.root, width=self.gif.width(), height=self.gif.height())
            self.canvas.pack()
            # 在Canvas上创建一个图像对象，存储gif图像以防止被垃圾收集器回收
            self.canvas.gif_image = self.canvas.create_image(0, 0, anchor="nw", image=self.gif)
        else:
            # 更新Canvas上的gif图像
            self.canvas.itemconfig(self.canvas.gif_image, image=self.gif)

        self.gif_frame += 1
        try:
            # 尝试显示下一帧
            self.root.after(100, lambda: self.display_gif(gif_path))
        except tk.TclError as e:
            # 如果超出帧数，重置回第一帧，并继续播放
            self.gif_frame = 0
            self.root.after(100, lambda: self.display_gif(gif_path))


    

    def close_application(self):
        """关闭当前Python运行"""
        sys.exit()



def get_selected_folders_from_config(config_file_path):
    """从配置文件中读取选中的文件夹路径列表"""
    selected_folders = []
    config = configparser.ConfigParser()
    if os.path.exists(config_file_path):
        config.read(config_file_path)
        if 'Folders' in config:
            for key, value in config['Folders'].items():
                selected_folders.append(value)
    return selected_folders

def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)

    input_dir = '/home/jo/E-album/input_image'  # 输入目录
    config_file_path = os.path.join(os.path.expanduser('~/E-album'), 'config.ini')
    output_dir = get_selected_folders_from_config(config_file_path)
    

    album = PhotoAlbum(root, input_dir, output_dir)

    root.mainloop()

if __name__ == "__main__":
    main()