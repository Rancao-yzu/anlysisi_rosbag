"""bag_parser 包：提供 ROS Bag 文件的解析与 CSV 导出功能。

核心模块：
    core.py      - 读取 bag 文件、获取 topic 信息
    flattener.py - 将任意 ROS 消息递归展平为扁平字典
    exporter.py  - 将展平后的数据导出为 CSV
"""
from .core import get_topic_info, read_messages
from .exporter import export_to_csv
