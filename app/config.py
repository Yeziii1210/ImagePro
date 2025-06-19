"""
应用程序配置文件
"""
import os
import platform
from pathlib import Path
import psutil

class AppConfig:
    """应用程序配置类"""
    
    def __init__(self):
        self._config = {}
        self.load_default_config()
    
    def load_default_config(self):
        """加载默认配置"""
        # 获取系统内存信息，用于智能配置缓存大小
        system_memory = psutil.virtual_memory().total // (1024 * 1024 * 1024)  # 内存大小（GB）
        
        # 根据系统内存大小配置缓存
        if system_memory < 4:  # 小于4GB内存的设备
            cache_size = 50
            thread_pool_size = 2
        elif system_memory < 8:  # 4-8GB内存的设备
            cache_size = 75
            thread_pool_size = 3
        else:  # 8GB以上内存的设备
            cache_size = 100
            thread_pool_size = 4
        
        self._config = {
            'image_processing': {
                'filter_size': 3,
                'brightness': 0,
                'contrast': 1.0,
                'max_image_size': (10000, 10000)
            },
            'ui': {
                'window_title': "图像处理软件",
                'window_size': (1024, 768),
                'theme': 'dark_theme', # 默认主题，可以是 'dark_theme' 或 'light_theme'
                'language': 'zh_CN'
            },
            'paths': {
                'save_dir': str(Path.home() / 'Pictures' / 'ImagePro'),
                'temp_dir': str(Path.home() / 'AppData' / 'Local' / 'Temp' / 'ImagePro')
            },
            'performance': {
                'thread_pool_size': thread_pool_size,
                'cache_size': cache_size,  # 缓存最近处理的图像数量
                'memory_check_interval': 60,  # 内存检查间隔时间（秒）
                'auto_gc_threshold': 80,  # 内存使用率超过此值时触发垃圾回收（百分比）
                'lazy_loading': True,  # 是否使用延迟加载优化启动速度
                'preview_quality': 'medium',  # 预览质量：low, medium, high
                'image_downscale_threshold': 20,  # 超过此分辨率（百万像素）时自动缩小预览图像
                'tile_size': 256,  # 图像处理时的分块大小
            }
        }
        
        # 根据操作系统调整路径
        if platform.system() != 'Windows':
            self._config['paths']['temp_dir'] = str(Path.home() / '.cache' / 'ImagePro')
        
        # 确保必要的目录存在
        os.makedirs(self._config['paths']['save_dir'], exist_ok=True)
        os.makedirs(self._config['paths']['temp_dir'], exist_ok=True)
    
    def get(self, key, default=None):
        """获取配置值
        
        Args:
            key (str): 配置键，支持点号分隔的多级键
            default: 默认值，当键不存在时返回
        
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """设置配置值
        
        Args:
            key (str): 配置键，支持点号分隔的多级键
            value: 要设置的值
        """
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save_to_file(self, filename):
        """保存配置到文件
        
        Args:
            filename (str): 配置文件名
        """
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)
    
    def load_from_file(self, filename):
        """从文件加载配置
        
        Args:
            filename (str): 配置文件名
        """
        import json
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
    
    def get_memory_usage(self):
        """获取当前内存使用情况
        
        Returns:
            dict: 内存使用信息
        """
        usage = psutil.virtual_memory()
        return {
            'total': usage.total,
            'available': usage.available,
            'percent': usage.percent,
            'used': usage.used,
            'free': usage.free
        }
    
    def is_low_memory(self):
        """检查是否处于低内存状态
        
        Returns:
            bool: 是否处于低内存状态
        """
        memory = self.get_memory_usage()
        return memory['percent'] > self.get('performance.auto_gc_threshold', 80)

# 创建全局配置实例
config = AppConfig() 