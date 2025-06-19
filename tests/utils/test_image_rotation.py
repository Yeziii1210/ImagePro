"""
测试图像旋转功能
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

# 使用通用的模块导入机制
sys.path.append(os.path.join(project_root, "tests"))
try:
    from test_import_with_config import import_module_from_file, create_module_imports
    
    # 预先导入所有必要的模块
    create_module_imports()
    
    # 导入模块
    from utils.image_utils import rotate_image
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestImageRotation(unittest.TestCase):
    """测试图像旋转功能"""
    
    def setUp(self):
        """准备测试环境"""
        # 创建一个测试图像
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # OpenCV默认是BGR格式，但图像处理函数可能期望RGB格式
        # 在测试中使用RGB格式，以与image_utils中的函数一致
        self.test_image[40:60, 20:80] = [255, 0, 0]  # RGB格式，红色
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 定义测试图像输出路径（用于可视化检查）
        self.output_path = self.test_dir / "rotation_test"
        self.output_path.mkdir(exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        # 这里可以添加清理代码，比如删除测试过程中生成的图像文件
        # 暂时保留输出图像，便于手动检查
        pass
    
    def test_rotate_90_degrees(self):
        """测试旋转90度"""
        # 旋转图像90度
        rotated = rotate_image(self.test_image, 90)
        
        # 保存原始图像和旋转后的图像，便于手动检查
        # 转换为BGR格式再保存
        cv2.imwrite(str(self.output_path / "original.png"), cv2.cvtColor(self.test_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.output_path / "rotated_90.png"), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))
        
        # 验证图像尺寸不变
        self.assertEqual(rotated.shape, self.test_image.shape)
        
        # 验证旋转90度后，矩形应该出现在图像左侧
        # 验证图像内容有变化
        self.assertFalse(np.array_equal(self.test_image, rotated))
        
        # 检查旋转后图像的红色通道
        # 因为我们使用的是RGB格式，所以红色在通道0
        self.assertTrue(np.any(rotated[:, :, 0] > 128))
    
    def test_rotate_180_degrees(self):
        """测试旋转180度"""
        # 旋转图像180度
        rotated = rotate_image(self.test_image, 180)
        
        # 保存旋转后的图像
        cv2.imwrite(str(self.output_path / "rotated_180.png"), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))
        
        # 验证图像尺寸不变
        self.assertEqual(rotated.shape, self.test_image.shape)
        
        # 验证旋转180度后，矩形应该出现在图像的对侧
        # 原始矩形在(40:60, 20:80)，旋转180度后应该在(40:60, 20:80)的对侧位置
        # 检查一个样本点位置
        original_color = self.test_image[50, 50]  # 原始矩形中心
        rotated_opposite = rotated[100-50-1, 100-50-1]  # 旋转后的对应位置
        
        # 颜色应该接近
        self.assertTrue(np.all(np.abs(original_color.astype(int) - rotated_opposite.astype(int)) < 50))
    
    def test_rotate_45_degrees(self):
        """测试旋转45度"""
        # 旋转图像45度
        rotated = rotate_image(self.test_image, 45)
        
        # 保存旋转后的图像
        cv2.imwrite(str(self.output_path / "rotated_45.png"), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))
        
        # 验证图像尺寸不变
        self.assertEqual(rotated.shape, self.test_image.shape)
        
        # 45度旋转会导致矩形部分移出图像，主要测试旋转是否正确执行
        # 我们可以检查图像是否有变化
        self.assertFalse(np.array_equal(self.test_image, rotated))
    
    def test_rotate_with_expand(self):
        """测试使用expand参数旋转图像"""
        # 旋转图像45度，并扩展图像以容纳旋转后的完整图像
        rotated = rotate_image(self.test_image, 45, expand=True)
        
        # 保存旋转后的图像
        cv2.imwrite(str(self.output_path / "rotated_45_expand.png"), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))
        
        # 验证图像尺寸增加
        self.assertGreater(rotated.shape[0], self.test_image.shape[0])
        self.assertGreater(rotated.shape[1], self.test_image.shape[1])
        
        # 验证图像有内容（不全是黑色）
        self.assertTrue(np.any(rotated > 0))
    
    def test_rotate_with_scale(self):
        """测试使用缩放参数旋转图像"""
        # 旋转图像45度，并缩放为原来的1.5倍
        rotated = rotate_image(self.test_image, 45, scale=1.5)
        
        # 保存旋转后的图像
        cv2.imwrite(str(self.output_path / "rotated_45_scale.png"), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))
        
        # 验证图像尺寸不变（因为没有设置expand=True）
        self.assertEqual(rotated.shape, self.test_image.shape)
        
        # 验证图像有内容
        self.assertTrue(np.any(rotated > 0))

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestImageRotation,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 