"""
测试ImageView类
"""
import os
import sys
import unittest
import numpy as np
import cv2
from pathlib import Path
import tempfile

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
    
    # 导入模块
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QSize, QRect, QRectF
    from PySide6.QtGui import QImage, QTransform
    from views.image_view import ImageView
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 创建QApplication实例
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestImageView(unittest.TestCase):
    """测试ImageView类"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.view = ImageView()
        self.view.resize(200, 200)  # 设置视图大小，避免获取区域时出错
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图像
        self.test_image = self._create_test_image()
    
    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 释放视图引用
        self.view = None
    
    def _create_test_image(self):
        """创建测试图像（QImage）"""
        # 创建一个100x100的RGB测试图像
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 添加一些形状以便识别
        # 红色矩形
        img_array[20:40, 20:40] = [255, 0, 0]
        # 绿色矩形
        img_array[20:40, 60:80] = [0, 255, 0]
        # 蓝色矩形
        img_array[60:80, 20:40] = [0, 0, 255]
        # 白色矩形
        img_array[60:80, 60:80] = [255, 255, 255]
        
        # 转换为QImage
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return q_image
    
    def test_set_image(self):
        """测试设置图像功能"""
        # 设置图像
        self.view.set_image(self.test_image)
        
        # 验证图像已设置
        self.assertIsNotNone(self.view._image)
        self.assertIsNotNone(self.view._pixmap_item)
    
    def test_fit_in_view(self):
        """测试适应视图功能"""
        # 设置图像
        self.view.set_image(self.test_image)
        
        # 调用适应视图方法
        self.view.fit_in_view()
        
        # 验证缩放因子被更新
        self.assertGreater(self.view._scale_factor, 0)
    
    def test_get_image_region(self):
        """测试获取图像区域功能"""
        # 设置图像
        self.view.set_image(self.test_image)
        
        # 定义区域 - 使用QRectF而不是QRect
        rect = QRectF(10, 10, 50, 50)
        
        # 获取区域
        region = self.view.get_image_region(rect)
        
        # 验证返回的区域是有效的
        self.assertIsNotNone(region)
        
        # 验证返回的区域大小合理（可能会因视图转换有所不同）
        self.assertGreater(region.width(), 0)
        self.assertGreater(region.height(), 0)
    
    def test_clear_cache(self):
        """测试清除缓存功能"""
        # 设置图像
        self.view.set_image(self.test_image)
        
        # 模拟一些缩放操作，填充缓存
        self.view._cache.put("scale_1.10", QTransform().scale(1.1, 1.1))
        self.view._cache.put("scale_1.20", QTransform().scale(1.2, 1.2))
        
        # 清除缓存
        self.view.clear_cache()
        
        # 验证缓存已清空
        self.assertEqual(len(self.view._cache), 0)

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestImageView,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 