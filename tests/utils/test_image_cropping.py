"""
测试图像裁剪功能
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

from utils.image_utils import crop_image

class TestImageCropping(unittest.TestCase):
    """测试图像裁剪功能"""
    
    def setUp(self):
        """测试前设置"""
        # 创建测试输出目录
        self.output_path = Path('./tests/output/cropping')
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建一个测试图像
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 在中间画一个红色矩形
        self.test_image[40:60, 20:80, 0] = 255  # 红色通道
    
    def tearDown(self):
        """测试后清理"""
        # 清理输出目录
        if self.output_path.exists():
            shutil.rmtree(str(self.output_path))
    
    def test_crop_center(self):
        """测试裁剪中心区域"""
        # 裁剪图像中心区域
        cropped = crop_image(self.test_image, 25, 25, 50, 50)
        
        # 保存原始图像和裁剪后的图像，便于手动检查
        cv2.imwrite(str(self.output_path / "original.png"), cv2.cvtColor(self.test_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.output_path / "cropped_center.png"), cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
        
        # 验证裁剪后的尺寸
        self.assertEqual(cropped.shape, (50, 50, 3))
        
        # 验证裁剪后的图像包含了原始图像中的红色矩形部分
        self.assertTrue(np.any(cropped[:, :, 0] > 128))
    
    def test_crop_edge(self):
        """测试裁剪边缘区域"""
        # 裁剪图像边缘
        cropped = crop_image(self.test_image, 80, 80, 30, 30)
        
        # 保存裁剪后的图像
        cv2.imwrite(str(self.output_path / "cropped_edge.png"), cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
        
        # 验证裁剪后的尺寸
        # 由于裁剪区域超出图像边界，应该被调整为有效范围
        self.assertEqual(cropped.shape, (20, 20, 3))
    
    def test_crop_outside_bounds(self):
        """测试裁剪超出边界的情况"""
        # 尝试裁剪完全超出图像边界的区域
        cropped = crop_image(self.test_image, 150, 150, 50, 50)
        
        # 保存裁剪后的图像（如果不是空图像）
        if cropped.size > 0:
            cv2.imwrite(str(self.output_path / "cropped_outside.png"), cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
        else:
            # 只是写一个空图像文件，标记测试通过
            empty = np.zeros((1, 1, 3), dtype=np.uint8)
            cv2.imwrite(str(self.output_path / "cropped_outside.png"), empty)
        
        # 验证裁剪结果
        # 应该得到一个空图像或者很小的图像
        self.assertTrue(cropped.size == 0 or (cropped.shape[0] == 0 or cropped.shape[1] == 0))
    
    def test_crop_with_negative_coords(self):
        """测试使用负坐标裁剪"""
        # 尝试使用负坐标裁剪
        cropped = crop_image(self.test_image, -10, -10, 50, 50)
        
        # 保存裁剪后的图像
        cv2.imwrite(str(self.output_path / "cropped_negative.png"), cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
        
        # 验证裁剪后的尺寸
        # 负坐标应该被调整为0
        self.assertEqual(cropped.shape, (50, 50, 3))
        
        # 验证裁剪后的图像内容正确
        # 应该是图像左上角的内容
        self.assertEqual(cropped[0, 0, 0], self.test_image[0, 0, 0])

if __name__ == "__main__":
    unittest.main() 