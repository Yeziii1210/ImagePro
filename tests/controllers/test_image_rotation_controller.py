"""
测试图像控制器的旋转功能
"""
import os
import sys
import unittest
import numpy as np
import cv2
from pathlib import Path

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
    from models.image_model import ImageModel
    from controllers.image_controller import ImageController
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestImageRotationController(unittest.TestCase):
    """测试图像控制器的旋转功能"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.model = ImageModel()
        self.controller = ImageController(self.model)
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图像文件
        self.test_image_path = self.test_dir / "test_rotation_controller.png"
        self._create_test_image()
        
        # 加载测试图像
        self.model.load_image(str(self.test_image_path))
        
        # 创建输出目录，用于保存测试结果图像
        self.output_path = self.test_dir / "rotation_controller_test"
        self.output_path.mkdir(exist_ok=True)
    
    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 释放模型和控制器的引用
        self.controller = None
        self.model = None
        
        # 删除测试图像
        if self.test_image_path.exists():
            self.test_image_path.unlink()
    
    def _create_test_image(self):
        """创建测试图像"""
        # 创建一个100x100的RGB测试图像
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 添加一个红色矩形，便于看清旋转效果
        # 注意：OpenCV使用BGR格式，但保存后加载到模型中会转换为RGB格式
        image[40:60, 20:80] = [0, 0, 255]  # BGR格式，红色
        
        # 保存图像
        cv2.imwrite(str(self.test_image_path), image)
    
    def _save_current_image(self, filename):
        """保存当前图像"""
        # 将当前图像保存到输出目录
        bgr_image = cv2.cvtColor(self.model.current_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(self.output_path / filename), bgr_image)
    
    def test_rotate_90_degrees(self):
        """测试旋转90度"""
        # 保存原始图像
        self._save_current_image("original.png")
        
        # 应用90度旋转
        result = self.controller.rotate_image(90)
        
        # 保存旋转后的图像
        self._save_current_image("rotated_90.png")
        
        # 验证操作成功
        self.assertTrue(result)
        
        # 验证图像已经被修改
        # 我们应该能够撤销操作
        self.assertTrue(self.model.can_undo())
        
        # 验证旋转后图像与原始图像不同
        self.assertFalse(np.array_equal(
            cv2.imread(str(self.output_path / "original.png")), 
            cv2.imread(str(self.output_path / "rotated_90.png"))
        ))
    
    def test_rotate_180_degrees(self):
        """测试旋转180度"""
        # 保存原始图像
        self._save_current_image("original.png")
        
        # 应用180度旋转
        result = self.controller.rotate_image(180)
        
        # 保存旋转后的图像
        self._save_current_image("rotated_180.png")
        
        # 验证操作成功
        self.assertTrue(result)
        
        # 验证图像已经被修改
        # 验证旋转后图像与原始图像不同
        self.assertFalse(np.array_equal(
            cv2.imread(str(self.output_path / "original.png")), 
            cv2.imread(str(self.output_path / "rotated_180.png"))
        ))
    
    def test_rotate_with_expand(self):
        """测试使用expand参数旋转图像"""
        # 保存原始图像
        self._save_current_image("original.png")
        
        # 应用45度旋转并扩展图像
        result = self.controller.rotate_image(45, expand=True)
        
        # 保存旋转后的图像
        self._save_current_image("rotated_45_expand.png")
        
        # 验证操作成功
        self.assertTrue(result)
        
        # 验证图像已经被修改
        # 检查旋转后的图像与原始图像不同
        original_image = cv2.imread(str(self.output_path / "original.png"))
        rotated_image = cv2.imread(str(self.output_path / "rotated_45_expand.png"))
        
        # 图像尺寸应该不同（因为expand=True）
        self.assertNotEqual(original_image.shape, rotated_image.shape)
        
        # 旋转后的图像应该更大
        self.assertGreater(rotated_image.shape[0], original_image.shape[0])
        self.assertGreater(rotated_image.shape[1], original_image.shape[1])
    
    def test_preview_and_apply_rotation(self):
        """测试预览旋转功能和应用预览"""
        # 保存原始图像
        self._save_current_image("original.png")
        
        # 应用预览旋转45度
        result = self.controller.preview_rotate_image(45)
        
        # 保存预览图像
        self._save_current_image("preview_45.png")
        
        # 验证预览成功
        self.assertTrue(result)
        
        # 验证预览不会加入历史记录（不能撤销）
        self.assertFalse(self.model.can_undo())
        
        # 应用预览
        self.controller.apply_last_preview()
        
        # 保存应用预览后的图像
        self._save_current_image("applied_preview_45.png")
        
        # 验证现在可以撤销
        self.assertTrue(self.model.can_undo())
        
        # 验证图像已经被修改
        self.assertFalse(np.array_equal(
            cv2.imread(str(self.output_path / "original.png")), 
            cv2.imread(str(self.output_path / "applied_preview_45.png"))
        ))
        
        # 撤销操作
        self.model.undo()
        
        # 保存撤销后的图像
        self._save_current_image("undo.png")
        
        # 验证撤销后图像内容与原始图像相似
        # 由于保存和重新加载可能会有轻微差异，我们比较图像的主要特征
        original = cv2.imread(str(self.output_path / "original.png"))
        undo = cv2.imread(str(self.output_path / "undo.png"))
        
        # 计算图像差异
        diff = cv2.absdiff(original, undo)
        mean_diff = np.mean(diff)
        
        # 差异应该很小
        self.assertLess(mean_diff, 1.0)

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestImageRotationController,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 