"""
测试图像处理工具函数
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

from utils.image_utils import (
    adjust_brightness_contrast,
    apply_gaussian_blur,
    apply_median_blur,
    apply_bilateral_filter,
    convert_to_grayscale,
    apply_threshold,
    apply_adaptive_threshold
)

class TestImageUtils(unittest.TestCase):
    """测试图像处理工具函数"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        # 创建一个测试图像（100x100像素，灰色背景）
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # 在图像中添加一些几何形状，以便更好地测试处理效果
        # 红色矩形
        self.test_image[20:40, 20:40] = [255, 0, 0]
        # 绿色矩形
        self.test_image[20:40, 60:80] = [0, 255, 0]
        # 蓝色矩形
        self.test_image[60:80, 20:40] = [0, 0, 255]
        # 白色矩形
        self.test_image[60:80, 60:80] = [255, 255, 255]
        
        # 创建带噪声的图像版本
        self.noisy_image = self.test_image.copy()
        noise = np.random.randint(0, 50, self.test_image.shape, dtype=np.uint8)
        self.noisy_image = cv2.add(self.noisy_image, noise)
        
        # 创建带椒盐噪声的图像版本
        self.salt_pepper_image = self.test_image.copy()
        # 添加椒盐噪声
        num_salt = np.ceil(0.05 * self.test_image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in self.test_image.shape[:2]]
        self.salt_pepper_image[coords[0], coords[1]] = 255
        
        num_pepper = np.ceil(0.05 * self.test_image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in self.test_image.shape[:2]]
        self.salt_pepper_image[coords[0], coords[1]] = 0
    
    def _calculate_image_stats(self, image):
        """计算图像统计信息"""
        if len(image.shape) == 3:
            mean = np.mean(image, axis=(0, 1))
            std = np.std(image, axis=(0, 1))
        else:
            mean = np.mean(image)
            std = np.std(image)
        return mean, std
    
    def test_adjust_brightness_contrast(self):
        """测试亮度对比度调整功能"""
        # 获取原始图像统计信息
        original_mean, original_std = self._calculate_image_stats(self.test_image)
        
        # 测试增加亮度
        bright_image = adjust_brightness_contrast(self.test_image, brightness=50, contrast=1.0)
        bright_mean, _ = self._calculate_image_stats(bright_image)
        
        # 验证亮度增加
        self.assertTrue(np.all(bright_mean > original_mean))
        
        # 测试减少亮度
        dark_image = adjust_brightness_contrast(self.test_image, brightness=-50, contrast=1.0)
        dark_mean, _ = self._calculate_image_stats(dark_image)
        
        # 验证亮度减少
        self.assertTrue(np.all(dark_mean < original_mean))
        
        # 测试增加对比度
        contrast_image = adjust_brightness_contrast(self.test_image, brightness=0, contrast=1.5)
        _, contrast_std = self._calculate_image_stats(contrast_image)
        
        # 验证对比度增加
        self.assertTrue(np.all(contrast_std > original_std))
        
        # 测试减少对比度
        low_contrast_image = adjust_brightness_contrast(self.test_image, brightness=0, contrast=0.5)
        _, low_contrast_std = self._calculate_image_stats(low_contrast_image)
        
        # 验证对比度减少
        self.assertTrue(np.all(low_contrast_std < original_std))
    
    def test_apply_gaussian_blur(self):
        """测试高斯模糊功能"""
        # 应用高斯模糊
        blurred_image = apply_gaussian_blur(self.noisy_image, kernel_size=5, sigma=0)
        
        # 计算原始图像和模糊图像之间的差异
        diff = cv2.absdiff(self.noisy_image, blurred_image)
        
        # 验证图像变化
        self.assertTrue(np.mean(diff) > 0)
        
        # 验证噪声减少（通过比较标准差）
        _, noise_std = self._calculate_image_stats(self.noisy_image)
        _, blur_std = self._calculate_image_stats(blurred_image)
        
        # 模糊后的图像标准差应该更小（更平滑）
        self.assertTrue(np.all(blur_std < noise_std))
    
    def test_apply_median_blur(self):
        """测试中值滤波功能"""
        # 应用中值滤波
        filtered_image = apply_median_blur(self.salt_pepper_image, kernel_size=5)
        
        # 计算原始图像和滤波图像之间的差异
        diff = cv2.absdiff(self.salt_pepper_image, filtered_image)
        
        # 验证图像变化
        self.assertTrue(np.mean(diff) > 0)
        
        # 验证噪声减少
        self.assertTrue(np.count_nonzero(filtered_image == 0) < np.count_nonzero(self.salt_pepper_image == 0))
        self.assertTrue(np.count_nonzero(filtered_image == 255) < np.count_nonzero(self.salt_pepper_image == 255))
    
    def test_apply_bilateral_filter(self):
        """测试双边滤波功能"""
        # 应用双边滤波
        filtered_image = apply_bilateral_filter(self.noisy_image, d=9, sigma_color=75, sigma_space=75)
        
        # 计算原始图像和滤波图像之间的差异
        diff = cv2.absdiff(self.noisy_image, filtered_image)
        
        # 验证图像变化
        self.assertTrue(np.mean(diff) > 0)
    
    def test_convert_to_grayscale(self):
        """测试灰度转换功能"""
        # 应用灰度转换
        gray_image = convert_to_grayscale(self.test_image)
        
        # 检查输出图像尺寸（应该是2D）
        self.assertEqual(len(gray_image.shape), 2)
        
        # 验证图像大小保持不变
        self.assertEqual(gray_image.shape[0], self.test_image.shape[0])
        self.assertEqual(gray_image.shape[1], self.test_image.shape[1])
        
        # 如果源图像已经是灰度，应该返回相同图像
        gray_again = convert_to_grayscale(gray_image)
        self.assertTrue(np.array_equal(gray_image, gray_again))
    
    def test_apply_threshold(self):
        """测试阈值处理功能"""
        # 先转为灰度图
        gray_image = convert_to_grayscale(self.test_image)
        
        # 应用阈值处理
        threshold_image = apply_threshold(gray_image, threshold=128, max_value=255, threshold_type=cv2.THRESH_BINARY)
        
        # 验证结果图像只有0和255两个值
        unique_values = np.unique(threshold_image)
        self.assertEqual(len(unique_values), 2)
        self.assertTrue(0 in unique_values)
        self.assertTrue(255 in unique_values)
    
    def test_apply_adaptive_threshold(self):
        """测试自适应阈值处理功能"""
        # 先转为灰度图
        gray_image = convert_to_grayscale(self.test_image)
        
        # 应用自适应阈值处理
        threshold_image = apply_adaptive_threshold(gray_image, max_value=255, block_size=11, c=2)
        
        # 验证结果图像只有0和255两个值
        unique_values = np.unique(threshold_image)
        self.assertEqual(len(unique_values), 2)
        self.assertTrue(0 in unique_values)
        self.assertTrue(255 in unique_values)

if __name__ == "__main__":
    unittest.main() 