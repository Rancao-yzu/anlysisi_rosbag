import csv
import os


def export_to_csv(topic_data, output_dir, bag_name):
    """
    将 topic 消息数据导出为 CSV 文件。

    每个 topic 生成一个独立的 CSV 文件，文件名格式: {bag_name}_{safe_topic}.csv

    参数:
        topic_data: {topic_name: [flattened_dict, ...]}
        output_dir: 输出目录路径
        bag_name:   bag 文件的名称（不含路径和扩展名）

    返回:
        list: 生成的 CSV 文件路径列表
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_paths = []

    for topic, msgs in topic_data.items():
        if not msgs:
            continue

        other_fields = []
        for msg_dict in msgs:
            for key in msg_dict:
                if key == '_time':
                    continue
                if key.startswith('header.'):
                    continue
                if key not in other_fields:
                    other_fields.append(key)
        all_fields = ['n_id', '_time'] + other_fields

        safe_topic = topic.replace("/", "_").strip("_")
        csv_path = os.path.join(output_dir, f"{bag_name}_{safe_topic}.csv")

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            for i, msg_dict in enumerate(msgs, 1):
                row = {k: v for k, v in msg_dict.items()
                        if not k.startswith('header.')}
                row = {'n_id': i, **row}
                writer.writerow(row)

        csv_paths.append(csv_path)

    return csv_paths
