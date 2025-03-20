"""
Written by: HelloWorld05 in 20250321
picture2matrix是一个简易的把图片文件转化成矩阵并输出的项目 
version: 2.0
新增功能：
1. 现代暗黑主题界面
2. 实时矩阵预览
3. 批量文件转换
4. 进度条显示
5. 自动打开输出目录
6. 主题切换功能
7. 优化代码结构
"""
import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox,
                             QFileDialog, QProgressBar, QMessageBox, QListWidget, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QSplitter, QStyleFactory, QAction, QStyle)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from PIL import Image

class ConversionThread(QThread):
    progress_updated = pyqtSignal(int)
    conversion_finished = pyqtSignal(str, bool)
    
    def __init__(self, files, output_dir, format_type):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.format_type = format_type
        self.running = True

    def run(self):
        try:
            total = len(self.files)
            for idx, file_path in enumerate(self.files):
                if not self.running:
                    break
                
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(
                    self.output_dir,
                    f"{base_name}_matrix.{self.format_type.lower()}"
                )
                
                # 图像处理
                with Image.open(file_path) as img:
                    img = self.process_image_mode(img)
                    img_array = np.array(img)
                
                # 保存文件
                self.save_matrix(img_array, output_file)
                self.progress_updated.emit(int((idx+1)/total*100))
                
            self.conversion_finished.emit(self.output_dir, True)
        except Exception as e:
            self.conversion_finished.emit(str(e), False)

    def process_image_mode(self, img):
        if img.mode not in ['L', 'RGB']:
            return img.convert('RGB' if img.mode in ['RGBA', 'P'] else 'L')
        return img

    def save_matrix(self, array, path):
        if self.format_type == "NPY":
            np.save(path, array)
        else:
            delimiter = "," if self.format_type == "CSV" else " "
            reshaped = array.reshape(-1, array.shape[-1]) if len(array.shape) == 3 else array
            np.savetxt(path, reshaped, fmt="%d", delimiter=delimiter)

    def stop(self):
        self.running = False

class MatrixConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("picture2matrix v2.0")
        self.setGeometry(300, 200, 800, 600)
        self.files = []
        self.dark_mode = True
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        main_splitter = QSplitter(Qt.Vertical)
        
        # 控制面板
        control_panel = QWidget()
        grid = QGridLayout()
        
        # 文件选择
        self.btn_add = QPushButton("添加文件")
        self.btn_add.setFixedHeight(35)
        self.btn_add.clicked.connect(self.add_files)
        
        self.btn_clear = QPushButton("清空列表")
        self.btn_clear.setFixedHeight(35)
        self.btn_clear.clicked.connect(self.clear_files)
        
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        
        # 输出设置
        self.btn_output = QPushButton("选择输出目录")
        self.btn_output.setFixedHeight(35)
        self.btn_output.clicked.connect(self.select_output)
        
        self.lbl_output = QLabel("未选择输出目录")
        self.lbl_output.setAlignment(Qt.AlignCenter)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "CSV", "NPY"])
        self.format_combo.setFixedHeight(35)
        
        self.btn_theme = QPushButton("切换主题")
        self.btn_theme.setFixedHeight(35)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        
        # 操作按钮
        self.btn_convert = QPushButton("开始转换")
        self.btn_convert.setFixedHeight(45)
        self.btn_convert.clicked.connect(self.start_conversion)
        
        # 布局
        grid.addWidget(self.btn_add, 0, 0)
        grid.addWidget(self.btn_clear, 0, 1)
        grid.addWidget(self.file_list, 1, 0, 1, 2)
        grid.addWidget(self.btn_output, 2, 0)
        grid.addWidget(self.lbl_output, 2, 1)
        grid.addWidget(QLabel("输出格式:"), 3, 0)
        grid.addWidget(self.format_combo, 3, 1)
        grid.addWidget(self.btn_theme, 4, 0, 1, 2)
        grid.addWidget(self.progress, 5, 0, 1, 2)
        grid.addWidget(self.btn_convert, 6, 0, 1, 2)
        
        control_panel.setLayout(grid)
        
        # 预览面板
        preview_panel = QWidget()
        vbox = QVBoxLayout()
        self.preview_area = QLabel("矩阵预览区域")
        self.preview_area.setAlignment(Qt.AlignTop)
        self.preview_area.setWordWrap(True)
        self.preview_area.setStyleSheet("background: #333; padding: 10px;")
        
        vbox.addWidget(QLabel("实时预览:"))
        vbox.addWidget(self.preview_area)
        preview_panel.setLayout(vbox)
        
        main_splitter.addWidget(control_panel)
        main_splitter.addWidget(preview_panel)
        main_splitter.setSizes([400, 200])
        
        self.setCentralWidget(main_splitter)
        
        # 初始化工作线程
        self.conversion_thread = None

    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(dark_palette)
        self.setStyleSheet("""
            QPushButton { 
                background: #444; 
                border: 1px solid #555; 
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background: #555; }
            QComboBox { 
                background: #444; 
                color: white; 
                padding: 5px;
            }
            QListWidget { 
                background: #353535; 
                color: white;
            }
        """)

    def show_about(self):
        about_text = f"""
        <b>picture2matrix v2.0</b><br><br>
        
        <u>功能特性：</u>
        <ul>
            <li>支持多种图像格式：JPG/JPEG/PNG/BMP/TIFF</li>
            <li>可选的输出格式：TXT/CSV/NPY</li>
            <li>自动处理图像色彩模式</li>
            <li>改进的错误处理机制</li>
            <li>自动创建输出目录</li>
            <li>批量文件转换支持</li>
            <li>实时矩阵预览</li>
        </ul>
        
        <u>运行环境：</u>
        <ul>
            <li>Python {sys.version.split()[0]}</li>
            <li>Pillow {Image.__version__}</li>
            <li>NumPy {np.__version__}</li>
        </ul>
        
        开发者主页：<a href='https://github.com/helloworldpxy'>https://github.com/helloworldpxy</a>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("关于")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(
            self.style().standardPixmap(QStyle.SP_MessageBoxInformation)  
        )
        msg_box.exec_()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
            self.setStyleSheet("")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片文件", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        if files:
            self.files.extend(files)
            self.file_list.addItems([os.path.basename(f) for f in files])
            self.update_preview()

    def clear_files(self):
        self.files.clear()
        self.file_list.clear()
        self.preview_area.clear()

    def select_output(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.lbl_output.setText(directory)
            self.lbl_output.setToolTip(directory)

    def update_preview(self):
        if self.files:
            try:
                with Image.open(self.files[-1]) as img:
                    img = self.process_image_mode(img)
                    array = np.array(img)
                    preview_text = f"最新文件预览:\n{array.shape} 维矩阵\n示例数据:\n{array[:2, :2]}"
                    self.preview_area.setText(preview_text)
            except Exception as e:
                self.preview_area.setText(f"预览失败: {str(e)}")

    def start_conversion(self):
        if not self.files:
            QMessageBox.warning(self, "警告", "请先添加要转换的文件！")
            return
        if not self.lbl_output.text() or self.lbl_output.text() == "未选择输出目录":
            QMessageBox.warning(self, "警告", "请选择输出目录！")
            return
        
        self.btn_convert.setEnabled(False)
        self.progress.setValue(0)
        
        self.conversion_thread = ConversionThread(
            self.files,
            self.lbl_output.text(),
            self.format_combo.currentText()
        )
        self.conversion_thread.progress_updated.connect(self.update_progress)
        self.conversion_thread.conversion_finished.connect(self.conversion_done)
        self.conversion_thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def conversion_done(self, result, success):
        self.btn_convert.setEnabled(True)
        if success:
            QMessageBox.information(self, "完成", f"所有文件转换完成！\n输出目录：{result}")
            os.startfile(result)  # 自动打开输出目录
        else:
            QMessageBox.critical(self, "错误", f"转换失败：\n{result}")

    def closeEvent(self, event):
        if self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.stop()
            self.conversion_thread.quit()
            self.conversion_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = MatrixConverter()
    window.show()
    sys.exit(app.exec_())
