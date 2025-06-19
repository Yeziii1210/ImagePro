"""
内存监控器模块 - 用于管理应用程序的内存使用
"""
import psutil
import gc
import time
import threading
import weakref
from PySide6.QtCore import QObject, Signal
from app.config import config

class MemoryMonitor(QObject):
    """内存监控器类，管理应用内存使用"""
    
    # 定义信号
    memory_warning = Signal(float)  # 内存使用率警告信号
    memory_critical = Signal(float)  # 内存使用率危急信号
    memory_status = Signal(dict)  # 内存状态信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 内存使用阈值
        self._warning_threshold = 70  # 警告阈值（百分比）
        self._critical_threshold = config.get('performance.auto_gc_threshold', 80)  # 危急阈值（百分比）
        
        # 监控状态
        self._running = False
        self._stop_event = threading.Event()
        self._monitor_thread = None
        
        # 被监控的对象
        self._image_model_ref = None
        self._image_view_ref = None
        
        # 上次清理时间
        self._last_cleanup_time = 0
        self._cleanup_interval = config.get('performance.memory_check_interval', 60)  # 清理间隔（秒）
    
    def start_monitoring(self, check_interval=5):
        """开始内存监控
        
        Args:
            check_interval: 检查间隔（秒）
        """
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        # 启动监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_memory, args=(check_interval,))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止内存监控"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
    
    def register_image_model(self, image_model):
        """注册图像模型对象
        
        Args:
            image_model: ImageModel实例
        """
        self._image_model_ref = weakref.ref(image_model)
    
    def register_image_view(self, image_view):
        """注册图像视图对象
        
        Args:
            image_view: ImageView实例
        """
        self._image_view_ref = weakref.ref(image_view)
    
    def get_memory_info(self):
        """获取内存使用信息
        
        Returns:
            dict: 内存使用信息
        """
        memory = psutil.virtual_memory()
        return {
            'total': memory.total / (1024 * 1024),  # MB
            'used': memory.used / (1024 * 1024),    # MB
            'free': memory.free / (1024 * 1024),    # MB
            'percent': memory.percent               # 百分比
        }
    
    def force_cleanup(self):
        """强制清理内存"""
        self._perform_cleanup(force=True)
        self._last_cleanup_time = time.time()
    
    def _monitor_memory(self, interval):
        """内存监控线程函数
        
        Args:
            interval: 检查间隔（秒）
        """
        while not self._stop_event.is_set():
            try:
                # 获取内存使用信息
                memory_info = self.get_memory_info()
                
                # 发送内存状态信号
                self.memory_status.emit(memory_info)
                
                # 检查内存使用率
                if memory_info['percent'] >= self._critical_threshold:
                    # 发送危急信号
                    self.memory_critical.emit(memory_info['percent'])
                    # 执行清理
                    self._perform_cleanup(force=True)
                elif memory_info['percent'] >= self._warning_threshold:
                    # 发送警告信号
                    self.memory_warning.emit(memory_info['percent'])
                    # 检查是否需要执行清理
                    current_time = time.time()
                    if current_time - self._last_cleanup_time >= self._cleanup_interval:
                        self._perform_cleanup()
                        self._last_cleanup_time = current_time
            except Exception as e:
                print(f"内存监控错误: {str(e)}")
            
            # 等待下一次检查
            for _ in range(int(interval)):
                if self._stop_event.is_set():
                    break
                time.sleep(1)
    
    def _perform_cleanup(self, force=False):
        """执行内存清理
        
        Args:
            force: 是否强制清理
        """
        # 清理图像模型缓存
        if self._image_model_ref:
            image_model = self._image_model_ref()
            if image_model:
                try:
                    image_model.clear_memory()
                except Exception as e:
                    print(f"清理图像模型缓存失败: {str(e)}")
        
        # 清理图像视图缓存
        if self._image_view_ref:
            image_view = self._image_view_ref()
            if image_view:
                try:
                    image_view.clear_cache()
                except Exception as e:
                    print(f"清理图像视图缓存失败: {str(e)}")
        
        # 强制清理时执行完整垃圾回收
        if force:
            collected = gc.collect(2)  # 完整收集
            print(f"垃圾回收完成，回收了 {collected} 个对象")
        else:
            gc.collect(0)  # 仅收集最年轻的对象

# 创建全局内存监控实例
memory_monitor = MemoryMonitor() 