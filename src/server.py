import os
import sys

from flask import Flask, request, jsonify, render_template

base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bag_parser import get_topic_info, read_messages, export_to_csv
import config

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.getcwd()
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')

def _filter_topics(topics_info):
    exclude_keywords = getattr(config, 'TOPIC_EXCLUDE_KEYWORDS', [])
    if not exclude_keywords:
        return topics_info

    filtered = {}
    for topic, info in topics_info.items():
        if any(kw.lower() in topic.lower() for kw in exclude_keywords):
            continue
        filtered[topic] = info
    return filtered


def _get_unpack_topics(topics):
    unpack_keywords = getattr(config, 'BYTE_UNPACK_TOPIC_KEYWORDS', [])
    if not unpack_keywords:
        return set()
    return {t for t in topics if any(kw.lower() in t.lower() for kw in unpack_keywords)}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def scan_path():
    data = request.get_json()
    target_path = (data or {}).get('path', '').strip()

    if not target_path:
        return jsonify({'ok': False, 'error': '路径不能为空'}), 400

    abs_path = os.path.abspath(target_path)

    if not os.path.exists(abs_path):
        return jsonify({'ok': False, 'error': f'路径不存在: {abs_path}'}), 400

    if not os.path.isdir(abs_path):
        return jsonify({'ok': False, 'error': f'不是有效目录: {abs_path}'}), 400

    bag_files = []
    try:
        for entry in os.listdir(abs_path):
            full = os.path.join(abs_path, entry)
            if entry.endswith('.bag') and os.path.isfile(full):
                bag_files.append({
                    'name': entry,
                    'path': full,
                    'size': os.path.getsize(full)
                })
    except PermissionError:
        return jsonify({'ok': False, 'error': f'没有读取目录的权限: {abs_path}'}), 403

    bag_files.sort(key=lambda x: x['name'])

    return jsonify({
        'ok': True,
        'path': abs_path,
        'count': len(bag_files),
        'files': bag_files
    })


@app.route('/api/topics', methods=['POST'])
def list_topics():
    data = request.get_json()
    bag_path = (data or {}).get('path', '').strip()

    if not bag_path:
        return jsonify({'ok': False, 'error': 'Bag 文件路径不能为空'}), 400

    if not os.path.isfile(bag_path):
        return jsonify({'ok': False, 'error': f'文件不存在: {bag_path}'}), 400

    try:
        topics_info = get_topic_info(bag_path)
        topics_info = _filter_topics(topics_info)

        topics = []
        for topic, info in sorted(topics_info.items()):
            topics.append({
                'name': topic,
                'msg_type': info['msg_type'],
                'msg_count': info['msg_count']
            })

        return jsonify({
            'ok': True,
            'bag_path': bag_path,
            'count': len(topics),
            'topics': topics
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': f'读取 topic 失败: {str(e)}'}), 500


@app.route('/api/process', methods=['POST'])
def process_bag():
    data = request.get_json() or {}
    bag_path = data.get('path', '').strip()
    selected_topics = data.get('topics', [])
    max_msgs = data.get('max_msgs', 3)

    if not bag_path:
        return jsonify({'ok': False, 'error': 'Bag 文件路径不能为空'}), 400
    if not os.path.isfile(bag_path):
        return jsonify({'ok': False, 'error': f'文件不存在: {bag_path}'}), 400
    if not selected_topics:
        return jsonify({'ok': False, 'error': '请至少选择一个 topic'}), 400

    bag_name = os.path.splitext(os.path.basename(bag_path))[0]

    output_dir = os.path.join(DEFAULT_OUTPUT_DIR, bag_name)
    os.makedirs(output_dir, exist_ok=True)

    try:
        unpack_set = _get_unpack_topics(selected_topics)
        topic_data = read_messages(bag_path, selected_topics, max_msgs,
                                   unpack_all_bytes_topics=unpack_set)
        csv_paths = export_to_csv(topic_data, output_dir, bag_name)

        files_info = [{'name': os.path.basename(p), 'path': p} for p in csv_paths]

        return jsonify({
            'ok': True,
            'bag_name': bag_name,
            'output_dir': output_dir,
            'file_count': len(files_info),
            'files': files_info
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': f'处理失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
