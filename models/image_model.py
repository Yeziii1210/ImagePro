"""
图像数据模型模块

主要功能：
1. 图像数据管理
   - 存储和管理原始图像数据
   - 维护当前处理状态
   - 支持图像预览功能

2. 历史记录管理
   - 使用双端队列实现撤销/重做功能
   - 自动限制历史记录大小
   - 支持历史状态切换

3. 异步处理机制
   - 使用线程池处理图像操作
   - 实现非阻塞的图像处理
   - 支持任务队列管理

4. 内存优化
   - 实现图像数据缓存机制
   - 自动垃圾回收
   - 内存使用监控

5. 信号通知
   - 图像变化通知
   - 历史记录更新通知
   - 错误处理通知

"""
import cv2
import numpy as np
from PySide6.QtGui import QImage
from PySide6.QtCore import QObject, Signal
from collections import deque
from app.config import config
import threading
from queue import Queue, Empty
import time
import gc
import weakref

class ImageModel(QObject):
    """图像数据模型类，负责图像数据的存储和管理"""
    
    # 信号定义，用于在图像处理过程中通知其他组件（如视图或控制器）发生了特定的事件。
    image_changed = Signal()  # 图像数据改变信号
    history_changed = Signal()  # 历史记录改变信号
    error_occurred = Signal(str)  # 错误信号
    
    def __init__(self):
        super().__init__()
        self._original_image = None  # 原始图像（OpenCV格式），用于重置，none表示尚未加载图像
        self._current_image = None   # 当前图像（OpenCV格式）
        self._preview_image = None   # 预览前的图像状态
        
        # 使用deque替代列表存储历史记录，便于限制长度
        self._max_history_size = config.get('performance.cache_size', 100)
        self._history = deque(maxlen=self._max_history_size)
        self._history_index = -1  # 当前历史记录索引
        
        # 处理队列
        self._process_queue = Queue() # 线程安全的队列，用于存储待处理的图像操作任务
        self._result_queue = Queue() # 线程安全的队列，用于存储处理结果
        self._stop_event = threading.Event() # 事件对象，用于停止处理线程
        
        # 启动处理线程
        self._process_thread = threading.Thread(target=self._process_worker)# 创建一个新的线程，目标函数为_process_worker，负责从处理队列中获取任务并执行。
        self._process_thread.daemon = True # 设置为守护线程，当主线程结束时，子线程也会自动结束。
        self._process_thread.start() # 启动线程
        
        # 图像缓存清理计时器
        self._last_gc_time = time.time()
        self._gc_interval = 60  # 每60秒检查一次是否需要清理内存
        
        # 图像像素数据引用计数，用于重用内存
        self._pixel_data_refs = {}
    
    @property
    def original_image(self):
        """获取原始图像"""
        return self._original_image
    
    @property
    def current_image(self):
        """获取当前图像"""
        return self._current_image
    
    def _process_worker(self):
        """
        处理线程工作函数
        从处理队列中获取任务并执行。
        """
        while not self._stop_event.is_set():
            try:
                # 获取处理任务
                task = self._process_queue.get(timeout=0.1)
                if task is None:
                    continue
                
                # 执行处理
                func, args, kwargs = task
                result = func(*args, **kwargs)
                
                # 返回结果
                self._result_queue.put(result)
                
                # 标记任务完成
                self._process_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self._result_queue.put(e)
                self._process_queue.task_done()
    
    def _add_to_history(self, image):
        """
        添加图像到历史记录，使用deque限制历史记录大小
        
        Args:
            image: 要添加的图像
        """
        # 检查当前索引是否在历史记录中间位置
        if self._history_index < len(self._history) - 1:
            # 删除当前位置之后的历史记录
            while len(self._history) > self._history_index + 1:
                self._history.pop()
        
        # 添加新图像（智能拷贝，避免不必要的内存分配）
        # 只在必要时进行深拷贝，减少内存消耗
        image_id = id(image)
        if image_id in self._pixel_data_refs:
            # 增加引用计数
            self._pixel_data_refs[image_id] += 1
            self._history.append(image)
        else:
            # 添加新引用
            img_copy = image.copy()
            self._pixel_data_refs[id(img_copy)] = 1
            self._history.append(img_copy)
        
        self._history_index = len(self._history) - 1
        
        # 检查是否需要主动清理内存
        self._check_memory_cleanup()
    
    def _check_memory_cleanup(self):
        """检查是否需要清理内存"""
        current_time = time.time()
        if current_time - self._last_gc_time > self._gc_interval:
            self._last_gc_time = current_time
            # 移除不再使用的图像数据的引用
            current_ids = set(id(img) for img in self._history)
            current_ids.add(id(self._current_image) if self._current_image is not None else 0)
            current_ids.add(id(self._original_image) if self._original_image is not None else 0)
            current_ids.add(id(self._preview_image) if self._preview_image is not None else 0)
            
            # 删除不再使用的引用计数
            to_remove = []
            for img_id in self._pixel_data_refs:
                if img_id not in current_ids:
                    to_remove.append(img_id)
            
            for img_id in to_remove:
                del self._pixel_data_refs[img_id]
            
            # 强制执行垃圾回收
            gc.collect()
    
    def load_image(self, file_path):
        """
        加载图像函数
        读取图像，并检查图像大小是否超过限制，如果超过限制，则抛出异常。（出于性能，资源考虑）
        将图像转换为RGB格式，并更新图像数据。（opencv读取的图像为BGR格式）
        
        Args:
            file_path (str): 图像文件路径
        """
        try:
            # 清理先前可能的大型图像数据
            if self._current_image is not None or self._original_image is not None:
                # 释放之前的图像引用
                self._current_image = None
                self._original_image = None
                self._preview_image = None
                
                # 清理历史记录
                self._history.clear()
                self._history_index = -1
                
                # 尝试回收内存
                gc.collect()
            
            # 读取图像
            image = cv2.imread(file_path, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"无法加载图像: {file_path}")
            
            # 检查图像大小
            max_size = config.get('image_processing.max_image_size', (10000, 10000))
            if image.shape[0] > max_size[0] or image.shape[1] > max_size[1]:
                raise ValueError(f"图像尺寸超过限制: {max_size}")
            """
            图像数组的shape通常包含三个维度：
            第一个维度(shape[0])：图像的高度（行数）
            第二个维度(shape[1])：图像的宽度（列数）
            第三个维度(shape[2])：颜色通道数（如RGB图像为3，灰度图像为1）
            """
            
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 更新图像数据
            self._original_image = image.copy()
            self._current_image = image.copy()
            self._preview_image = None  # 清除预览状态
            
            # 记录像素数据引用
            self._pixel_data_refs[id(self._original_image)] = 1
            self._pixel_data_refs[id(self._current_image)] = 1
            
            # 清空历史记录并添加当前图像
            self._history.clear()
            self._history.append(self._current_image)
            self._history_index = 0
            
            # 发出信号
            self.image_changed.emit()
            self.history_changed.emit()
            
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def save_image(self, file_path):
        """保存图像，主要是调用opencv的imwrite函数
        
        Args:
            file_path (str): 保存路径
        """
        try:
            if self._current_image is None:
                raise ValueError("没有可保存的图像")
            
            # 转换为BGR格式（OpenCV保存图像需要BGR格式）
            bgr_image = cv2.cvtColor(self._current_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, bgr_image)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def apply_operation(self, operation_func, *args, **kwargs):
        """应用图像处理操作
        
        Args:
            operation_func: 处理函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if self._current_image is None:
            return False
        
        try:
            # 如果有预览状态，先恢复
            base_image = self._current_image
            if self._preview_image is not None:
                base_image = self._preview_image
                self._preview_image = None
            
            # 保存当前状态到历史记录
            self._add_to_history(base_image)
            
            # 应用操作
            result = operation_func(base_image, *args, **kwargs)
            if result is not None:
                self._current_image = result
                # 记录新图像的引用
                self._pixel_data_refs[id(result)] = 1
            
            # 发出信号
            self.image_changed.emit()
            self.history_changed.emit()
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def undo(self):
        """撤销操作"""
        if self._history_index > 0:
            # 清除预览状态
            self._preview_image = None
            
            self._history_index -= 1
            # 使用引用而非拷贝以节省内存
            self._current_image = self._history[self._history_index]
            self.image_changed.emit()
            self.history_changed.emit()
            return True
        return False
    
    def redo(self):
        """重做操作"""
        if self._history_index < len(self._history) - 1:
            # 清除预览状态
            self._preview_image = None
            
            self._history_index += 1
            # 使用引用而非拷贝以节省内存
            self._current_image = self._history[self._history_index]
            self.image_changed.emit()
            self.history_changed.emit()
            return True
        return False
    
    def reset(self):
        """重置为原始图像"""
        if self._original_image is not None:
            # 清除预览状态
            self._preview_image = None
            
            self._add_to_history(self._original_image)
            self._current_image = self._original_image
            self.image_changed.emit()
            self.history_changed.emit()
            return True
        return False
    
    def to_qimage(self, image=None):
        """将OpenCV图像转换为QImage
        
        Args:
            image: OpenCV格式图像，如果为None则使用当前图像
        
        Returns:
            QImage: Qt图像对象
        """
        if image is None:
            image = self._current_image
        if image is None:
            return None
        
        # 确保图像是BGR格式
        if len(image.shape) == 2:  # 灰度图
            # 避免不必要的转换，直接创建QImage
            height, width = image.shape
            bytes_per_line = width
            return QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
        # 创建QImage
        height, width, channel = image.shape
        bytes_per_line = channel * width
        
        # 直接使用RGB格式创建QImage，避免额外的颜色空间转换
        return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    
    def get_image(self):
        """获取当前图像
        
        Returns:
            QImage: 当前图像
        """
        if self._current_image is None:
            return None
        
        # 使用优化后的to_qimage方法
        return self.to_qimage(self._current_image)
    
    def has_image(self):
        """检查是否有图像
        
        Returns:
            bool: 是否有图像
        """
        return self._current_image is not None
    
    def can_undo(self):
        """检查是否可以撤销
        
        Returns:
            bool: 是否可以撤销
        """
        return self._history_index > 0
    
    def can_redo(self):
        """检查是否可以重做
        
        Returns:
            bool: 是否可以重做
        """
        return self._history_index < len(self._history) - 1
    
    def process_image(self, func, *args, **kwargs):
        """处理图像
        
        Args:
            func: 处理函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            bool: 是否成功处理
        """
        try:
            if self._current_image is None:
                raise ValueError("没有可处理的图像")
            
            # 添加处理任务
            self._process_queue.put((func, args, kwargs))
            
            # 等待处理结果
            result = self._result_queue.get()
            
            # 检查是否有错误
            if isinstance(result, Exception):
                raise result
            
            # 更新图像
            self._current_image = result
            
            # 添加新图像引用
            self._pixel_data_refs[id(result)] = 1
            
            # 添加到历史记录
            self._add_to_history(result)
            
            # 发出信号
            self.image_changed.emit()
            
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def preview_operation(self, operation_func, *args, **kwargs):
        """预览图像处理操作，不添加到历史记录
        
        Args:
            operation_func: 处理函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if self._current_image is None:
            return False
        
        try:
            # 保存当前状态用于恢复
            if self._preview_image is None:
                self._preview_image = self._current_image.copy()
                # 记录预览图像引用
                self._pixel_data_refs[id(self._preview_image)] = 1
            
            # 基于预览前的图像应用操作
            result = operation_func(self._preview_image.copy(), *args, **kwargs)
            if result is not None:
                # 更新当前图像但不记录历史
                self._current_image = result
                # 记录结果图像引用
                self._pixel_data_refs[id(result)] = 1
            
            # 只发出图像变化信号，不发出历史变化信号，确保预览时不会产生历史记录
            self.image_changed.emit()
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def apply_last_preview(self):
        """将当前预览应用为正式操作，添加到历史记录"""
        if self._current_image is None:
            return False
        
        # 保存当前状态到历史记录
        self._add_to_history(self._preview_image if self._preview_image is not None else self._current_image)
        self._preview_image = None  # 清除预览状态
        
        # 发出历史变化信号
        self.history_changed.emit()
        return True
    
    def clear_memory(self):
        """主动清理内存"""
        # 整理历史记录
        if len(self._history) > self._max_history_size / 2:
            # 仅保留必要的历史记录
            step = 2 if len(self._history) > self._max_history_size * 0.8 else 1
            new_history = deque(maxlen=self._max_history_size)
            
            # 保留当前索引和关键点的历史
            for i in range(0, len(self._history), step):
                if i == self._history_index or i == 0 or i == len(self._history) - 1:
                    new_history.append(self._history[i])
            
            # 更新历史记录和索引
            self._history_index = list(new_history).index(self._history[self._history_index])
            self._history = new_history
        
        # 清理像素数据引用
        self._check_memory_cleanup()
        
        # 强制垃圾回收
        gc.collect()
    
    def __del__(self):
        """析构函数"""
        # 停止处理线程
        self._stop_event.set()
        if self._process_thread.is_alive():
            self._process_thread.join()
        
        # 清理资源
        self._current_image = None
        self._original_image = None
        self._preview_image = None
        self._history.clear()
        self._pixel_data_refs.clear()
        
        # 强制清理内存
        gc.collect()
