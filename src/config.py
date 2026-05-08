"""
开发者配置文件

所有参数在此定义，修改后重启 server.py 即可生效。
"""

# 跳过包含这些关键词的 topic（大小写不敏感）
TOPIC_EXCLUDE_KEYWORDS = ["image"]

# 指定 topic 关键词，匹配到的 topic 中所有 list/bytes 字段全部逐字节展开
# （保留展开列 key_b0..bN，丢弃原始列 key）
BYTE_UNPACK_TOPIC_KEYWORDS = ["warning_status"]
