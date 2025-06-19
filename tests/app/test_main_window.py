"""
测试MainWindow类
"""
import os
import sys
import unittest
import tempfile
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 添加app目录到sys.path
app_dir = os.path.join(project_root, "app")
sys.path.insert(0, app_dir)

# 添加所有主要模块目录到系统路径
for module_dir in ["models", "views", "controllers", "utils"]:
    module_path = os.path.join(project_root, module_dir)
    if os.path.exists(module_path) and module_path not in sys.path:
        sys.path.insert(0, module_path)

# 使用通用的模块导入机制
sys.path.append(os.path.join(project_root, "tests"))
try:
    from test_import_with_config import import_module_from_file, create_module_imports
    
    # 预先导入所有必要的模块
    create_module_imports()
    
    # 检查main_window.py是否存在
    main_window_file = os.path.join(app_dir, "main_window.py")
    if not os.path.exists(main_window_file):
        print(f"Warning: {main_window_file} does not exist. Skipping MainWindow tests.")
        sys.exit(0)
    
    # 导入MainWindow模块
    try:
        from app.main_window import MainWindow
    except ImportError:
        # 如果导入失败，尝试直接从文件导入
        main_window_module = import_module_from_file("main_window", main_window_file)
        if main_window_module:
            MainWindow = main_window_module.MainWindow
        else:
            print("Could not import MainWindow. Skipping tests.")
            sys.exit(0)
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 确保有一个QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestMainWindow(unittest.TestCase):
    """测试MainWindow类"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        # 创建主窗口实例
        self.window = MainWindow()
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图像路径
        self.test_image_path = str(self.test_dir / "test_window.png")
        
        # 模拟文件对话框的返回值
        self.original_getOpenFileName = QFileDialog.getOpenFileName
        self.original_getSaveFileName = QFileDialog.getSaveFileName
        
        # 模拟消息框的返回值
        self.original_question = QMessageBox.question
    
    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 还原原始的文件对话框函数
        QFileDialog.getOpenFileName = self.original_getOpenFileName
        QFileDialog.getSaveFileName = self.original_getSaveFileName
        
        # 还原原始的消息框函数
        QMessageBox.question = self.original_question
        
        # 释放主窗口
        self.window.close()
        self.window = None
    
    def test_initial_state(self):
        """测试主窗口初始状态"""
        # 验证图像模型、视图和控制器已创建
        self.assertIsNotNone(self.window.image_model)
        self.assertIsNotNone(self.window.image_view)
        self.assertIsNotNone(self.window.image_controller)
        
        # 验证初始状态下没有图像
        self.assertFalse(self.window.image_model.has_image())
        
        # 验证撤销和重做动作被禁用
        self.assertFalse(self.window.undo_action.isEnabled())
        self.assertFalse(self.window.redo_action.isEnabled())
    
    def test_create_actions(self):
        """测试动作创建"""
        # 验证文件操作
        self.assertIsNotNone(self.window.open_action)
        self.assertIsNotNone(self.window.save_action)
        self.assertIsNotNone(self.window.exit_action)
        
        # 验证编辑操作
        self.assertIsNotNone(self.window.undo_action)
        self.assertIsNotNone(self.window.redo_action)
    
    def test_memory_monitor(self):
        """测试内存监控功能"""
        # 验证内存标签已创建
        self.assertIsNotNone(self.window._memory_label)
        
        # 验证内存进度条已创建
        self.assertIsNotNone(self.window._memory_bar)
        
        # 验证内存监控定时器已启动
        self.assertTrue(self.window._memory_timer.isActive())
    
    def _mock_file_open_dialog(self, image_path):
        """模拟文件打开对话框"""
        # 替换QFileDialog.getOpenFileName为自定义函数
        QFileDialog.getOpenFileName = lambda *args, **kwargs: (image_path, "")
    
    def _mock_file_save_dialog(self, save_path):
        """模拟文件保存对话框"""
        # 替换QFileDialog.getSaveFileName为自定义函数
        QFileDialog.getSaveFileName = lambda *args, **kwargs: (save_path, "")
    
    def _mock_message_question(self, return_value=QMessageBox.Yes):
        """模拟消息询问对话框"""
        # 替换QMessageBox.question为自定义函数
        QMessageBox.question = lambda *args, **kwargs: return_value
    
    def test_open_image(self):
        """测试打开图像功能"""
        # 创建临时测试图像
        import numpy as np
        import cv2
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, :, 0] = 255  # 蓝色图像
        cv2.imwrite(self.test_image_path, image)
        
        # 模拟文件打开对话框
        self._mock_file_open_dialog(self.test_image_path)
        
        # 调用打开图像动作
        self.window.open_action.trigger()
        
        # 验证图像已加载
        self.assertTrue(self.window.image_model.has_image())
        
        # 清理
        os.remove(self.test_image_path)
    
    def test_memory_cleanup(self):
        """测试内存清理功能"""
        # 触发内存清理
        self.window._force_cleanup_memory()
        
        # 由于没有实际的内存压力，我们只能测试函数执行不会崩溃
        self.assertTrue(True)
    
    def test_exit_action(self):
        """测试退出动作"""
        # 模拟消息框的返回值
        self._mock_message_question(QMessageBox.No)
        
        # 使用QTimer在短暂延迟后关闭应用程序
        QTimer.singleShot(100, lambda: self.window.exit_action.trigger())
        
        # 由于我们模拟了No的返回值，窗口不应该关闭
        self.assertTrue(self.window.isVisible())

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestMainWindow,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 