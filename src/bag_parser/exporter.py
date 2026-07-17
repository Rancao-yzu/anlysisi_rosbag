"""CSV 导出模块。

将展平后的 topic 消息数据按 topic 分别导出为 CSV 文件，
自动排除 header.* 和 layout.* 等冗余字段。
"""
import csv
import os


def _is_zero_or_null(val):
    """判断值是否为零或空（0, 0.0, None, ''）"""
    if val is None:
        return True
    if isinstance(val, (int, float)) and val == 0:
        return True
    return False


def export_to_csv(topic_data, output_dir, bag_name, drop_zero_cols=False, zero_check_rows=100):
    """
    将 topic 消息数据导出为 CSV 文件。

    每个 topic 生成一个独立的 CSV 文件，文件名格式: {bag_name}_{safe_topic}.csv
    CSV 列顺序: n_id, _time, ... (其他字段按出现顺序排列)

    参数:
        topic_data:      {topic_name: [flattened_dict, ...]}
        output_dir:      输出目录路径
        bag_name:        bag 文件的名称（不含路径和扩展名）
        drop_zero_cols:  是否丢弃前 zero_check_rows 条全为零/None 的列
        zero_check_rows: 检测零列时检查的行数（默认 100）

    返回:
        list: 生成的 CSV 文件路径列表
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_paths = []

    for topic, msgs in topic_data.items():
        if not msgs:
            continue

        # 收集所有字段名（排除 _time、header.*、layout.*）
        other_fields = []
        for msg_dict in msgs:
            for key in msg_dict:
                if key == '_time':
                    continue
                if key.startswith('header.'):
                    continue
                if key.startswith('layout.'):
                    continue
                if key not in other_fields:
                    other_fields.append(key)

        # ---- 丢弃全零列：检查前 zero_check_rows 条 ----
        drop_fields = set()
        if drop_zero_cols and msgs:
            check_count = min(len(msgs), zero_check_rows)
            for field in other_fields:
                all_zero = True
                for i in range(check_count):
                    val = msgs[i].get(field)
                    if not _is_zero_or_null(val):
                        all_zero = False
                        break
                if all_zero:
                    drop_fields.add(field)

        # 过滤掉被丢弃的列
        kept_fields = [f for f in other_fields if f not in drop_fields]
        all_fields = ['n_id', '_time'] + kept_fields

        # 生成安全的文件名：替换 / 为 _
        safe_topic = topic.replace("/", "_").strip("_")
        csv_path = os.path.join(output_dir, f"{bag_name}_{safe_topic}.csv")

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
            writer.writeheader()
            for i, msg_dict in enumerate(msgs, 1):
                # 过滤掉 header.*、layout.* 以及被丢弃的零列
                row = {k: v for k, v in msg_dict.items()
                        if not k.startswith('header.')
                        and not k.startswith('layout.')
                        and k not in drop_fields}
                row = {'n_id': i, **row}
                writer.writerow(row)

        csv_paths.append(csv_path)

    return csv_paths
