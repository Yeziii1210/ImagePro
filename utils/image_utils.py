"""
图像处理工具函数
"""
import cv2
import numpy as np

def adjust_brightness_contrast(image, brightness=0, contrast=1.0):
    """调整亮度和对比度
    
    Args:
        image: 输入图像
        brightness: 亮度调整值，范围[-100, 100]
        contrast: 对比度调整值，范围[0.0, 3.0]
    
    Returns:
        处理后的图像
    """
    # 确保输入是numpy数组
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 调整亮度和对比度
    adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    return adjusted

def apply_gaussian_blur(image, kernel_size=3, sigma=0):
    """应用高斯模糊
    
    Args:
        image: 输入图像
        kernel_size: 核大小，必须是奇数
        sigma: 高斯核标准差
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保kernel_size是奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

def apply_median_blur(image, kernel_size=3):
    """应用中值滤波
    
    Args:
        image: 输入图像
        kernel_size: 核大小，必须是奇数
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保kernel_size是奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    return cv2.medianBlur(image, kernel_size)

def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """应用双边滤波
    
    Args:
        image: 输入图像
        d: 像素邻域直径
        sigma_color: 颜色空间标准差
        sigma_space: 坐标空间标准差
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

def convert_to_grayscale(image):
    """转换为灰度图
    
    Args:
        image: 输入图像
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def apply_threshold(image, threshold=127, max_value=255, threshold_type=cv2.THRESH_BINARY):
    """应用阈值处理
    
    Args:
        image: 输入图像
        threshold: 阈值
        max_value: 最大值
        threshold_type: 阈值类型
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保图像是灰度图
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    _, result = cv2.threshold(image, threshold, max_value, threshold_type)
    return result

def apply_adaptive_threshold(image, max_value=255, block_size=11, c=2):
    """应用自适应阈值处理
    
    Args:
        image: 输入图像
        max_value: 最大值
        block_size: 邻域大小
        c: 常数
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保图像是灰度图
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 确保block_size是奇数
    if block_size % 2 == 0:
        block_size += 1
    
    return cv2.adaptiveThreshold(image, max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, block_size, c)

def rotate_image(image, angle, center=None, scale=1.0, expand=False):
    """旋转图像
    
    Args:
        image: 输入图像
        angle: 旋转角度（度），正值表示逆时针旋转
        center: 旋转中心，默认为图像中心
        scale: 缩放比例
        expand: 是否扩展图像以包含整个旋转后的图像
    
    Returns:
        旋转后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 获取图像尺寸
    height, width = image.shape[:2]
    
    # 如果没有指定旋转中心，默认为图像中心
    if center is None:
        center = (width // 2, height // 2)
    
    if expand:
        # 计算旋转后图像的新尺寸
        angle_rad = np.abs(np.radians(angle))
        new_width = int(height * np.abs(np.sin(angle_rad)) + width * np.abs(np.cos(angle_rad)))
        new_height = int(height * np.abs(np.cos(angle_rad)) + width * np.abs(np.sin(angle_rad)))
        
        # 调整旋转中心和输出图像大小
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        rotation_matrix[0, 2] += (new_width - width) / 2
        rotation_matrix[1, 2] += (new_height - height) / 2
        
        # 执行仿射变换
        rotated_image = cv2.warpAffine(image, rotation_matrix, (new_width, new_height))
    else:
        # 计算旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        
        # 执行仿射变换
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    
    return rotated_image

def flip_image(image, flip_code):
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
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    return cv2.flip(image, flip_code)

def crop_image(image, x, y, width, height):
    """裁剪图像
    
    Args:
        image: 输入图像
        x: 裁剪区域左上角的x坐标
        y: 裁剪区域左上角的y坐标
        width: 裁剪区域的宽度
        height: 裁剪区域的高度
    
    Returns:
        裁剪后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保坐标在有效范围内
    height_img, width_img = image.shape[:2]
    
    # 检查裁剪区域是否完全在图像外部
    if x >= width_img or y >= height_img or (x + width) <= 0 or (y + height) <= 0:
        # 返回空图像
        return np.array([], dtype=image.dtype).reshape(0, 0, image.shape[2] if len(image.shape) > 2 else 1)
    
    # 调整坐标确保在图像内部
    x = max(0, min(x, width_img - 1))
    y = max(0, min(y, height_img - 1))
    width = min(width, width_img - x)
    height = min(height, height_img - y)
    
    return image[y:y+height, x:x+width].copy()

def apply_laplacian_sharpen(image, kernel_size=3, strength=1.0):
    """应用拉普拉斯锐化
    
    Args:
        image: 输入图像
        kernel_size: 拉普拉斯核大小，必须是奇数
        strength: 锐化强度，范围[0.0, 5.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保kernel_size是奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # 转换为灰度图像计算拉普拉斯
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 应用拉普拉斯算子
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size)
    
    # 将结果转换回适当的范围
    laplacian = cv2.convertScaleAbs(laplacian)
    
    # 如果输入是彩色图像，对每个通道应用锐化
    if len(image.shape) == 3:
        sharpened = image.copy()
        for i in range(3):
            sharpened[:,:,i] = cv2.addWeighted(image[:,:,i], 1.0, laplacian, strength, 0)
    else:
        sharpened = cv2.addWeighted(image, 1.0, laplacian, strength, 0)
    
    return sharpened

def apply_usm_sharpen(image, radius=5, amount=1.0, threshold=0):
    """应用USM锐化(Unsharp Masking)
    
    Args:
        image: 输入图像
        radius: 高斯模糊半径，控制锐化的细节范围
        amount: 锐化强度，范围[0.0, 5.0]
        threshold: 阈值，只有差异大于阈值的像素才会被锐化
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 确保半径是正数
    radius = max(1, radius)
    
    # 创建高斯模糊版本作为"模糊掩码"
    blurred = cv2.GaussianBlur(image, (radius*2+1, radius*2+1), 0)
    
    # 计算原图与模糊图的差异
    sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
    
    # 应用阈值
    if threshold > 0:
        # 计算原图和锐化图的差异
        diff = cv2.absdiff(sharpened, image)
        
        # 创建掩码，其中差异大于阈值的部分为1，否则为0
        mask = diff > threshold
        
        # 只应用差异大于阈值的部分
        result = image.copy()
        if len(image.shape) == 3:
            for i in range(3):
                result[:,:,i] = np.where(mask[:,:,i], sharpened[:,:,i], image[:,:,i])
        else:
            result = np.where(mask, sharpened, image)
        
        return result
    
    return sharpened

def apply_custom_sharpen(image, kernel, strength=1.0):
    """应用自定义锐化核
    
    Args:
        image: 输入图像
        kernel: 自定义锐化核，必须是numpy数组
        strength: 锐化强度，范围[0.0, 5.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    if not isinstance(kernel, np.ndarray):
        raise TypeError("锐化核必须是numpy数组")
    
    # 应用自定义滤波器
    filtered = cv2.filter2D(image, -1, kernel)
    
    # 混合原始图像和锐化结果
    sharpened = cv2.addWeighted(image, 1.0, filtered, strength, 0)
    
    return sharpened

def calculate_histogram(image, channel=None, mask=None, bins=256, range_values=(0, 256)):
    """计算图像直方图
    
    Args:
        image: 输入图像
        channel: 要计算的通道，None表示所有通道，0表示蓝色通道，1表示绿色通道，2表示红色通道
        mask: 掩码图像，可选
        bins: 直方图柱数
        range_values: 直方图范围
    
    Returns:
        直方图数据，如果是彩色图像则返回每个通道的直方图数据列表，灰度图像则返回单个直方图
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 检查图像类型
    is_color = len(image.shape) == 3 and image.shape[2] == 3
    
    # 灰度图像
    if not is_color:
        # 在mask上进行一次检查
        if mask is not None and not isinstance(mask, np.ndarray):
            mask = None
        
        hist = cv2.calcHist([image], [0], mask, [bins], range_values)
        return hist
    
    # 彩色图像
    if channel is not None:
        # 计算指定通道的直方图
        if channel < 0 or channel > 2:
            raise ValueError("通道索引必须是0、1或2")
        
        hist = cv2.calcHist([image], [channel], mask, [bins], range_values)
        return hist
    else:
        # 计算所有通道的直方图
        hist_b = cv2.calcHist([image], [0], mask, [bins], range_values)
        hist_g = cv2.calcHist([image], [1], mask, [bins], range_values)
        hist_r = cv2.calcHist([image], [2], mask, [bins], range_values)
        return [hist_b, hist_g, hist_r]

def apply_histogram_equalization(image, per_channel=False):
    """应用直方图均衡化
    
    Args:
        image: 输入图像
        per_channel: 是否对彩色图像的每个通道分别进行均衡化，默认False表示只均衡化亮度通道
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 灰度图像直接均衡化
    if len(image.shape) == 2 or image.shape[2] == 1:
        return cv2.equalizeHist(image)
    
    # 彩色图像
    if per_channel:
        # 分别对BGR三个通道进行均衡化
        result = np.zeros_like(image)
        for i in range(3):
            result[:,:,i] = cv2.equalizeHist(image[:,:,i])
        return result
    else:
        # 转换到LAB颜色空间，只均衡化亮度通道
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # 均衡化L通道
        l_eq = cv2.equalizeHist(l)
        
        # 合并通道
        lab_eq = cv2.merge([l_eq, a, b])
        
        # 转换回RGB空间
        result = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
        return result

def adjust_exposure(image, exposure=0.0):
    """调整图像曝光度
    
    Args:
        image: 输入图像
        exposure: 曝光度调整值，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 将曝光度转换为增益因子
    if exposure > 0:
        # 正曝光值，增加亮度但避免过度曝光
        gain = 1.0 + exposure
    else:
        # 负曝光值，降低亮度
        gain = 1.0 / (1.0 - exposure)
    
    # 应用曝光调整
    adjusted = cv2.convertScaleAbs(image, alpha=gain, beta=0)
    return adjusted

def adjust_highlights(image, highlights=0.0):
    """调整图像高光部分
    
    Args:
        image: 输入图像
        highlights: 高光调整值，正值增强高光，负值减弱高光，范围[-1.0, 1.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 复制原始图像
    result = image.copy()
    
    # 计算图像亮度
    if len(image.shape) == 3:
        # 彩色图像，转换为HSV后提取V通道
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        v = hsv[:,:,2]
    else:
        # 灰度图像，直接使用灰度值
        v = image.copy()
    
    # 创建高光区域掩码（亮度值高于阈值的区域）
    highlight_threshold = 180  # 0-255范围内，亮度高于此值的像素被视为高光
    highlight_mask = v > highlight_threshold
    
    # 根据参数调整高光区域
    if highlights > 0:
        # 增强高光，提高亮度
        if len(image.shape) == 3:
            for i in range(3):
                result[:,:,i][highlight_mask] = np.clip(
                    result[:,:,i][highlight_mask] * (1 + 0.5 * highlights), 
                    0, 
                    255
                ).astype(np.uint8)
        else:
            result[highlight_mask] = np.clip(
                result[highlight_mask] * (1 + 0.5 * highlights), 
                0, 
                255
            ).astype(np.uint8)
    else:
        # 减弱高光，降低亮度
        if len(image.shape) == 3:
            for i in range(3):
                result[:,:,i][highlight_mask] = np.clip(
                    result[:,:,i][highlight_mask] * (1 + highlights), 
                    0, 
                    255
                ).astype(np.uint8)
        else:
            result[highlight_mask] = np.clip(
                result[highlight_mask] * (1 + highlights), 
                0, 
                255
            ).astype(np.uint8)
    
    return result

def adjust_shadows(image, shadows=0.0):
    """调整图像阴影部分
    
    Args:
        image: 输入图像
        shadows: 阴影调整值，正值增强阴影细节，负值减弱阴影，范围[-1.0, 1.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 复制原始图像
    result = image.copy()
    
    # 计算图像亮度
    if len(image.shape) == 3:
        # 彩色图像，转换为HSV后提取V通道
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        v = hsv[:,:,2]
    else:
        # 灰度图像，直接使用灰度值
        v = image.copy()
    
    # 创建阴影区域掩码（亮度值低于阈值的区域）
    shadow_threshold = 80  # 0-255范围内，亮度低于此值的像素被视为阴影
    shadow_mask = v < shadow_threshold
    
    # 根据参数调整阴影区域
    if shadows > 0:
        # 增强阴影，提高亮度使细节更清晰
        gamma = 1 - shadows * 0.5  # gamma值小于1时增强暗部细节
        if len(image.shape) == 3:
            for i in range(3):
                temp = result[:,:,i][shadow_mask].astype(np.float32) / 255.0
                result[:,:,i][shadow_mask] = np.clip(
                    (temp ** gamma) * 255.0, 
                    0, 
                    255
                ).astype(np.uint8)
        else:
            temp = result[shadow_mask].astype(np.float32) / 255.0
            result[shadow_mask] = np.clip(
                (temp ** gamma) * 255.0, 
                0, 
                255
            ).astype(np.uint8)
    else:
        # 减弱阴影，降低亮度
        if len(image.shape) == 3:
            for i in range(3):
                result[:,:,i][shadow_mask] = np.clip(
                    result[:,:,i][shadow_mask] * (1 + shadows), 
                    0, 
                    255
                ).astype(np.uint8)
        else:
            result[shadow_mask] = np.clip(
                result[shadow_mask] * (1 + shadows), 
                0, 
                255
            ).astype(np.uint8)
    
    return result

def adjust_local_exposure(image, center_x, center_y, radius, strength=0.5):
    """局部曝光调整，调整以指定中心点为中心的圆形区域的曝光
    
    Args:
        image: 输入图像
        center_x: 中心点X坐标
        center_y: 中心点Y坐标
        radius: 影响半径
        strength: 调整强度，正值增加曝光，负值降低曝光，范围[-1.0, 1.0]
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 创建和图像大小相同的掩码
    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.float32)
    
    # 创建网格坐标
    y, x = np.ogrid[:height, :width]
    
    # 计算每个像素到中心点的距离
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # 创建衰减掩码，中心处值为1，距离越远值越小
    mask = np.maximum(0, 1 - dist_from_center / radius)
    
    # 确保mask是3D的，如果输入是彩色图像
    if len(image.shape) == 3:
        mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    
    # 调整曝光
    if strength > 0:
        # 提高曝光度
        gain = 1.0 + strength
        adjusted = cv2.convertScaleAbs(image, alpha=gain, beta=0)
    else:
        # 降低曝光度
        gain = 1.0 + strength  # strength为负值，所以这里是减小gain
        adjusted = cv2.convertScaleAbs(image, alpha=gain, beta=0)
    
    # 根据mask混合原始图像和调整后的图像
    return cv2.addWeighted(image, 1 - mask, adjusted, mask, 0)

def auto_contrast_enhancement(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """自动对比度增强，使用CLAHE（对比度受限的自适应直方图均衡化）算法
    
    Args:
        image: 输入图像
        clip_limit: 对比度限制，防止过度增强噪声，范围[1.0, 5.0]
        tile_grid_size: 分块大小，用于局部均衡化
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 复制原始图像
    result = image.copy()
    
    # 创建CLAHE对象
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    if len(image.shape) == 2:
        # 灰度图像直接处理
        result = clahe.apply(image)
    else:
        # 彩色图像转换到LAB颜色空间
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # 只对亮度通道应用CLAHE
        l = clahe.apply(l)
        
        # 合并通道
        lab = cv2.merge([l, a, b])
        
        # 转换回RGB
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    return result

def auto_color_correction(image, saturation_scale=1.3, vibrance_scale=1.2):
    """自动色彩校正，增强图像饱和度和鲜艳度
    
    Args:
        image: 输入图像
        saturation_scale: 饱和度放大因子，范围[1.0, 2.0]，大于1增强饱和度
        vibrance_scale: 鲜艳度放大因子，范围[1.0, 2.0]，仅增强低饱和区域
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 仅处理彩色图像
    if len(image.shape) != 3 or image.shape[2] != 3:
        return image
    
    # 转换到HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    
    # 全局饱和度提升
    s = np.clip(s.astype(np.float32) * saturation_scale, 0, 255).astype(np.uint8)
    
    # 智能鲜艳度提升（仅增强低饱和区域，保留高饱和区域）
    # 饱和度越低，增强效果越明显
    if vibrance_scale > 1.0:
        # 计算饱和度反比例
        s_inv = 255 - s
        
        # 计算增强系数，低饱和区域增强更多
        vibrance_mask = s_inv / 255.0
        
        # 应用鲜艳度增强
        s_vibrance = s.astype(np.float32) * (1.0 + (vibrance_scale - 1.0) * vibrance_mask)
        s = np.clip(s_vibrance, 0, 255).astype(np.uint8)
    
    # 合并通道
    hsv_corrected = cv2.merge([h, s, v])
    
    # 转换回RGB
    result = cv2.cvtColor(hsv_corrected, cv2.COLOR_HSV2RGB)
    
    return result

def auto_white_balance(image, method='gray_world'):
    """自动白平衡处理
    
    Args:
        image: 输入图像
        method: 白平衡方法，可选值:
            'gray_world': 灰色世界假设
            'perfect_reflector': 完美反射假设
            'adaptive': 自适应白平衡 (结合以上两种方法)
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    # 仅处理彩色图像
    if len(image.shape) != 3 or image.shape[2] != 3:
        return image
    
    # 使用灰色世界假设方法
    if method == 'gray_world':
        # 计算每个通道的平均值
        b_avg, g_avg, r_avg = np.mean(image[:, :, 0]), np.mean(image[:, :, 1]), np.mean(image[:, :, 2])
        
        # 计算整体平均值
        k = (b_avg + g_avg + r_avg) / 3
        
        # 计算增益
        kb, kg, kr = k / b_avg, k / g_avg, k / r_avg
        
        # 应用增益
        balanced = image.copy().astype(np.float32)
        balanced[:, :, 0] = np.clip(balanced[:, :, 0] * kb, 0, 255)
        balanced[:, :, 1] = np.clip(balanced[:, :, 1] * kg, 0, 255)
        balanced[:, :, 2] = np.clip(balanced[:, :, 2] * kr, 0, 255)
        
        return balanced.astype(np.uint8)
    
    # 使用完美反射假设方法
    elif method == 'perfect_reflector':
        # 找出每个通道的最大值
        b_max, g_max, r_max = np.max(image[:, :, 0]), np.max(image[:, :, 1]), np.max(image[:, :, 2])
        
        # 计算最大值中的最大值
        rgb_max = max(b_max, g_max, r_max)
        
        # 计算增益
        kb, kg, kr = rgb_max / b_max if b_max > 0 else 1.0, rgb_max / g_max if g_max > 0 else 1.0, rgb_max / r_max if r_max > 0 else 1.0
        
        # 应用增益
        balanced = image.copy().astype(np.float32)
        balanced[:, :, 0] = np.clip(balanced[:, :, 0] * kb, 0, 255)
        balanced[:, :, 1] = np.clip(balanced[:, :, 1] * kg, 0, 255)
        balanced[:, :, 2] = np.clip(balanced[:, :, 2] * kr, 0, 255)
        
        return balanced.astype(np.uint8)
    
    # 使用自适应方法（结合灰色世界和完美反射）
    elif method == 'adaptive':
        # 灰色世界部分
        b_avg, g_avg, r_avg = np.mean(image[:, :, 0]), np.mean(image[:, :, 1]), np.mean(image[:, :, 2])
        k = (b_avg + g_avg + r_avg) / 3
        kb_gw, kg_gw, kr_gw = k / b_avg, k / g_avg, k / r_avg
        
        # 完美反射部分
        b_max, g_max, r_max = np.max(image[:, :, 0]), np.max(image[:, :, 1]), np.max(image[:, :, 2])
        rgb_max = max(b_max, g_max, r_max)
        kb_pr, kg_pr, kr_pr = rgb_max / b_max if b_max > 0 else 1.0, rgb_max / g_max if g_max > 0 else 1.0, rgb_max / r_max if r_max > 0 else 1.0
        
        # 计算标准差，用于自适应权重
        b_std, g_std, r_std = np.std(image[:, :, 0]), np.std(image[:, :, 1]), np.std(image[:, :, 2])
        std_sum = b_std + g_std + r_std
        
        # 根据标准差计算权重，标准差越大，完美反射权重越大
        w_pr = min(1.0, std_sum / 100.0)  # 将标准差归一化
        w_gw = 1.0 - w_pr
        
        # 混合两种方法的增益
        kb = kb_gw * w_gw + kb_pr * w_pr
        kg = kg_gw * w_gw + kg_pr * w_pr
        kr = kr_gw * w_gw + kr_pr * w_pr
        
        # 应用增益
        balanced = image.copy().astype(np.float32)
        balanced[:, :, 0] = np.clip(balanced[:, :, 0] * kb, 0, 255)
        balanced[:, :, 1] = np.clip(balanced[:, :, 1] * kg, 0, 255)
        balanced[:, :, 2] = np.clip(balanced[:, :, 2] * kr, 0, 255)
        
        return balanced.astype(np.uint8)
    
    else:
        raise ValueError(f"不支持的白平衡方法: {method}")
        
def auto_image_enhance(image, contrast=True, color=True, white_balance=True):
    """一键增强图像，综合应用对比度增强、色彩校正和白平衡调整
    
    Args:
        image: 输入图像
        contrast: 是否应用对比度增强
        color: 是否应用色彩校正
        white_balance: 是否应用白平衡调整
    
    Returns:
        处理后的图像
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("输入必须是numpy数组")
    
    result = image.copy()
    
    # 首先应用白平衡
    if white_balance:
        result = auto_white_balance(result, method='adaptive')
    
    # 然后应用对比度增强
    if contrast:
        result = auto_contrast_enhancement(result)
    
    # 最后应用色彩校正
    if color:
        result = auto_color_correction(result)
    
    return result 