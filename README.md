# ROS Bag Parser

一个用于解析 ROS bag 文件并导出 CSV 的 Web 工具。

## 功能特性

- **动态解析**：无需预先了解 bag 文件内容，可解析任意类型的 ROS bag
- **Web 界面**：通过浏览器选择 bag 文件、查看 topic、选择导出项
- **灵活配置**：所有参数可在 `config.py` 中自定义设置
- **一键打包**：提供 `build.sh` 脚本，可打包为独立可执行文件

## 项目结构

```
anlysisi_rosbag/
├── src/
│   ├── bag_parser/        # 核心解析模块
│   │   ├── core.py       # bag 读取、topic 信息获取
│   │   ├── flattener.py  # 消息展平（解析任意消息结构）
│   │   └── exporter.py   # CSV 导出
│   ├── static/           # 前端静态资源
│   │   ├── app.js        # 交互逻辑
│   │   └── style.css     # 样式
│   ├── templates/
│   │   └── index.html    # 页面模板
│   ├── config.py         # 配置文件
│   └── server.py         # Flask 服务入口
├── build.sh              # 打包脚本
└── README.md
```

## 快速开始

### 1. 运行开发版本

```bash
cd src
python3 server.py
```

然后访问 http://127.0.0.1:5000

### 2. 打包为可执行文件

```bash
./build.sh
```

构建完成后，会在当前目录生成 `bag_parser_server` 可执行文件。

运行：
```bash
./bag_parser_server
```

## 配置说明

编辑 `src/config.py` 可配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `TOPIC_EXCLUDE_KEYWORDS` | 排除包含这些关键词的 topic（大小写不敏感） | `["image"]` |
| `BYTE_UNPACK_TOPIC_KEYWORDS` | 匹配到的 topic 中所有 bytes 字段逐字节展开为 key_b0..bN | `["warning_status"]` |

## 核心技术

程序利用 Python 反射机制（`__slots__`、`getattr`）动态读取 ROS 消息的任意字段结构，无需预定义消息类型。

```
用户选择 bag → rosbag 获取 topic 列表 → 读取消息 → 动态展平 → CSV
```

## 环境要求

- Python 3.8
- rosbag（Python 包）
- Flask

## 依赖安装

```bash
pip install rosbag flask
```
