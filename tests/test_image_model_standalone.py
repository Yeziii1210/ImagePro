"""
单独测试ImageModel类
"""
import os
import sys
import unittest
import numpy as np
import cv2
import importlib.util
from pathlib import Path

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 添加app目录到sys.path
app_dir = os.path.join(project_root, "app")
sys.path.insert(0, app_dir)

# 导入模块的函数
def import_module_from_file(module_name, file_path):
    """从文件路径导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 预加载必要的模块
try:
    # 先导入config模块
    config_file = os.path.join(project_root, "app", "config.py")
    config_module = import_module_from_file("config", config_file)
    sys.modules["app.config"] = config_module
    
    # 导入image_model模块
    model_file = os.path.join(project_root, "models", "image_model.py")
    image_model_module = import_module_from_file("image_model", model_file)
    from image_model import ImageModel
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestImageModel(unittest.TestCase):
    """测试ImageModel类"""

    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.model = ImageModel()
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图像文件
        self.test_image_path = self.test_dir / "test_image.png"
        self._create_test_image()
    
    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 释放模型引用
        self.model = None
        
        # 删除测试图像
        if self.test_image_path.exists():
            self.test_image_path.unlink()
    
    def _create_test_image(self):
        """创建测试图像"""
        # 创建一个100x100的RGB测试图像
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 绘制一些形状，使图像包含一些内容
        # 红色矩形
        image[20:40, 20:40] = [255, 0, 0]
        # 绿色矩形
        image[20:40, 60:80] = [0, 255, 0]
        # 蓝色矩形
        image[60:80, 20:40] = [0, 0, 255]
        # 白色矩形
        image[60:80, 60:80] = [255, 255, 255]
        
        # 保存图像
        cv2.imwrite(str(self.test_image_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.model.original_image)
        self.assertIsNone(self.model.current_image)
        self.assertFalse(self.model.has_image())
        self.assertFalse(self.model.can_undo())
        self.assertFalse(self.model.can_redo())
    
    def test_load_image(self):
        """测试加载图像"""
        # 加载测试图像
        result = self.model.load_image(str(self.test_image_path))
        
        # 验证加载成功
        self.assertTrue(result)
        self.assertTrue(self.model.has_image())
        self.assertIsNotNone(self.model.original_image)
        self.assertIsNotNone(self.model.current_image)
        
        # 验证图像尺寸
        self.assertEqual(self.model.original_image.shape[0], 100)  # 高度
        self.assertEqual(self.model.original_image.shape[1], 100)  # 宽度
        self.assertEqual(self.model.original_image.shape[2], 3)    # 通道数
    
    def test_save_image(self):
        """测试保存图像"""
        # 先加载图像
        self.model.load_image(str(self.test_image_path))
        
        # 保存到新位置
        save_path = self.test_dir / "test_save.png"
        if save_path.exists():
            save_path.unlink()
        
        result = self.model.save_image(str(save_path))
        
        # 验证保存成功
        self.assertTrue(result)
        self.assertTrue(save_path.exists())
        
        # 清理
        if save_path.exists():
            save_path.unlink()
    
    def test_undo(self):
        """测试撤销功能"""
        # 先加载图像
        self.model.load_image(str(self.test_image_path))
        
        # 获取原始图像的副本
        original_image = self.model.current_image.copy()
        
        # 应用一个简单操作，将图像设为全黑
        def make_black(image):
            return np.zeros_like(image)
        
        # 应用操作并检查图像已变化
        self.model.apply_operation(make_black)
        modified_image = self.model.current_image
        self.assertEqual(np.sum(modified_image), 0, "图像应该全黑")
        
        # 测试撤销
        self.assertTrue(self.model.can_undo())
        self.model.undo()
        
        # 验证撤销后的图像与原始图像相同
        self.assertTrue(np.array_equal(original_image, self.model.current_image))
    
    def test_redo(self):
        """测试重做功能"""
        # 先加载图像
        self.model.load_image(str(self.test_image_path))
        
        # 应用一个操作
        def make_white(image):
            return np.ones_like(image) * 255
        
        self.model.apply_operation(make_white)
        
        # 验证图像已变白
        self.assertTrue(np.mean(self.model.current_image) > 254)
        
        # 撤销操作
        self.model.undo()
        
        # 检查redo是否可用
        self.assertTrue(self.model.can_redo())
    
    def test_reset(self):
        """测试重置功能"""
        # 先加载图像
        self.model.load_image(str(self.test_image_path))
        
        # 获取原始图像的副本
        original_image = self.model.original_image.copy()
        
        # 应用一个操作，使图像变为灰度
        def to_grayscale(image):
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        self.model.apply_operation(to_grayscale)
        
        # 验证图像已变化
        self.assertFalse(np.array_equal(original_image, self.model.current_image))
        
        # 重置图像
        self.model.reset()
        
        # 验证重置后的图像与原始图像相同
        self.assertTrue(np.array_equal(original_image, self.model.current_image))
    
    def test_preview_operation(self):
        """测试操作预览功能"""
        # 先加载图像
        self.model.load_image(str(self.test_image_path))
        
        # 获取原始图像的副本
        original_image = self.model.current_image.copy()
        
        # 应用预览操作，使图像变为灰度
        def to_grayscale(image):
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        result = self.model.preview_operation(to_grayscale)
        
        # 验证预览成功
        self.assertTrue(result)
        
        # 验证图像已变化
        self.assertFalse(np.array_equal(original_image, self.model.current_image))
        
        # 验证历史记录未变化（预览不应该添加到历史记录）
        self.assertFalse(self.model.can_undo())
        
        # 应用预览
        self.model.apply_last_preview()
        
        # 验证应用后可以撤销
        self.assertTrue(self.model.can_undo())

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestImageModel,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 