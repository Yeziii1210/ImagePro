# This Python file uses the following encoding: utf-8
import sys
import gc
import psutil
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from app.main_window import MainWindow
from app.config import config

def check_system_resources():
    """检查系统资源是否满足要求"""
    memory = psutil.virtual_memory()
    available_memory_gb = memory.available / (1024 * 1024 * 1024)
    
    if available_memory_gb < 1.0:  # 可用内存小于1GB
        print(f"警告: 可用内存较低 ({available_memory_gb:.1f}GB)，应用可能运行缓慢")
        return False
    return True

if __name__ == "__main__":
    # 强制进行一次垃圾回收，确保启动时内存占用最小
    gc.collect()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("ImagePro")
    
    # 创建并显示启动画面
    splash_pixmap = QPixmap(500, 300)
    splash_pixmap.fill(Qt.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents()
    
    # 检查系统资源
    check_system_resources()
    
    # 创建主窗口
    splash.showMessage("正在初始化界面...", Qt.AlignBottom | Qt.AlignHCenter, Qt.black)
    window = MainWindow()
    
    # 延迟显示主窗口，让启动画面多显示一会儿
    def show_main_window():
        window.show()
        splash.finish(window)
    
    QTimer.singleShot(1000, show_main_window)
    
    # 运行应用
    sys.exit(app.exec())
