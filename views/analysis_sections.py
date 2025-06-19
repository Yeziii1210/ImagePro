"""
图像分析功能模块
包含直方图显示、均衡化等图像分析功能
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QCheckBox)
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPolygon

from .adjustment_section_widget import AdjustmentSectionWidget

class HistogramView(QWidget):
    """直方图显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hist_data = None
        self._hist_color = QColor(0, 0, 255)  # 默认蓝色
        self._max_value = 1
        self.setMinimumSize(200, 150)
        self.setObjectName("histogramView")
    
    def set_histogram_data(self, hist_data, color=None):
        """设置直方图数据
        
        Args:
            hist_data: 直方图数据
            color: 直方图颜色
        """
        self._hist_data = hist_data
        if color:
            self._hist_color = color
        
        # 找到最大值用于归一化
        if hist_data is not None:
            self._max_value = max(hist_data.max(), 1)
        
        # 更新显示
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        if self._hist_data is None:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置绘图区域
        width = self.width()
        height = self.height()
        padding = 15
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding
        
        # 设置背景色
        painter.fillRect(self.rect(), QColor(45, 45, 45))
        
        # 绘制图表背景
        chart_rect = QRect(padding, padding, chart_width, chart_height)
        painter.fillRect(chart_rect, QColor(30, 30, 30))
        
        # 设置画笔和画刷
        pen = QPen(self._hist_color)
        pen.setWidth(2)  # 增加线条宽度
        painter.setPen(pen)
        
        # 设置半透明填充画刷
        fill_color = QColor(self._hist_color)
        fill_color.setAlpha(80)  # 半透明效果
        brush = QBrush(fill_color)
        painter.setBrush(brush)
        
        # 绘制坐标轴
        axis_pen = QPen(QColor(80, 80, 80))
        axis_pen.setWidth(1)
        painter.setPen(axis_pen)
        painter.setBrush(QBrush())  # 清除填充
        
        painter.drawLine(padding, height - padding, width - padding, height - padding)  # x轴
        painter.drawLine(padding, padding, padding, height - padding)  # y轴
        
        # 绘制网格线
        grid_pen = QPen(QColor(60, 60, 60))
        grid_pen.setWidth(1)
        grid_pen.setStyle(Qt.DashLine)
        painter.setPen(grid_pen)
        
        # 垂直网格线
        for i in range(1, 5):
            x = padding + (chart_width * i / 4)
            painter.drawLine(int(x), padding, int(x), height - padding)
        
        # 水平网格线
        for i in range(1, 4):
            y = padding + (chart_height * i / 3)
            painter.drawLine(padding, int(y), width - padding, int(y))
        
        # 绘制直方图
        if len(self._hist_data) > 0:
            # 重新设置画笔和画刷用于直方图
            painter.setPen(pen)
            painter.setBrush(brush)
            
            bin_width = chart_width / len(self._hist_data)
            
            # 改进归一化：使用95百分位数作为最大值，避免极值影响显示
            hist_values = self._hist_data.flatten()
            effective_max = np.percentile(hist_values, 95)
            if effective_max == 0:
                effective_max = self._max_value
            
            # 创建多边形路径用于填充
            polygon_points = []
            polygon_points.append(QPoint(int(padding), int(height - padding)))
            
            for i, value in enumerate(hist_values):
                # 改进的归一化值
                normalized_value = min((value / effective_max) * chart_height, chart_height)
                
                # 计算位置
                x = padding + i * bin_width
                y = height - padding - normalized_value
                
                # 添加到多边形
                polygon_points.append(QPoint(int(x), int(y)))
            
            # 闭合多边形
            polygon_points.append(QPoint(int(width - padding), int(height - padding)))
            
            # 绘制填充的多边形
            if len(polygon_points) > 2:
                polygon = QPolygon(polygon_points)
                painter.drawPolygon(polygon)
            
            # 绘制线条轮廓
            painter.setBrush(QBrush())  # 只绘制轮廓
            pen.setWidth(2)
            painter.setPen(pen)
            
            for i in range(len(hist_values) - 1):
                value1 = hist_values[i]
                value2 = hist_values[i + 1]
                
                normalized_value1 = min((value1 / effective_max) * chart_height, chart_height)
                normalized_value2 = min((value2 / effective_max) * chart_height, chart_height)
                
                x1 = padding + i * bin_width
                y1 = height - padding - normalized_value1
                x2 = padding + (i + 1) * bin_width
                y2 = height - padding - normalized_value2
                
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # 绘制边框
        border_pen = QPen(QColor(100, 100, 100))
        border_pen.setWidth(2)
        painter.setPen(border_pen)
        painter.setBrush(QBrush())
        painter.drawRect(padding, padding, chart_width, chart_height)
        
        # 确保QPainter正确结束
        painter.end()


class MultiChannelHistogramView(QWidget):
    """多通道直方图显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("multiChannelHistogramView")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 创建三个直方图视图
        self.red_hist_view = HistogramView()
        self.green_hist_view = HistogramView()
        self.blue_hist_view = HistogramView()
        
        # 设置尺寸
        for view in [self.red_hist_view, self.green_hist_view, self.blue_hist_view]:
            view.setFixedHeight(80)
        
        # 创建标签和直方图的组合
        # 红色通道
        red_layout = QHBoxLayout()
        red_label = QLabel("R")
        red_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        red_label.setFixedWidth(15)
        red_layout.addWidget(red_label)
        red_layout.addWidget(self.red_hist_view)
        layout.addLayout(red_layout)
        
        # 绿色通道
        green_layout = QHBoxLayout()
        green_label = QLabel("G")
        green_label.setStyleSheet("color: #51cf66; font-weight: bold; font-size: 12px;")
        green_label.setFixedWidth(15)
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_hist_view)
        layout.addLayout(green_layout)
        
        # 蓝色通道
        blue_layout = QHBoxLayout()
        blue_label = QLabel("B")
        blue_label.setStyleSheet("color: #339af0; font-weight: bold; font-size: 12px;")
        blue_label.setFixedWidth(15)
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self.blue_hist_view)
        layout.addLayout(blue_layout)
    
    def set_histogram_data(self, hist_data_list):
        """设置直方图数据
        
        Args:
            hist_data_list: 包含三个通道的直方图数据的列表 [blue_hist, green_hist, red_hist]
        """
        if hist_data_list is None or len(hist_data_list) != 3:
            return
        
        # 设置各通道数据，注意颜色对应
        self.blue_hist_view.set_histogram_data(hist_data_list[0], QColor(51, 154, 240))  # 蓝色
        self.green_hist_view.set_histogram_data(hist_data_list[1], QColor(81, 207, 102))  # 绿色
        self.red_hist_view.set_histogram_data(hist_data_list[2], QColor(255, 107, 107))  # 红色


class HistogramSection(AdjustmentSectionWidget):
    """直方图分析区域"""
    
    # 信号
    preview_requested = Signal(str, dict)
    apply_requested = Signal(str, dict)
    histogram_requested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__("直方图分析", parent)
        self._build_ui()
    
    def _build_ui(self):
        """构建用户界面"""
        # 通道选择
        channel_layout = QHBoxLayout()
        channel_label = QLabel("显示通道:")
        self.channel_combo = QComboBox()
        self.channel_combo.addItem("RGB 合成", "all")
        self.channel_combo.addItem("红色通道", "red")
        self.channel_combo.addItem("绿色通道", "green")
        self.channel_combo.addItem("蓝色通道", "blue")
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.channel_combo)
        self.add_layout(channel_layout)
        
        # 直方图显示区域
        self.single_hist_view = HistogramView()
        self.single_hist_view.setFixedHeight(120)
        self.multi_hist_view = MultiChannelHistogramView()
        
        # 默认显示多通道视图
        self.single_hist_view.hide()
        
        self.add_widget(self.single_hist_view)
        self.add_widget(self.multi_hist_view)
        
        # 直方图均衡化选项
        self.per_channel_checkbox = QCheckBox("对每个通道分别均衡化")
        self.add_widget(self.per_channel_checkbox)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        
        self.equalize_button = QPushButton("直方图均衡化")
        self.equalize_button.clicked.connect(self._on_equalize_clicked)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.equalize_button)
        self.add_layout(buttons_layout)
    
    def _on_channel_changed(self, index):
        """通道选择改变"""
        channel = self.channel_combo.currentData()
        
        if channel == "all":
            # 显示多通道视图
            self.single_hist_view.hide()
            self.multi_hist_view.show()
        else:
            # 显示单通道视图
            self.multi_hist_view.hide()
            self.single_hist_view.show()
        
        # 请求更新直方图数据
        self._request_histogram()
    
    def _on_refresh_clicked(self):
        """刷新直方图"""
        self._request_histogram()
    
    def _on_equalize_clicked(self):
        """执行直方图均衡化"""
        params = {
            'per_channel': self.per_channel_checkbox.isChecked()
        }
        print(f"HistogramSection: Emitting apply_requested for histogram_equalization with params: {params}")
        self.apply_requested.emit("histogram_equalization", params)
    
    def _request_histogram(self):
        """请求直方图数据"""
        channel = self.channel_combo.currentData()
        params = {'channel': channel}
        print(f"HistogramSection: Requesting histogram data for channel: {channel}")
        self.histogram_requested.emit(params)
    
    def update_histogram(self, hist_data):
        """更新直方图显示
        
        Args:
            hist_data: 直方图数据，可以是单通道数据或多通道数据列表
        """
        channel = self.channel_combo.currentData()
        
        if channel == "all":
            # 多通道显示
            if isinstance(hist_data, list) and len(hist_data) == 3:
                self.multi_hist_view.set_histogram_data(hist_data)
        else:
            # 单通道显示
            if hasattr(hist_data, '__len__') and not isinstance(hist_data, list):
                # 单个通道的数组数据
                color_map = {
                    'red': QColor(255, 107, 107),
                    'green': QColor(81, 207, 102),
                    'blue': QColor(51, 154, 240)
                }
                color = color_map.get(channel, QColor(128, 128, 128))
                self.single_hist_view.set_histogram_data(hist_data, color)
    
    def get_parameters(self) -> dict:
        """获取当前参数"""
        return {
            'channel': self.channel_combo.currentData(),
            'per_channel': self.per_channel_checkbox.isChecked()
        }
    
    def set_parameters(self, params: dict):
        """设置参数"""
        if 'channel' in params:
            # 找到对应的索引
            for i in range(self.channel_combo.count()):
                if self.channel_combo.itemData(i) == params['channel']:
                    self.channel_combo.setCurrentIndex(i)
                    break
        
        if 'per_channel' in params:
            self.per_channel_checkbox.setChecked(params['per_channel'])
