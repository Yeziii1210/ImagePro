"""
测试ImageController类
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
    from models.image_model import ImageModel
    from controllers.image_controller import ImageController
except Exception as e:
    print(f"预加载模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestImageController(unittest.TestCase):
    """测试ImageController类"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.model = ImageModel()
        self.controller = ImageController(self.model)
        
        # 创建测试资源目录
        self.test_dir = Path(project_root) / "tests" / "resources"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图像文件
        self.test_image_path = self.test_dir / "test_controller.png"
        self._create_test_image()
        
        # 加载测试图像
        self.model.load_image(str(self.test_image_path))
    
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
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128  # 中灰色图像
        
        # 添加一些颜色变化，以便测试对比度
        image[30:70, 30:70, 0] = 100  # R通道暗一些
        image[30:70, 30:70, 1] = 150  # G通道亮一些
        image[30:70, 30:70, 2] = 200  # B通道更亮
        
        # 保存图像
        cv2.imwrite(str(self.test_image_path), image)
    
    def _calculate_image_stats(self, image):
        """计算图像统计信息（平均值和标准差）"""
        mean = np.mean(image, axis=(0, 1))
        std = np.std(image, axis=(0, 1))
        return mean, std
    
    def test_adjust_brightness_contrast(self):
        """测试亮度对比度调整功能"""
        # 测试亮度增加
        # 获取原始图像统计信息
        original_image = self.model.current_image.copy()
        original_mean, original_std = self._calculate_image_stats(original_image)
        
        # 使用极端值进行亮度增加测试（增加50）
        self.controller.adjust_brightness_contrast(50, 1.0)
        bright_image = self.model.current_image.copy()
        bright_mean, bright_std = self._calculate_image_stats(bright_image)
        
        # 验证亮度增加
        self.assertTrue(np.mean(bright_mean) > np.mean(original_mean), 
                      f"平均亮度应该增加，原始：{np.mean(original_mean)}，调整后：{np.mean(bright_mean)}")
        
        # 撤销操作
        self.model.undo()
        
        # 使用极端值测试对比度增加（对比度系数2.0）
        original_image = self.model.current_image.copy()  # 重新获取原始图像
        original_mean, original_std = self._calculate_image_stats(original_image)
        
        self.controller.adjust_brightness_contrast(0, 2.0)
        contrast_image = self.model.current_image.copy()
        contrast_mean, contrast_std = self._calculate_image_stats(contrast_image)
        
        # 验证对比度增加（至少一个通道的标准差应增加）
        # 注意：对比度增加不一定使所有通道的标准差都增加
        self.assertTrue(np.any(contrast_std > original_std),
                      f"至少一个通道的标准差应该增加，原始：{original_std}，调整后：{contrast_std}")
    
    def test_apply_gaussian_blur(self):
        """测试高斯模糊功能"""
        # 获取原始图像
        original_image = self.model.current_image.copy()
        
        # 向图像添加一些噪声，使高斯模糊效果更明显
        noisy_image = original_image.copy()
        noise = np.random.randint(0, 50, original_image.shape, dtype=np.uint8)
        noisy_image = cv2.add(noisy_image, noise)
        
        # 将带噪声的图像设置为当前图像
        def set_noisy(image):
            return noisy_image
        
        self.model.apply_operation(set_noisy)
        
        # 应用高斯模糊
        self.controller.apply_gaussian_blur(5, 0)
        blurred_image = self.model.current_image.copy()
        
        # 计算原始图像和模糊图像之间的差异
        diff = cv2.absdiff(noisy_image, blurred_image)
        
        # 验证图像变化
        self.assertTrue(np.mean(diff) > 0)
    
    def test_apply_median_blur(self):
        """测试中值滤波功能"""
        # 获取原始图像
        original_image = self.model.current_image.copy()
        
        # 向图像添加一些椒盐噪声，使中值滤波效果更明显
        noisy_image = original_image.copy()
        num_salt = np.ceil(0.05 * original_image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in original_image.shape[:2]]
        noisy_image[coords[0], coords[1]] = 255
        
        num_pepper = np.ceil(0.05 * original_image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in original_image.shape[:2]]
        noisy_image[coords[0], coords[1]] = 0
        
        # 将带噪声的图像设置为当前图像
        def set_noisy(image):
            return noisy_image
        
        self.model.apply_operation(set_noisy)
        
        # 应用中值滤波
        self.controller.apply_median_blur(5)
        filtered_image = self.model.current_image.copy()
        
        # 计算原始图像和滤波图像之间的差异
        diff = cv2.absdiff(noisy_image, filtered_image)
        
        # 验证图像变化
        self.assertTrue(np.mean(diff) > 0)
    
    def test_convert_to_grayscale(self):
        """测试灰度转换功能"""
        # 获取原始图像
        original_image = self.model.current_image.copy()
        
        # 应用灰度转换
        self.controller.convert_to_grayscale()
        gray_image = self.model.current_image.copy()
        
        # 验证图像变化 - 检查是否为灰度图像
        if len(gray_image.shape) == 3 and gray_image.shape[2] == 3:
            # 对于3通道图像，检查所有通道是否具有相同的值
            channel_diff = np.abs(gray_image[:,:,0] - gray_image[:,:,1]).sum() + \
                          np.abs(gray_image[:,:,1] - gray_image[:,:,2]).sum()
            self.assertTrue(channel_diff < original_image.size * 0.01, 
                           "通道之间应该几乎没有差异")
        else:
            # 如果已经是单通道图像，则验证通过
            self.assertTrue(True)
    
    def test_preview_brightness_contrast(self):
        """测试亮度对比度预览功能"""
        # 获取原始图像
        original_image = self.model.current_image.copy()
        
        # 应用预览
        self.controller.preview_brightness_contrast(50, 1.5)
        preview_image = self.model.current_image.copy()
        
        # 验证图像已变化
        self.assertFalse(np.array_equal(original_image, preview_image))
        
        # 验证历史记录未变化（预览不应该添加到历史记录）
        self.assertFalse(self.model.can_undo())
        
        # 应用预览
        self.controller.apply_last_preview()
        
        # 验证应用后可以撤销
        self.assertTrue(self.model.can_undo())

def load_tests(loader, standard_tests, pattern):
    """自定义测试加载函数，使unittest发现所有测试"""
    suite = unittest.TestSuite()
    for test_class in (TestImageController,):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite

if __name__ == "__main__":
    unittest.main() 