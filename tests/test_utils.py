"""
测试辅助工具 - 提供测试过程中需要的通用功能
"""
import os
import tempfile
import shutil
import numpy as np
import cv2
from pathlib import Path

# 获取项目根目录路径
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试资源目录
TEST_RESOURCES_DIR = PROJECT_ROOT / 'tests' / 'resources'

def ensure_test_resources_dir():
    """确保测试资源目录存在"""
    if not TEST_RESOURCES_DIR.exists():
        TEST_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

def get_temp_dir():
    """获取临时目录
    
    Returns:
        Path: 临时目录路径
    """
    return Path(tempfile.mkdtemp())

def create_test_image(width=100, height=100, channels=3):
    """创建用于测试的图像
    
    Args:
        width: 图像宽度
        height: 图像高度
        channels: 通道数（1=灰度图，3=RGB图）
    
    Returns:
        numpy.ndarray: 生成的图像数据
    """
    if channels == 1:
        # 创建灰度图
        img = np.zeros((height, width), dtype=np.uint8)
        # 添加一些图案以便于识别（对角线）
        for i in range(min(width, height)):
            img[i, i] = 255
    else:
        # 创建彩色图
        img = np.zeros((height, width, channels), dtype=np.uint8)
        # 添加一些颜色（RGB对角线）
        for i in range(min(width, height)):
            if channels >= 3:
                img[i, i, 0] = 255  # 红色对角线
                img[i, i//2, 1] = 255  # 绿色半对角线
                img[i//2, i, 2] = 255  # 蓝色半对角线
    
    return img

def save_test_image(img, filename):
    """保存测试图像到文件
    
    Args:
        img: 图像数据（numpy.ndarray）
        filename: 文件名（不含路径）
    
    Returns:
        Path: 保存的文件路径
    """
    ensure_test_resources_dir()
    filepath = TEST_RESOURCES_DIR / filename
    cv2.imwrite(str(filepath), img)
    return filepath

def create_and_save_test_image(filename, width=100, height=100, channels=3):
    """创建并保存测试图像
    
    Args:
        filename: 文件名（不含路径）
        width: 图像宽度
        height: 图像高度
        channels: 通道数（1=灰度图，3=RGB图）
    
    Returns:
        tuple: (图像数据, 文件路径)
    """
    img = create_test_image(width, height, channels)
    filepath = save_test_image(img, filename)
    return img, filepath

def cleanup_temp_dir(temp_dir):
    """清理临时目录
    
    Args:
        temp_dir: 临时目录路径
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def get_sample_image_path():
    """获取示例图像路径（如果不存在则创建）
    
    Returns:
        Path: 示例图像路径
    """
    ensure_test_resources_dir()
    sample_path = TEST_RESOURCES_DIR / 'sample.jpg'
    
    if not sample_path.exists():
        img = create_test_image(200, 200, 3)
        cv2.imwrite(str(sample_path), img)
    
    return sample_path

def images_equal(img1, img2):
    """比较两个图像是否相同
    
    Args:
        img1: 第一个图像（numpy.ndarray）
        img2: 第二个图像（numpy.ndarray）
    
    Returns:
        bool: 图像是否相同
    """
    if img1.shape != img2.shape:
        return False
    
 