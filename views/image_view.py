"""
图像视图模块

实现ImageView类，用于在GUI中显示和操作图像。主要功能包括：

1. 图像显示
   - 支持显示OpenCV格式(numpy数组)和Qt格式(QImage)的图像
   - 自动调整图像大小以适应视图
   - 支持图像缩放和平移操作

2. 图像缓存
   - 使用LRU(最近最少使用)缓存机制优化性能
   - 缓存最近使用的图像数据，减少重复处理
   - 自动管理缓存大小，防止内存溢出

3. 交互功能
   - 支持鼠标滚轮缩放
   - 支持鼠标拖拽平移
   - 支持键盘快捷键操作

4. 性能优化
   - 使用弱引用避免内存泄漏
   - 实现图像数据的延迟加载
   - 优化大图像的处理和显示

5. 信号机制
   - 定义imageChanged信号，当图像更新时发出
   - 定义viewChanged信号，当视图状态（缩放、平移等）改变时发出
   - 定义mousePositionChanged信号，当鼠标在图像上移动时发出坐标信息
   - 定义selectionChanged信号，当用户选择区域改变时发出
   - 所有信号都支持与Qt组件的标准信号槽连接机制

主要类：
- LRUCache: 实现最近最少使用的缓存机制
- ImageView: 继承自QGraphicsView，实现图像显示和交互功能
"""

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, Signal, QRectF, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QTransform
import numpy as np
import gc
import weakref
from collections import OrderedDict

class LRUCache(OrderedDict):
    """
    实现一个最近最少使用(Least Recently Used)的缓存机制。
    
    主要用途:
    - 缓存最近使用的图像数据,提高访问速度
    - 当缓存达到容量上限时,自动删除最久未使用的项目
    - 通过OrderedDict有序字典实现,保持插入顺序
    
    属性:
        capacity: int, 缓存的最大容量
        
    方法:
        get(key): 获取缓存项,如果存在则移到最新位置
        put(key, value): 插入新的缓存项,如果超出容量则删除最旧的
    """
    
    def __init__(self, capacity): #初始化缓存容量
        super().__init__() #调用父类OrderedDict的初始化方法
        self.capacity = capacity #缓存容量
        
    def get(self, key): #获取缓存，key是缓存项的键，用于标识和访问缓存中的数据
        if key not in self:
            return None
        self.move_to_end(key) #将key移动到末尾
        return self[key] #返回key的值
    
    def put(self, key, value):
        if key in self:
            self.move_to_end(key)
        self[key] = value #将key的值赋值给value
        if len(self) > self.capacity: #如果缓存大小大于缓存容量
            self.popitem(last=False) #移除最早的缓存项

class ImageView(QGraphicsView):
    """图像视图类"""
    
    # 信号定义
    image_changed = Signal()  # 图像改变信号
    local_exposure_position_selected = Signal(int, int)  # 局部曝光位置选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建场景
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        # 设置视图属性
        self.setRenderHint(QPainter.Antialiasing) #抗锯齿，提高图像质量
        self.setRenderHint(QPainter.SmoothPixmapTransform) #平滑变换，提高图像质量
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) #水平滚动条，根据需要显示
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) #垂直滚动条，根据需要显示
        self.setDragMode(QGraphicsView.ScrollHandDrag) #拖动手柄，用于拖动图像
        self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate) #优化为最小视口更新，减少渲染
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse) #变换锚点，鼠标位置
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse) #调整大小锚点，鼠标位置
        
        # 使用像素缓存减少重绘消耗
        # CacheBackground: 缓存背景内容,减少重绘
        # CacheAll: 缓存所有内容,包括前景和背景
        # NoCache: 不缓存,每次都重绘
        # 这里选择CacheBackground是因为:
        # 1. 图像作为背景内容,变化不频繁
        # 2. 比CacheAll更节省内存
        # 3. 在滚动和缩放时仍能保持流畅
        self.setCacheMode(QGraphicsView.CacheBackground)
        
        # 图像数据
        self._image = None
        self._pixmap_item = None
        self._scale_factor = 1.0
        
        # 高级缓存策略
        self._cache = LRUCache(10)  # 使用LRU缓存策略
        self._last_viewport_size = QSize()
        self._last_gc_time = 0
        
        # 局部曝光模式
        self._local_exposure_mode = False
    
    def set_image(self, image):
        """设置图像    
        此函数用于在视图中显示新的图像。主要功能包括：
        1. 清空当前场景和图像数据
        2. 将新的QImage转换为QPixmap并创建图形项
        3. 将图像项添加到场景中
        4. 调整视图以适应图像大小
        5. 发出图像改变信号
        6. 清理缓存
        
        实现细节：
        - 使用QGraphicsPixmapItem显示图像，支持高质量缩放
        - 设置平滑变换模式提高图像质量
        - 自动调整视图大小以适应图像
        - 使用缓存机制优化性能
        - 在图像改变时发出信号通知其他组件

        Args:
            image: QImage对象
        """
        if image is None: #如果图像为空
            self._scene.clear() #清空场景
            self._image = None #清空图像
            self._pixmap_item = None #清空像素图
            self._scale_factor = 1.0 #缩放因子
            self._cache.clear()  # 清空缓存
            self.image_changed.emit() #发出图像改变信号
            return
        
        # 更新图像
        self._image = image
        
        # 清空场景并添加新图像
        self._scene.clear()
        
        # 创建QPixmap并使用QGraphicsPixmapItem代替直接添加QPixmap
        # 使用QPixmap.fromImage()将QImage转换为QPixmap,因为QGraphicsScene需要QPixmap
        pixmap = QPixmap.fromImage(image)
        self._pixmap_item = QGraphicsPixmapItem(pixmap) # 创建QGraphicsPixmapItem对象,用于在场景中显示图像
        self._pixmap_item.setTransformationMode(Qt.SmoothTransformation) # 设置变换模式为平滑变换,提高图像缩放质量
        self._scene.addItem(self._pixmap_item) # 将图像项添加到场景中
        
        # 设置场景大小
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        
        # 调整视图
        self.fit_in_view()
        
        # 发出信号
        self.image_changed.emit()
        
        # 清理不需要的缓存
        self._clear_unused_cache()
    
    def fit_in_view(self):
        """
        调整视图以适应图像大小，确保图像完整显示在视图中
        实现步骤：
        1. 检查图像是否存在
        2. 获取视图和场景的矩形区域
        3. 计算合适的缩放因子
        4. 应用缩放变换
        5. 更新缓存策略

        """
        if self._pixmap_item is None:
            return
        
        # 计算缩放因子，缩放图像提高性能
        # 获取视图的矩形区域
        view_rect = self.viewport().rect()
        # 获取场景的矩形区域
        scene_rect = self._scene.sceneRect()
        
        # 记录视口大小，用于缓存策略
        self._last_viewport_size = view_rect.size()
        
        # 计算缩放因子
        width_ratio = view_rect.width() / scene_rect.width()
        height_ratio = view_rect.height() / scene_rect.height()
        
        # 选择较小的缩放因子，确保图像完整显示
        self._scale_factor = min(width_ratio, height_ratio)
        
        # 应用变换
        # 重置变换矩阵
        self.resetTransform()
        # 缩放图像）
        self.scale(self._scale_factor, self._scale_factor)
    
    def wheelEvent(self, event):
        """鼠标滚轮事件处理
        
        Args:
            event: 事件对象
        """
        if self._pixmap_item is None:
            return
        
        # 计算缩放因子
        # 如果滚轮向上滚动，缩放因子为1.1，否则为0.9
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        
        # 限制缩放范围
        new_scale = self._scale_factor * factor
        if 0.1 <= new_scale <= 10.0:
            self._scale_factor = new_scale
            
            # 检查缓存中是否已有此缩放级别的图像
            cache_key = f"scale_{self._scale_factor:.2f}"
            cached_transform = self._cache.get(cache_key)
            
            if cached_transform:
                # 使用缓存的变换
                self.setTransform(cached_transform)
            else:
                # 应用新变换并缓存
                self.scale(factor, factor)
                self._cache.put(cache_key, self.transform())
    
    def resizeEvent(self, event):
        """窗口大小改变事件处理
        
        Args:
            event: 事件对象
        """
        super().resizeEvent(event)
        # 只有当窗口大小变化显著时才重新适应视图
        current_size = self.viewport().size()
        if abs(current_size.width() - self._last_viewport_size.width()) > 20 or \
           abs(current_size.height() - self._last_viewport_size.height()) > 20:
            if self._pixmap_item is not None:
                self.fit_in_view()
                self._last_viewport_size = current_size
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理
        
        Args:
            event: 事件对象
        """
        if self._local_exposure_mode and event.button() == Qt.LeftButton:
            # 在局部曝光模式下，获取鼠标点击位置并发送信号
            pos = self.mapToScene(event.pos())
            x = int(pos.x())
            y = int(pos.y())
            self.local_exposure_position_selected.emit(x, y)
        else:
            # 正常模式下的处理
            if event.button() == Qt.LeftButton:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理
        
        Args:
            event: 事件对象
        """
        if event.button() == Qt.LeftButton: #如果按下的是左键，则设置拖动手柄模式
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event) #调用父类的事件处理方法
    
    def get_image_region(self, rect):
        """获取图像区域
        从当前图像中提取指定区域的图像数据
        处理坐标转换和缩放
        确保提取的区域在有效范围内
        
        Args:
            rect: QRectF对象，指定区域
            
        Returns:
            QImage: 区域图像
        """
        if self._image is None:
            return None
        
        # 使用缓存检查是否已经计算过这个区域
        cache_key = f"region_{rect.x()}_{rect.y()}_{rect.width()}_{rect.height()}"
        cached_image = self._cache.get(cache_key)
        if cached_image:
            return cached_image
        
        # 转换坐标
        scene_rect = self.mapToScene(rect.toRect()).boundingRect()
        image_rect = self._scene.sceneRect()
        
        # 计算缩放比例
        scale_x = self._image.width() / image_rect.width()
        scale_y = self._image.height() / image_rect.height()
        
        # 计算图像坐标
        x = int(scene_rect.x() * scale_x)
        y = int(scene_rect.y() * scale_y)
        width = int(scene_rect.width() * scale_x)
        height = int(scene_rect.height() * scale_y)
        
        # 确保坐标在有效范围内
        x = max(0, min(x, self._image.width() - 1))
        y = max(0, min(y, self._image.height() - 1))
        width = min(width, self._image.width() - x)
        height = min(height, self._image.height() - y)
        
        # 复制区域
        result = self._image.copy(x, y, width, height)
        
        # 缓存结果
        self._cache.put(cache_key, result)
        
        return result
    
    def get_current_transform(self):
        """获取当前变换矩阵
        
        Returns:
            QTransform: 变换矩阵
        """
        return self.transform()
    
    def apply_transform(self, transform):
        """应用变换矩阵
        
        Args:
            transform: QTransform对象
        """
        self.setTransform(transform)
        self._scale_factor = transform.m11()  # 使用水平缩放作为缩放因子
    
    def _clear_unused_cache(self):
        """清理不再需要的缓存"""
        # 限制缓存大小
        while len(self._cache) > 10:
            self._cache.popitem(last=False)  # 移除最早的缓存项
        
        # 建议垃圾回收
        gc.collect()
    
    def clear_cache(self):
        """清空缓存，用于主动释放内存"""
        self._cache.clear()
        gc.collect()

    def update_image(self, image):
        """更新图像
        
        Args:
            image: OpenCV格式的图像
        """
        if image is None:
            return
        
        # 以线程安全的方式更新图像
        try:
            # 将OpenCV图像转换为QImage
            if len(image.shape) == 3:
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            else:
                height, width = image.shape
                qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)
            
            # 转换为QPixmap
            pixmap = QPixmap.fromImage(qimage)
            
            # 设置场景图像
            self._set_pixmap(pixmap)
            
            # 更新缓存
            self._cache_current_pixmap(pixmap)
            
            # 重置视图
            if self._first_image:
                self.reset_view()
                self._first_image = False
            
        except Exception as e:
            print(f"更新图像失败: {e}")
            # 可以添加更多错误处理逻辑 

    def _set_pixmap(self, pixmap):
        """设置场景中的图像
        
        Args:
            pixmap: 图像数据，QPixmap对象
        """
        if pixmap is None or pixmap.isNull():
            return
        
        # 清空现有场景
        self._scene.clear()
        
        # 添加新的图像项
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        self._scene.addItem(self._pixmap_item)
        
        # 更新场景矩形
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        
        # 发出信号
        self.image_changed.emit()

    def _cache_current_pixmap(self, pixmap):
        """缓存当前图像
        
        Args:
            pixmap: QPixmap对象
        """
        if pixmap is None or pixmap.isNull():
            return
        
        # 缓存当前图像
        self._cache.put("current_pixmap", pixmap)
        
        # 如果是第一次设置图像，初始化标志
        if not hasattr(self, '_first_image'):
            self._first_image = True

    def reset_view(self):
        """重置视图，适应图像大小并居中"""
        if self._pixmap_item is None:
            return
        
        # 适应视图
        self.fit_in_view()
        
        # 居中
        self.centerOn(self._scene.sceneRect().center())

    def set_local_exposure_mode(self, enabled):
        """设置局部曝光模式
        
        Args:
            enabled: 是否启用局部曝光模式
        """
        self._local_exposure_mode = enabled
        if enabled:
            # 在局部曝光模式下禁用拖动
            self.setDragMode(QGraphicsView.NoDrag)
            # 更改鼠标指针形状为十字形
            self.setCursor(Qt.CrossCursor)
        else:
            # 恢复正常模式
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            # 恢复默认光标
            self.unsetCursor() 