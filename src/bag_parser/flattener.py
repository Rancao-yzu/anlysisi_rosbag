"""ROS 消息递归展平模块。

通过 Python 反射机制（__slots__、getattr）遍历任意 ROS 消息的字段结构，
将嵌套的自定义消息类型递归展平为单层字典，无需预定义消息 schema。
"""


def _round_val(val, decimals=6):
    """浮点数保留指定小数位，非浮点数原样返回"""
    if isinstance(val, float):
        return round(val, decimals)
    return val


def flatten_msg(msg, prefix="", unpack_all_bytes=False):
    """
    将任意 ROS 消息递归展平为扁平的键值字典。

    处理规则：
        - 基本类型（int/float/str/bool）：直接保留值，浮点数保留最多 6 位小数
        - 时间类型（有 secs/nsecs 属性）：转为浮点秒数
        - 嵌套消息（有 __slots__）：递归展平，key 用 . 连接
        - 数组/列表：逐个展平或逗号拼接
        - bytes：普通模式跳过，逐字节模式展开为 b0..bN

    参数:
        msg:              ROS 消息对象
        prefix:           字段名前缀（递归时逐层追加）
        unpack_all_bytes: 是否将所有 bytes/list[int] 逐字节展开

    返回:
        dict: 展平后的字段字典
    """
    result = {}

    # 通过 __slots__ 获取消息的所有字段名，无需预知消息类型
    slots = msg.__slots__

    for slot_name in slots:
        key = f"{prefix}{slot_name}" if prefix else slot_name
        value = getattr(msg, slot_name)

        # 逐字节展开模式：将 bytes 或 list[int] 的每个元素作为独立列
        if unpack_all_bytes:
            if isinstance(value, bytes):
                for i, b in enumerate(value):
                    result[f"{key}_b{i}"] = b
                continue
            elif isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], int):
                for i, b in enumerate(value):
                    result[f"{key}_b{i}"] = b
                continue

        # ROS 时间类型：secs + nsecs → 浮点秒
        if hasattr(value, 'secs') and hasattr(value, 'nsecs'):
            result[key] = value.secs + value.nsecs * 1e-9

        # 嵌套的自定义消息类型：递归展平
        elif hasattr(value, '__slots__'):
            nested = flatten_msg(value, prefix=key + ".",
                                 unpack_all_bytes=unpack_all_bytes)
            result.update(nested)

        # 列表/元组：递归处理每个元素或逗号拼接
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                result[key] = ""
            elif hasattr(value[0], '__slots__'):
                for i, item in enumerate(value):
                    nested = flatten_msg(item, prefix=f"{key}[{i}].",
                                         unpack_all_bytes=unpack_all_bytes)
                    result.update(nested)
            else:
                result[key] = ", ".join(
                    str(_round_val(v)) for v in value)
        else:
            result[key] = _round_val(value)

    return result
