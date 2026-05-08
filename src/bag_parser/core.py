"""Bag 文件读取与 Topic 信息获取。

通过 rosbag 库动态读取任意 ROS Bag 文件，无需预知消息类型。
"""
import os
import rosbag

from .flattener import flatten_msg


def get_topic_info(bag_path):
    """
    获取 bag 文件中所有 topic 的信息。

    返回:
        dict: {topic_name: {'msg_type': str, 'msg_count': int}}
    """
    bag = rosbag.Bag(bag_path)
    info = bag.get_type_and_topic_info()
    bag.close()

    topics_info = info.topics
    result = {}

    for topic, topic_info in sorted(topics_info.items()):
        msg_type = topic_info.msg_type if hasattr(topic_info, 'msg_type') else topic_info[0]
        msg_count = topic_info.message_count if hasattr(topic_info, 'message_count') else topic_info[1]
        result[topic] = {'msg_type': msg_type, 'msg_count': msg_count}

    return result


def read_messages(bag_path, topics, max_per_topic=3,
                  unpack_all_bytes_topics=None):
    """
    从 bag 文件中读取指定 topic 的消息（每个 topic 最多 max_per_topic 条）。

    参数:
        bag_path:  bag 文件路径
        topics:    要读取的 topic 名称列表
        max_per_topic: 每个 topic 最多读取的消息数（0 表示不限制）
        unpack_all_bytes_topics: 需要全量逐字节展开的 topic 名集合

    返回:
        dict: {topic_name: [flattened_dict, ...]}
    """
    from collections import defaultdict

    unpack_set = set(unpack_all_bytes_topics or [])
    topic_msgs = defaultdict(list)
    topic_set = set(topics)

    bag = rosbag.Bag(bag_path)

    for topic, msg, t in bag.read_messages(topics=topics):
        if topic not in topic_set:
            continue

        # 达到单 topic 上限后，若所有 topic 都已满足则提前退出遍历
        if max_per_topic > 0 and len(topic_msgs[topic]) >= max_per_topic:
            if all(len(topic_msgs[t]) >= max_per_topic for t in topics):
                break
            continue

        # 根据配置决定是否对该 topic 逐字节展开
        use_unpack_all = topic in unpack_set
        flat_msg = flatten_msg(msg, unpack_all_bytes=use_unpack_all)
        flat_msg['_time'] = t.to_sec()
        topic_msgs[topic].append(flat_msg)

    bag.close()
    return dict(topic_msgs)


def find_bag_files(directory, pattern=".bag"):
    """
    在指定目录下查找所有匹配的 bag 文件。

    返回:
        list: 排序后的 bag 文件路径列表
    """
    files = [f for f in os.listdir(directory) if f.endswith(pattern)]
    return sorted([os.path.join(directory, f) for f in files])
