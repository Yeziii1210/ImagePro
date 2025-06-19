"""
图像控制器模块

1. 图像处理操作控制
   - 亮度/对比度调整
   - 高斯模糊
   - 中值滤波
   - 双边滤波
   - 灰度转换
   - 阈值处理
   - 自适应阈值处理
   - 图像旋转
   - 图像锐化
   - 图像直方图
   - 图像曝光调整

2. 设计模式
   - 采用闭包(Closure)模式封装图像处理操作
   - 使用策略模式实现不同处理算法的切换
   - 遵循单一职责原则，专注于控制逻辑

3. 代码组织
   - 将具体处理逻辑委托给utils模块
   - 通过Model-View-Controller架构与模型和视图交互
   - 提供统一的接口进行图像处理操作

4. 扩展性
   - 易于添加新的图像处理功能
   - 支持自定义处理算法
   - 便于维护和测试

"""
from utils.image_utils import (
    adjust_brightness_contrast,
    apply_gaussian_blur,
    apply_median_blur,
    apply_bilateral_filter,
    convert_to_grayscale,
    apply_threshold,
    apply_adaptive_threshold,
    rotate_image,
    flip_image,
    crop_image,
    apply_laplacian_sharpen,
    apply_usm_sharpen,
    apply_custom_sharpen,
    calculate_histogram,
    apply_histogram_equalization,
    adjust_exposure,
    adjust_highlights,
    adjust_shadows,
    adjust_local_exposure,
    auto_contrast_enhancement,
    auto_color_correction,
    auto_white_balance,
    auto_image_enhance
)

class ImageController:
    """图像控制器类，负责图像处理操作"""
    
    def __init__(self, image_model):
        """初始化控制器
        
        Args:
            image_model: 图像模型实例
        """
        self.image_model = image_model
    
    def adjust_brightness_contrast(self, brightness, contrast):
        """调整亮度和对比度
        
        Args:
            brightness: 亮度调整值
            contrast: 对比度调整值
        """

        #将具体的图像处理操作封装在一个函数中，保持了代码的模块化和可维护性，便于统一处理图像操作
        def operation(image):
            return adjust_brightness_contrast(image, brightness, contrast)
        
        return self.image_model.apply_operation(operation)
    
    def apply_gaussian_blur(self, kernel_size, sigma):
        """应用高斯模糊
        
        Args:
            kernel_size: 核大小
            sigma: 高斯核标准差
        """
        def operation(image):
            return apply_gaussian_blur(image, kernel_size, sigma)
        
        return self.image_model.apply_operation(operation)
    
    def apply_median_blur(self, kernel_size):
        """应用中值滤波
        
        Args:
            kernel_size: 核大小
        """
        def operation(image):
            return apply_median_blur(image, kernel_size)
        
        return self.image_model.apply_operation(operation)
    
    def apply_bilateral_filter(self, d, sigma_color, sigma_space):
        """应用双边滤波
        
        Args:
            d: 像素邻域直径
            sigma_color: 颜色空间标准差
            sigma_space: 坐标空间标准差
        """
        def operation(image):
            return apply_bilateral_filter(image, d, sigma_color, sigma_space)
        
        return self.image_model.apply_operation(operation)
    
    def convert_to_grayscale(self):
        """转换为灰度图"""
        def operation(image):
            return convert_to_grayscale(image)
        
        return self.image_model.apply_operation(operation)
    
    def apply_threshold(self, threshold, max_value, threshold_type):
        """应用阈值处理
        
        Args:
            threshold: 阈值
            max_value: 最大值
            threshold_type: 阈值类型
        """
        def operation(image):
            return apply_threshold(image, threshold, max_value, threshold_type)
        
        return self.image_model.apply_operation(operation)
    
    def apply_adaptive_threshold(self, max_value, block_size, c):
        """应用自适应阈值处理
        
        Args:
            max_value: 最大值
            block_size: 邻域大小
            c: 常数
        """
        def operation(image):
            return apply_adaptive_threshold(image, max_value, block_size, c)
        
        return self.image_model.apply_operation(operation)
    
    def rotate_image(self, angle, scale=1.0, expand=False):
        """旋转图像
        
        Args:
            angle: 旋转角度（度），正值表示逆时针旋转
            scale: 缩放比例，默认为1.0
            expand: 是否扩展图像以包含整个旋转后的图像，默认为False
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return rotate_image(image, angle, center=None, scale=scale, expand=expand)
        
        return self.image_model.apply_operation(operation)
    
    def flip_image(self, flip_code):
        """翻转图像
        
        Args:
            flip_code: 翻转方式
                0: 垂直翻转
                1: 水平翻转
                -1: 同时水平和垂直翻转
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return flip_image(image, flip_code)
        
        return self.image_model.apply_operation(operation)
    
    def crop_image(self, x, y, width, height):
        """裁剪图像
        
        Args:
            x: 裁剪区域左上角的x坐标
            y: 裁剪区域左上角的y坐标
            width: 裁剪区域的宽度
            height: 裁剪区域的高度
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return crop_image(image, x, y, width, height)
        
        return self.image_model.apply_operation(operation)
    
    def preview_brightness_contrast(self, brightness, contrast):
        """预览亮度和对比度调整（不添加历史记录）
        
        Args:
            brightness: 亮度调整值
            contrast: 对比度调整值
        """
        def operation(image):
            return adjust_brightness_contrast(image, brightness, contrast)
        
        return self.image_model.preview_operation(operation)
    
    def preview_crop_image(self, x, y, width, height):
        """预览裁剪效果（不添加历史记录）
        
        Args:
            x: 裁剪区域左上角的x坐标
            y: 裁剪区域左上角的y坐标
            width: 裁剪区域的宽度
            height: 裁剪区域的高度
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return crop_image(image, x, y, width, height)
        
        return self.image_model.preview_operation(operation)
    
    def preview_rotate_image(self, angle, scale=1.0, expand=False):
        """预览图像旋转效果（不添加历史记录）
        
        Args:
            angle: 旋转角度（度），正值表示逆时针旋转
            scale: 缩放比例，默认为1.0
            expand: 是否扩展图像以包含整个旋转后的图像，默认为False
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return rotate_image(image, angle, center=None, scale=scale, expand=expand)
        
        return self.image_model.preview_operation(operation)
    
    def preview_flip_image(self, flip_code):
        """预览翻转图像效果
        
        Args:
            flip_code: 翻转方式
                     1: 水平翻转（左右翻转）
                     0: 垂直翻转（上下翻转）
                     -1: 同时水平垂直翻转（180度旋转）
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return flip_image(image, flip_code)
        
        return self.image_model.preview_operation(operation)
    
    def apply_last_preview(self):
        """应用最后一次预览"""
        return self.image_model.apply_last_preview()
    
    def apply_laplacian_sharpen(self, kernel_size=3, strength=1.0):
        """应用拉普拉斯锐化
        
        Args:
            kernel_size: 拉普拉斯核大小，必须是奇数
            strength: 锐化强度，范围[0.0, 5.0]
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_laplacian_sharpen(image, kernel_size, strength)
        
        return self.image_model.apply_operation(operation)
    
    def apply_usm_sharpen(self, radius=5, amount=1.0, threshold=0):
        """应用USM锐化(Unsharp Masking)
        
        Args:
            radius: 高斯模糊半径，控制锐化的细节范围
            amount: 锐化强度，范围[0.0, 5.0]
            threshold: 阈值，只有差异大于阈值的像素才会被锐化
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_usm_sharpen(image, radius, amount, threshold)
        
        return self.image_model.apply_operation(operation)
    
    def apply_custom_sharpen(self, kernel, strength=1.0):
        """应用自定义锐化核
        
        Args:
            kernel: 自定义锐化核，必须是numpy数组
            strength: 锐化强度，范围[0.0, 5.0]
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_custom_sharpen(image, kernel, strength)
        
        return self.image_model.apply_operation(operation)
    
    def preview_laplacian_sharpen(self, kernel_size=3, strength=1.0):
        """预览拉普拉斯锐化效果
        
        Args:
            kernel_size: 拉普拉斯核大小，必须是奇数
            strength: 锐化强度，范围[0.0, 5.0]
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_laplacian_sharpen(image, kernel_size, strength)
        
        return self.image_model.preview_operation(operation)
    
    def preview_usm_sharpen(self, radius=5, amount=1.0, threshold=0):
        """预览USM锐化效果
        
        Args:
            radius: 高斯模糊半径，控制锐化的细节范围
            amount: 锐化强度，范围[0.0, 5.0]
            threshold: 阈值，只有差异大于阈值的像素才会被锐化
        
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_usm_sharpen(image, radius, amount, threshold)
        
        return self.image_model.preview_operation(operation)
    
    def calculate_histogram(self, channel=None, mask=None, bins=256, range_values=(0, 256)):
        """计算当前图像的直方图
        
        Args:
            channel: 要计算的通道，None表示所有通道，0表示蓝色通道，1表示绿色通道，2表示红色通道
            mask: 掩码图像，可选
            bins: 直方图柱数
            range_values: 直方图范围
            
        Returns:
            直方图数据
        """
        if not self.image_model.has_image():
            return None
            
        return calculate_histogram(
            self.image_model.current_image,
            channel=channel,
            mask=mask,
            bins=bins,
            range_values=range_values
        )
        
    def apply_histogram_equalization(self, per_channel=False):
        """应用直方图均衡化
        
        Args:
            per_channel: 是否对彩色图像的每个通道分别进行均衡化
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_histogram_equalization(image, per_channel=per_channel)
            
        return self.image_model.apply_operation(operation)
        
    def preview_histogram_equalization(self, per_channel=False):
        """预览直方图均衡化效果
        
        Args:
            per_channel: 是否对彩色图像的每个通道分别进行均衡化
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return apply_histogram_equalization(image, per_channel=per_channel)
            
        return self.image_model.preview_operation(operation)
        
    def adjust_exposure(self, exposure=0.0):
        """调整图像曝光度
        
        Args:
            exposure: 曝光度调整值，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_exposure(image, exposure=exposure)
            
        return self.image_model.apply_operation(operation)
        
    def preview_exposure(self, exposure=0.0):
        """预览曝光度调整效果
        
        Args:
            exposure: 曝光度调整值，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_exposure(image, exposure=exposure)
            
        return self.image_model.preview_operation(operation)
        
    def adjust_highlights(self, highlights=0.0):
        """调整图像高光部分
        
        Args:
            highlights: 高光调整值，正值增强高光，负值减弱高光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_highlights(image, highlights=highlights)
            
        return self.image_model.apply_operation(operation)
        
    def preview_highlights(self, highlights=0.0):
        """预览高光调整效果
        
        Args:
            highlights: 高光调整值，正值增强高光，负值减弱高光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_highlights(image, highlights=highlights)
            
        return self.image_model.preview_operation(operation)
        
    def adjust_shadows(self, shadows=0.0):
        """调整图像阴影部分
        
        Args:
            shadows: 阴影调整值，正值增强阴影细节，负值减弱阴影，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_shadows(image, shadows=shadows)
            
        return self.image_model.apply_operation(operation)
        
    def preview_shadows(self, shadows=0.0):
        """预览阴影调整效果
        
        Args:
            shadows: 阴影调整值，正值增强阴影细节，负值减弱阴影，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_shadows(image, shadows=shadows)
            
        return self.image_model.preview_operation(operation)
        
    def adjust_local_exposure(self, center_x, center_y, radius, strength=0.5):
        """局部曝光调整，调整以指定中心点为中心的圆形区域的曝光
        
        Args:
            center_x: 中心点X坐标
            center_y: 中心点Y坐标
            radius: 影响半径
            strength: 调整强度，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_local_exposure(image, center_x, center_y, radius, strength=strength)
            
        return self.image_model.apply_operation(operation)
        
    def preview_local_exposure(self, center_x, center_y, radius, strength=0.5):
        """预览局部曝光调整效果
        
        Args:
            center_x: 中心点X坐标
            center_y: 中心点Y坐标
            radius: 影响半径
            strength: 调整强度，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return adjust_local_exposure(image, center_x, center_y, radius, strength=strength)
            
        return self.image_model.preview_operation(operation)
        
    def apply_auto_contrast(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        """应用自动对比度增强
        
        Args:
            clip_limit: 对比度限制，防止过度增强噪声，范围[1.0, 5.0]
            tile_grid_size: 分块大小，用于局部均衡化
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_contrast_enhancement(image, clip_limit=clip_limit, tile_grid_size=tile_grid_size)
            
        return self.image_model.apply_operation(operation)
        
    def preview_auto_contrast(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        """预览自动对比度增强效果
        
        Args:
            clip_limit: 对比度限制，防止过度增强噪声，范围[1.0, 5.0]
            tile_grid_size: 分块大小，用于局部均衡化
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_contrast_enhancement(image, clip_limit=clip_limit, tile_grid_size=tile_grid_size)
            
        return self.image_model.preview_operation(operation)
        
    def apply_auto_color(self, saturation_scale=1.3, vibrance_scale=1.2):
        """应用自动色彩校正
        
        Args:
            saturation_scale: 饱和度放大因子，范围[1.0, 2.0]，大于1增强饱和度
            vibrance_scale: 鲜艳度放大因子，范围[1.0, 2.0]，仅增强低饱和区域
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_color_correction(image, saturation_scale=saturation_scale, vibrance_scale=vibrance_scale)
            
        return self.image_model.apply_operation(operation)
        
    def preview_auto_color(self, saturation_scale=1.3, vibrance_scale=1.2):
        """预览自动色彩校正效果
        
        Args:
            saturation_scale: 饱和度放大因子，范围[1.0, 2.0]，大于1增强饱和度
            vibrance_scale: 鲜艳度放大因子，范围[1.0, 2.0]，仅增强低饱和区域
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_color_correction(image, saturation_scale=saturation_scale, vibrance_scale=vibrance_scale)
            
        return self.image_model.preview_operation(operation)
        
    def apply_auto_white_balance(self, method='adaptive'):
        """应用自动白平衡
        
        Args:
            method: 白平衡方法，可选值：'gray_world', 'perfect_reflector', 'adaptive'
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_white_balance(image, method=method)
            
        return self.image_model.apply_operation(operation)
        
    def preview_auto_white_balance(self, method='adaptive'):
        """预览自动白平衡效果
        
        Args:
            method: 白平衡方法，可选值：'gray_world', 'perfect_reflector', 'adaptive'
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_white_balance(image, method=method)
            
        return self.image_model.preview_operation(operation)
        
    def apply_auto_all(self, contrast=True, color=True, white_balance=True):
        """应用一键优化
        
        Args:
            contrast: 是否应用对比度增强
            color: 是否应用色彩校正
            white_balance: 是否应用白平衡调整
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_image_enhance(image, contrast=contrast, color=color, white_balance=white_balance)
            
        return self.image_model.apply_operation(operation)
        
    def preview_auto_all(self, contrast=True, color=True, white_balance=True):
        """预览一键优化效果
        
        Args:
            contrast: 是否应用对比度增强
            color: 是否应用色彩校正
            white_balance: 是否应用白平衡调整
            
        Returns:
            bool: 操作是否成功
        """
        def operation(image):
            return auto_image_enhance(image, contrast=contrast, color=color, white_balance=white_balance)
            
        return self.image_model.preview_operation(operation) 