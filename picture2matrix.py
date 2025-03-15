'''
Written by: HelloWorld05 in 20250315
picture2matrix是一个简易的把图片文件转化成矩阵并输出的项目 
version: 1.0
'''
import tkinter as tk
from tkinter import ttk, filedialog, Menu, messagebox
from PIL import Image
import numpy as np
import os
import sys

class Tooltip:
    def __init__(self, widget, get_text):
        self.widget = widget
        self.get_text = get_text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        text = self.get_text()
        if not text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip, 
            text=text, 
            background="#ffffe0", 
            relief="solid", 
            borderwidth=1,
            padding=3
        )
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ImageMatrixConverter:
    def __init__(self, master):
        self.master = master
        master.title("picture2matrix v1.0")
        master.resizable(False, False)
        self.file_path = ""
        self.output_path = ""
        self.create_menu()
        self.init_ui()
        
        # 添加工具提示
        Tooltip(self.lbl_file, lambda: self.file_path)
        Tooltip(self.lbl_output, lambda: self.output_path)

    def create_menu(self):
        menubar = Menu(self.master)
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.master.config(menu=menubar)

    def init_ui(self):
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack()

        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="请选择图片文件", padding=10)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_open = ttk.Button(
            file_frame,
            text="打开图片文件",
            command=self.select_file,
            width=15
        )
        self.btn_open.pack(side="left")

        self.lbl_file = ttk.Label(file_frame, text="未选择文件", foreground="gray", width=40)
        self.lbl_file.pack(side="left", padx=10)

        # 输出设置部分
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding=10)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_output = ttk.Button(
            output_frame,
            text="选择输出目录",
            command=self.select_output,
            width=15
        )
        self.btn_output.pack(side="left")

        self.lbl_output = ttk.Label(output_frame, text="未选择目录", foreground="gray", width=30)
        self.lbl_output.pack(side="left", padx=10)

        self.format_var = tk.StringVar(value="txt")
        format_combo = ttk.Combobox(
            output_frame,
            textvariable=self.format_var,
            values=["txt", "csv", "npy"],
            state="readonly",
            width=8
        )
        format_combo.pack(side="right", padx=5)
        ttk.Label(output_frame, text="输出格式:").pack(side="right")

        self.btn_convert = ttk.Button(
            main_frame,
            text="开始转换",
            command=self.convert_image,
            state="disabled",
            style="Accent.TButton"
        )
        self.btn_convert.grid(row=2, column=0, pady=10)

        self.status_bar = ttk.Label(main_frame, text="已就绪", foreground="gray")
        self.status_bar.grid(row=3, column=0)

    def select_file(self):
        file_types = [
            ('图像文件', '*.jpg;*.jpeg;*.png;*.bmp;*.tiff'),
            ('所有文件', '*.*')
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.file_path = file_path
            self.lbl_file.config(
                text=os.path.basename(file_path),
                foreground="black"
            )
            self.check_ready()

    def select_output(self):
        output_path = filedialog.askdirectory()
        if output_path:
            self.output_path = output_path
            self.lbl_output.config(
                text=os.path.basename(output_path),
                foreground="black"
            )
            self.check_ready()

    def check_ready(self):
        self.btn_convert["state"] = "normal" if self.file_path and self.output_path else "disabled"

    def convert_image(self):
        try:
            os.makedirs(self.output_path, exist_ok=True)
            
            with Image.open(self.file_path) as img:
                if img.mode not in ['L', 'RGB']:
                    if img.mode in ['RGBA', 'P']:
                        img = img.convert('RGB')
                    else:
                        img = img.convert('L')
                
                img_array = np.array(img)

            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            output_format = self.format_var.get()
            ext_map = {
                "txt": ".txt",
                "csv": ".csv",
                "npy": ".npy"
            }
            output_file = os.path.join(
                self.output_path,
                f"{base_name}_matrix{ext_map[output_format]}"
            )

            if output_format in ["txt", "csv"]:
                delimiter = "," if output_format == "csv" else " "
                if len(img_array.shape) == 3:
                    reshaped_array = img_array.reshape(-1, img_array.shape[-1])
                else:
                    reshaped_array = img_array
                
                np.savetxt(
                    output_file,
                    reshaped_array,
                    fmt="%d",
                    delimiter=delimiter
                )
            elif output_format == "npy":
                np.save(output_file, img_array)

            self.show_status(f"转换成功: {os.path.basename(output_file)}", "green")
            messagebox.showinfo("成功", "文件转换完成！")
        except Exception as e:
            self.show_status(f"错误: {str(e)}", "red")
            messagebox.showerror("错误", f"转换失败:\n{str(e)}")

    def show_status(self, text, color="gray"):
        self.status_bar.config(text=text, foreground=color)

    def show_about(self):
        about_text = f"""
        picture2matrix v1.0
        
        功能特性：
        - 支持多种图像格式：JPG/JPEG/PNG/BMP/TIFF
        - 可选的输出格式：TXT/CSV/NPY
        - 自动处理图像色彩模式
        - 改进的错误处理机制
        - 自动创建输出目录
        
        运行环境：
        Python {sys.version.split()[0]}
        Pillow {Image.__version__}
        NumPy {np.__version__}
        
        开发者主页：https://github.com/helloworldpxy
        """
        messagebox.showinfo("关于", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', foreground='white', background='#2c7fb8')
    app = ImageMatrixConverter(root)
    root.mainloop()