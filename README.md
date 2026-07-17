# ROS Bag Parser

一个用于解析 ROS bag 文件并导出 CSV 的桌面工具。

## 功能特性

- **动态解析**：无需预先了解 bag 文件内容，可解析任意类型的 ROS bag
- **桌面图形界面（ttk）**：扁平化设计，橙色+白色配色，简洁直观
- **进度条**：实时显示消息展平和 CSV 导出的进度
- **灵活配置**：所有参数可在 `config.py` 中自定义设置（含样式配置）
- **一键打包**：提供 `build.sh` 脚本，可打包为独立可执行文件

## 项目结构

```
anlysisi_rosbag/
├── src/
│   ├── bag_parser/        # 核心解析模块
│   │   ├── core.py       # bag 读取、topic 信息获取
│   │   ├── flattener.py  # 消息展平（解析任意消息结构）
│   │   └── exporter.py   # CSV 导出
│   ├── config.py         # 配置（解析参数 + GUI 样式）
│   └── app.py            # 桌面 GUI 入口 (ttk)
├── build.sh              # 打包脚本
└── README.md
```

## 快速开始

### 1. 运行开发版本

```bash
cd src
python3 app.py
```

桌面图形界面将直接打开。

### 2. 打包为可执行文件

```bash
./build.sh
```

构建完成后，会在当前目录生成 `bag_parser` 可执行文件。

运行：
```bash
./bag_parser
```

## 配置说明

编辑 `src/config.py` 可配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `TOPIC_EXCLUDE_KEYWORDS` | 排除包含这些关键词的 topic（大小写不敏感） | `["image"]` |
| `BYTE_UNPACK_TOPIC_KEYWORDS` | 匹配到的 topic 中所有 bytes 字段逐字节展开为 key_b0..bN | `["warning_status"]` |
| `TTK_STYLE` | GUI 扁平样式配置（橙+白配色） | 见 config.py |

## 核心技术

程序利用 Python 反射机制（`__slots__`、`getattr`）动态读取 ROS 消息的任意字段结构，无需预定义消息类型。

```
用户选择目录 → 扫描 .bag 文件 → 选择 topic → 消息展平 → CSV 导出
```

## 环境要求

- Python 3.8+
- rosbag（Python 包）
- tkinter（Python 标准库自带）

## 依赖安装

```bash
pip install rosbag
```
