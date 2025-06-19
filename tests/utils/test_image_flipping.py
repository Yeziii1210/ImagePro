"""
测试图像翻转功能
"""
import os
import sys
import unittest
import numpy as np
import cv2
from pathlib import Path
import shutil

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.image_utils import flip_image

class TestImageFlipping(unittest.TestCase):
    """测试图像翻转功能"""
    
    def setUp(self):
        """测试前设置"""
        # 创建测试输出目录
        self.output_path = Path('./tests/output/flipping')
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建一个测试图像
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 在左上角画一个红色矩形
        self.test_image[10:30, 10:30, 0] = 255  # 红色通道
    
    def tearDown(self):
        """测试后清理"""
        # 清理输出目录
        if self.output_path.exists():
            shutil.rmtree(str(self.output_path))
    
    def test_horizontal_flip(self):
        """测试水平翻转"""
        # 水平翻转图像
        flipped = flip_image(self.test_image, 1)
        
        # 保存原始图像和翻转后的图像，便于手动检查
        cv2.imwrite(str(self.output_path / "original.png"), cv2.cvtColor(self.test_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.output_path / "flipped_horizontal.png"), cv2.cvtColor(flipped, cv2.COLOR_RGB2BGR))
        
        # 验证翻转后的尺寸不变
        self.assertEqual(flipped.shape, self.test_image.shape)
        
        # 验证水平翻转：左上角的红色矩形应该出现在右上角
        # 原始图像左上角区域
        original_top_left = self.test_image[10:30, 10:30, 0]
        # 翻转后图像右上角区域
        flipped_top_right = flipped[10:30, 70:90, 0]
        
        # 验证颜色值
        self.assertTrue(np.all(original_top_left > 0))
        self.assertTrue(np.all(flipped_top_right > 0))
    
    def test_vertical_flip(self):
        """测试垂直翻转"""
        # 垂直翻转图像
        flipped = flip_image(self.test_image, 0)
        
        # 保存翻转后的图像
        cv2.imwrite(str(self.output_path / "flipped_vertical.png"), cv2.cvtColor(flipped, cv2.COLOR_RGB2BGR))
        
        # 验证翻转后的尺寸不变
        self.assertEqual(flipped.shape, self.test_image.shape)
        
        # 验证垂直翻转：左上角的红色矩形应该出现在左下角
        # 原始图像左上角区域
        original_top_left = self.test_image[10:30, 10:30, 0]
        # 翻转后图像左下角区域
        flipped_bottom_left = flipped[70:90, 10:30, 0]
        
        # 验证颜色值
        self.assertTrue(np.all(original_top_left > 0))
        self.assertTrue(np.all(flipped_bottom_left > 0))
    
    def test_both_flip(self):
        """测试同时水平和垂直翻转"""
        # 同时水平和垂直翻转图像
        flipped = flip_image(self.test_image, -1)
        
        # 保存翻转后的图像
        cv2.imwrite(str(self.output_path / "flipped_both.png"), cv2.cvtColor(flipped, cv2.COLOR_RGB2BGR))
        
        # 验证翻转后的尺寸不变
        self.assertEqual(flipped.shape, self.test_image.shape)
        
        # 验证同时翻转：左上角的红色矩形应该出现在右下角
        # 原始图像左上角区域
        original_top_left = self.test_image[10:30, 10:30, 0]
        # 翻转后图像右下角区域
        flipped_bottom_right = flipped[70:90, 70:90, 0]
        
        # 验证颜色值
        self.assertTrue(np.all(original_top_left > 0))
        self.assertTrue(np.all(flipped_bottom_right > 0))

if __name__ == "__main__":
    unittest.main() 