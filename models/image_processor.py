"""
图像处理工具类
提供各种图像处理算法的实现
"""
import cv2
import numpy as np
from typing import Tuple, Optional, Union

class ImageProcessor:
    """图像处理工具类，提供各种图像处理算法的实现"""
    
    @staticmethod
    def resize(image: np.ndarray, size: Tuple[int, int], 
              interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
        """调整图像大小
        
        Args:
            image: 输入图像
            size: 目标尺寸 (width, height)
            interpolation: 插值方法
            
        Returns:
            调整大小后的图像
        """
        return cv2.resize(image, size, interpolation=interpolation)
    
    @staticmethod
    def rotate(image: np.ndarray, angle: float, 
              center: Optional[Tuple[int, int]] = None,
              scale: float = 1.0) -> np.ndarray:
        """旋转图像
        
        Args:
            image: 输入图像
            angle: 旋转角度（度）
            center: 旋转中心点，默认为图像中心
            scale: 缩放比例
            
        Returns:
            旋转后的图像
        """
        if center is None:
            center = (image.shape[1] // 2, image.shape[0] // 2)
        
        matrix = cv2.getRotationMatrix2D(center, angle, scale)
        return cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
    
    @staticmethod
    def flip(image: np.ndarray, flip_code: int) -> np.ndarray:
        """翻转图像
        
        Args:
            image: 输入图像
            flip_code: 翻转方式
                0: 垂直翻转
                1: 水平翻转
                -1: 同时水平和垂直翻转
                
        Returns:
            翻转后的图像
        """
        return cv2.flip(image, flip_code)
    
    @staticmethod
    def adjust_brightness(image: np.ndarray, value: float) -> np.ndarray:
        """调整图像亮度
        
        Args:
            image: 输入图像
            value: 亮度调整值，范围[-255, 255]
            
        Returns:
            调整后的图像
        """
        return cv2.add(image, value)
    
    @staticmethod
    def adjust_contrast(image: np.ndarray, value: float) -> np.ndarray:
        """调整图像对比度
        
        Args:
            image: 输入图像
            value: 对比度调整值，范围[0, 3]
            
        Returns:
            调整后的图像
        """
        return cv2.convertScaleAbs(image, alpha=value, beta=0)
    
    @staticmethod
    def adjust_saturation(image: np.ndarray, value: float) -> np.ndarray:
        """调整图像饱和度
        
        Args:
            image: 输入图像
            value: 饱和度调整值，范围[0, 3]
            
        Returns:
            调整后的图像
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], value)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def apply_filter(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """应用卷积滤波器
        
        Args:
            image: 输入图像
            kernel: 卷积核
            
        Returns:
            滤波后的图像
        """
        return cv2.filter2D(image, -1, kernel)
    
    @staticmethod
    def gaussian_blur(image: np.ndarray, kernel_size: Tuple[int, int], 
                     sigma_x: float = 0) -> np.ndarray:
        """高斯模糊
        
        Args:
            image: 输入图像
            kernel_size: 核大小 (width, height)
            sigma_x: X方向的标准差
            
        Returns:
            模糊后的图像
        """
        return cv2.GaussianBlur(image, kernel_size, sigma_x)
    
    @staticmethod
    def median_blur(image: np.ndarray, kernel_size: int) -> np.ndarray:
        """中值滤波
        
        Args:
            image: 输入图像
            kernel_size: 核大小
            
        Returns:
            滤波后的图像
        """
        return cv2.medianBlur(image, kernel_size)
    
    @staticmethod
    def bilateral_filter(image: np.ndarray, d: int, sigma_color: float, 
                        sigma_space: float) -> np.ndarray:
        """双边滤波
        
        Args:
            image: 输入图像
            d: 像素邻域直径
            sigma_color: 颜色空间标准差
            sigma_space: 坐标空间标准差
            
        Returns:
            滤波后的图像
        """
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    
    @staticmethod
    def threshold(image: np.ndarray, thresh: float, maxval: float, 
                 type: int) -> np.ndarray:
        """图像阈值处理
        
        Args:
            image: 输入图像
            thresh: 阈值
            maxval: 最大值
            type: 阈值类型
            
        Returns:
            处理后的图像
        """
        return cv2.threshold(image, thresh, maxval, type)[1]
    
    @staticmethod
    def adaptive_threshold(image: np.ndarray, maxval: float, 
                          adaptive_method: int, threshold_type: int,
                          block_size: int, C: float) -> np.ndarray:
        """自适应阈值处理
        
        Args:
            image: 输入图像
            maxval: 最大值
            adaptive_method: 自适应方法
            threshold_type: 阈值类型
            block_size: 邻域大小
            C: 常数
            
        Returns:
            处理后的图像
        """
        return cv2.adaptiveThreshold(image, maxval, adaptive_method,
                                   threshold_type, block_size, C)
    
    @staticmethod
    def canny(image: np.ndarray, threshold1: float, threshold2: float,
             aperture_size: int = 3, L2gradient: bool = False) -> np.ndarray:
        """Canny边缘检测
        
        Args:
            image: 输入图像
            threshold1: 第一个阈值
            threshold2: 第二个阈值
            aperture_size: Sobel算子大小
            L2gradient: 是否使用L2范数
            
        Returns:
            边缘检测结果
        """
        return cv2.Canny(image, threshold1, threshold2,
                        apertureSize=aperture_size, L2gradient=L2gradient)
    
    @staticmethod
    def convert_color(image: np.ndarray, code: int) -> np.ndarray:
        """颜色空间转换
        
        Args:
            image: 输入图像
            code: 转换代码
            
        Returns:
            转换后的图像
        """
        return cv2.cvtColor(image, code) 