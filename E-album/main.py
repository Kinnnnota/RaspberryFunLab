import tkinter as tk
from PIL import Image, ImageTk
import os
from tkinter import ttk 
import time
import subprocess 
from random import shuffle
import sys  # 确保在文件顶部导入sys模块

class PhotoAlbum:
    def __init__(self, root, input_dir, output_dir):
        self.root = root
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.hide_buttons_id = None
        self.prevent_update = False
        self.imgs = self.discover_images(filetype=output_dir)
        self.change_imgs = self.discover_images(filetype=input_dir)
        self.process_images()  # 处理所有图片
        self.index = 0
        self.shuffle_images()  # 洗牌

        self.display_image()  # 显示第一张图片
        
        

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
        self.canvas.bind("<Button-1>", lambda e: self.display_temp_buttons())
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


    def display_temp_buttons(self):
        """显示一个带有按钮的临时画面，几秒后自动关闭"""
        # 创建一个顶层窗口来承载按钮
        print("创建一个顶层窗口来承载按钮")
        self.temp_window = tk.Toplevel(self.root)
        self.temp_window.geometry('480x320')  # 设置窗口大小
        # 创建几个示例按钮
        print("创建几个示例按钮")
        button1 = ttk.Button(self.temp_window, text="停止运行", command=self.close_application)
        button1.pack(pady=5)
        button2 = ttk.Button(self.temp_window, text="串流steam",command=self.run_steam_link)
        button2.pack(pady=5)
        print("设置计时器，几秒后关闭窗口")

        # 设置计时器，几秒后关闭窗口
        self.root.after(5000, self.temp_window.destroy)  # 3秒后关闭
        print("关闭窗口")

    def close_application(self):
        """关闭当前Python运行"""
        sys.exit()

    def run_steam_link(self):
        try:
            subprocess.run(['moonlight', 'stream'], check=True)
        except:
            return


#self.root.bind("<Button-1>", self.show_options)
            # self.root.bind("<Motion>", self.handle_mouse_motion)

    # def display_image(self):
    #     if self.prevent_update:
    #         return
    #     if self.index >= len(self.imgs):
    #         self.index = 0  # 重置索引，循环显示图片
    #         self.shuffle_images()  # 每当遍历完一遍图片后，重新洗牌
    #     img_path = self.imgs[self.index]  # 直接使用完整路径
    #     extension = os.path.splitext(img_path)[1].lower()
    #     if extension == '.gif':
    #         self.display_gif(img_path)  # 显示GIF动画
    #     else:
    #         img = Image.open(img_path)
    #         photo = ImageTk.PhotoImage(img)
    #         if hasattr(self, 'label'):
    #             self.label.config(image=photo)
    #             self.label.image = photo
    #         else:
    #             self.label = tk.Label(self.root, image=photo)
    #             self.label.image = photo
    #             self.label.pack()
    #     self.index += 1
    #     if not self.prevent_update:
    #         self.root.after(40000, self.display_image)  # 每40秒更换一次图片

    # def display_gif(self, gif_path):
    #     # 初始化GIF动画的帧索引
    #     if not hasattr(self, 'gif_frame'):
    #         self.gif_frame = 0
    #     self.gif = tk.PhotoImage(file=gif_path, format=f"gif -index {self.gif_frame}")
    #     if hasattr(self, 'label'):
    #         self.label.config(image=self.gif)
    #         self.label.image = self.gif
    #     else:
    #         self.label = tk.Label(self.root, image=self.gif)
    #         self.label.image = self.gif
    #         self.label.pack()
        
    #     self.gif_frame += 1
    #     try:
    #         self.root.after(100, self.display_gif, gif_path)  # 尝试显示下一帧
    #     except tk.TclError:
    #         self.gif_frame = 0  # 如果超出帧数，重置回第一帧
    #         self.root.after(100, self.display_gif, gif_path)


    # def handle_mouse_motion(self, event):
    #     self.show_buttons()
    #     # 每次鼠标移动时取消之前的计时器
    #     if self.hide_buttons_id is not None:
    #         self.root.after_cancel(self.hide_buttons_id)
    #     # 设置10秒后隐藏按钮的计时器
    #     self.hide_buttons_id = self.root.after(10000, self.hide_buttons)

    # def show_buttons(self):
    #     # 检查按钮是否已经存在且当前是隐藏的
    #     if not hasattr(self, 'buttons_frame'):
    #         self.create_buttons()
    #     elif not self.buttons_visible:
    #         self.toggle_buttons_visibility()
    #     self.buttons_frame.lift()

    # def hide_buttons(self):
    #     # 直接检查按钮是否已经隐藏，如果没有，则隐藏它们
    #     if self.buttons_visible:
    #         self.toggle_buttons_visibility()

    # def create_buttons(self):
    #     print("开始创建按钮")
    #     self.buttons_frame = tk.Frame(self.root,bg="gray")  # 创建一个装载按钮的框架
    #     self.btn_option1 = tk.Button(self.buttons_frame, text="Option 1", command=lambda: print("Option 1 clicked"))
    #     self.btn_option2 = tk.Button(self.buttons_frame, text="Option 2", command=lambda: print("Option 2 clicked"))
    #     self.buttons_frame.pack(side=tk.TOP, fill=tk.X)  # 在顶部填充整个宽度
    #     self.btn_option1.pack(side=tk.LEFT, padx=5, expand=True)  # 使按钮均匀分布
    #     self.btn_option2.pack(side=tk.LEFT, padx=5, expand=True)
    #     # 初始时显不显示按钮
    #     self.buttons_visible = True  # 控制按钮的可见状态
    #     self.buttons_frame.lift()
    #     print("创建按钮设置完成")

    # def toggle_buttons_visibility(self):
        
    #     if self.buttons_visible:
    #         print("隐藏按钮")
    #         # 按钮当前是可见的，现在需要隐藏它们
    #         self.buttons_frame.pack_forget()
    #         self.buttons_visible = False
    #         self.prevent_update = False  # 允许继续图片更新
    #     else:
    #         print("显示按钮")
    #         # 按钮当前是隐藏的，现在需要显示它们
    #         self.buttons_frame.pack(side=tk.BOTTOM)  # 或其他适当的位置
    #         self.buttons_visible = True
    #         self.prevent_update = True  # 阻止图片更新
    #     time.sleep(5)

    # def show_options(self, event):
    #     if not hasattr(self, 'buttons_frame'):  # 如果按钮未创建，则创建它们
    #         print("按钮创建")
    #         self.create_buttons()
    #     self.toggle_buttons_visibility()  # 切换按钮的可见性



def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)

    input_dir = '/home/jo/E-album/input_image'  # 输入目录
    output_dir = '/home/jo/E-album/output_image'  # 输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 创建输出目录，如果它不存在

    album = PhotoAlbum(root, input_dir, output_dir)

    root.mainloop()

if __name__ == "__main__":
    main()