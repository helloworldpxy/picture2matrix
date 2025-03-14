'''
Written by: HelloWorld05 in 20250315
picture2matrix是一个简易的把图片文件转化成矩阵并输出的项目 
version: 0.9beta

'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np
import os

class ImageMatrixConverter:
    def __init__(self, master):
        self.master = master
        master.title("picture2matrix")
        master.resizable(False, False)

        # 初始化变量
        self.file_path = ""
        self.output_path = ""

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack()

        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="选择图片", padding=10)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_open = ttk.Button(
            file_frame,
            text="打开JPG文件",
            command=self.select_file
        )
        self.btn_open.pack(side="left")

        self.lbl_file = ttk.Label(file_frame, text="未选择文件", foreground="gray")
        self.lbl_file.pack(side="left", padx=10)

        # 输出目录部分
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding=10)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_output = ttk.Button(
            output_frame,
            text="选择输出目录",
            command=self.select_output
        )
        self.btn_output.pack(side="left")

        self.lbl_output = ttk.Label(output_frame, text="未选择目录", foreground="gray")
        self.lbl_output.pack(side="left", padx=10)

        # 转换按钮
        self.btn_convert = ttk.Button(
            main_frame,
            text="转换为矩阵",
            command=self.convert_image,
            state="disabled"
        )
        self.btn_convert.grid(row=2, column=0, pady=10)

        # 状态栏
        self.status_bar = ttk.Label(main_frame, text="就绪", foreground="gray")
        self.status_bar.grid(row=3, column=0)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JPG文件", "*.jpg;*.jpeg")]
        )
        if file_path:
            self.file_path = file_path
            self.lbl_file.config(text=os.path.basename(file_path), foreground="black")
            self.check_ready()

    def select_output(self):
        output_path = filedialog.askdirectory()
        if output_path:
            self.output_path = output_path
            self.lbl_output.config(text=output_path, foreground="black")
            self.check_ready()

    def check_ready(self):
        if self.file_path and self.output_path:
            self.btn_convert["state"] = "normal"
        else:
            self.btn_convert["state"] = "disabled"

    def convert_image(self):
        try:
            # 打开并转换图像
            with Image.open(self.file_path) as img:
                # 转换为灰度图像
                gray_img = img.convert('L')
                img_array = np.array(gray_img)

            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            output_file = os.path.join(self.output_path, f"{base_name}_matrix.txt")

            # 保存矩阵数据
            np.savetxt(output_file, img_array, fmt="%3d", delimiter=",")
            
            self.status_bar.config(text=f"转换成功：{output_file}", foreground="green")
            messagebox.showinfo("完成", "文件转换成功！")
        except Exception as e:
            self.status_bar.config(text=f"错误：{str(e)}", foreground="red")
            messagebox.showerror("错误", f"转换失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMatrixConverter(root)
    root.mainloop()