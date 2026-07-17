"""Bag Parser - 桌面版 (ttk)

提供 ttk 图形界面用于浏览 bag 文件、选择 topic 并导出为 CSV。
扁平化设计，配色：橙色 + 白色。
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 确保能导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bag_parser import get_topic_info, read_messages, export_to_csv
import config


def _filter_topics(topics_info):
    """根据 config.TOPIC_EXCLUDE_KEYWORDS 过滤 topic，大小写不敏感匹配"""
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
    """根据 config.BYTE_UNPACK_TOPIC_KEYWORDS 匹配需要逐字节展开的 topic"""
    unpack_keywords = getattr(config, 'BYTE_UNPACK_TOPIC_KEYWORDS', [])
    if not unpack_keywords:
        return set()
    return {t for t in topics if any(kw.lower() in t.lower() for kw in unpack_keywords)}


def _format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# ======================== 主界面 ========================

class BagParserApp:
    """Bag Parser 桌面应用主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("𝓑𝓪𝓰  𝓟𝓪𝓻𝓼𝓮𝓻 𝓥1.2")
        self.root.geometry("960x740")
        self.root.minsize(800, 600)
        self.root.configure(bg=config.TTK_STYLE["bg"])

        # 应用状态
        self.scanned_path = ""
        self.bag_files = []
        self.selected_bag = None
        self.topics = []
        self.topic_vars = {}       # topic_name -> tk.BooleanVar
        self.result_files = []
        self._processing = False

        # 应用样式（从 config.py）
        self._s, self._style = config.apply_flat_style()
        self._build_ui()

    # ==================== UI 构建 ====================

    def _build_ui(self):
        """构建完整界面"""
        c = config.TTK_STYLE

        # ===== Header =====
        header = tk.Frame(self.root, bg=c["bg_secondary"], height=65)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)  # 固定高度
        
        # 左侧区域
        left_frame = tk.Frame(header, bg=c["bg_secondary"])
        left_frame.pack(side='left', padx=38)
        
        # 图标 + 标题
        tk.Label(left_frame, text="𝓑𝓪𝓰  𝓟𝓪𝓻𝓼𝓮𝓻  𝓥 1.2 ", bg=c["bg_secondary"], 
                fg=c["primarynone"], font=(c["font_family"], 24, 'bold')).pack(side='left')
        

        right_frame = tk.Frame(header, bg=c["bg_secondary"])
        right_frame.pack(side='right', padx=20)
        
        tk.Label(right_frame, text="© 𝓦𝓮𝓲𝓯𝓾 𝓩𝓱𝓲𝓰𝓪𝓷（𝓦𝓾𝔁𝓲）𝓣𝓮𝓬𝓱𝓷𝓸𝓵𝓸𝓰𝔂 𝓒𝓸., 𝓛𝓽𝓭. ", bg=c["bg_secondary"], 
                font=(c["font_family"], 18)).pack(side='right')
        
        

        # ---- 主内容区（可滚动） ----
        outer = ttk.Frame(self.root)
        outer.pack(fill='both', expand=True)

        main_canvas = tk.Canvas(outer, bg=c["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=main_canvas.yview)
        self._main_frame = ttk.Frame(main_canvas, padding=(20, 12))

        self._canvas_window = main_canvas.create_window(
            (0, 0), window=self._main_frame, anchor='nw',
            tags=('inner',))

        def _on_canvas_configure(event):
            main_canvas.itemconfig(self._canvas_window, width=event.width)

        main_canvas.bind('<Configure>', _on_canvas_configure)

        self._main_frame.bind(
            '<Configure>',
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))

        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')


        # ======== 卡片（初始只显示 Step 1） ========

        # ---- Step 1: 目录选择（始终可见） ----
        self._card1 = ttk.Frame(self._main_frame, padding=(16, 8))
        self._card1.pack(fill='x')

        ttk.Label(self._card1, text="① 𝓢𝓮𝓵𝓮𝓬𝓽 𝓑𝓪𝓰 𝓓𝓲𝓻𝓮𝓬𝓽𝓸𝓻𝔂 ",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 8))

        row1 = ttk.Frame(self._card1)
        row1.pack(fill='x')
        self._path_entry = ttk.Entry(row1)
        self._path_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self._btn_scan = ttk.Button(row1, text="浏览并扫描",
                                     command=self._scan_directory,
                                     style='Primary.TButton')
        self._btn_scan.pack(side='right')

        self._path_hint = ttk.Label(self._card1, text="", style='Muted.TLabel')
        self._path_hint.pack(anchor='w', pady=(6, 0))

        # ---- Step 2: Bag 文件列表（初始隐藏） ----
        self._card2 = ttk.Frame(self._main_frame, padding=(16, 8))

        ttk.Label(self._card2, text="② 𝓢𝓮𝓵𝓮𝓬𝓽 𝓑𝓪𝓰 𝓕𝓲𝓵𝓮 ",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 8))

        self._files_info = ttk.Label(self._card2, text="", style='Muted.TLabel')
        self._files_info.pack(anchor='w')

        self._file_tree = ttk.Treeview(self._card2,
                                        columns=('name', 'size'),
                                        show='headings', height=6)
        self._file_tree.heading('name', text='文件名')
        self._file_tree.heading('size', text='大小')
        self._file_tree.column('name', width=400, minwidth=200)
        self._file_tree.column('size', width=100, anchor='e', minwidth=80)
        self._file_tree.pack(fill='both', expand=True, pady=(6, 0))
        self._file_tree.bind('<<TreeviewSelect>>', self._on_file_selected)

        # ---- Step 3: Topic 选择（初始隐藏） ----
        self._card3 = ttk.Frame(self._main_frame, padding=(16, 8))

        ttk.Label(self._card3, text="③  𝓢𝓮𝓵𝓮𝓬𝓽 𝓣𝓸𝓹𝓲𝓬𝓼 & 𝓟𝓻𝓸𝓬𝓮𝓼𝓼 ",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 8))

        self._topics_info = ttk.Label(self._card3, text="", style='Muted.TLabel')
        self._topics_info.pack(anchor='w')

        toolbar = ttk.Frame(self._card3)
        toolbar.pack(fill='x', pady=(6, 4))
        ttk.Button(toolbar, text="全选", command=self._select_all_topics,
                   style='Outline.TButton').pack(side='left', padx=(0, 6))
        ttk.Button(toolbar, text="取消全选", command=self._deselect_all_topics,
                   style='Outline.TButton').pack(side='left', padx=(0, 12))
        ttk.Label(toolbar, text="每条导出消息数:", style='Muted.TLabel').pack(side='left')
        self._max_msgs_var = tk.StringVar(value="3")
        self._max_msgs_entry = ttk.Entry(toolbar, textvariable=self._max_msgs_var, width=6)
        self._max_msgs_entry.pack(side='left', padx=(4, 12))
        self._export_all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="导出全部", variable=self._export_all_var,
                        command=self._toggle_export_all).pack(side='left')

        topic_outer = ttk.Frame(self._card3)
        topic_outer.pack(fill='both', expand=True, pady=(4, 0))

        self._topic_canvas = tk.Canvas(topic_outer, bg=c["bg"],
                                        highlightthickness=0, height=160)
        topic_scroll = ttk.Scrollbar(topic_outer, orient='vertical',
                                      command=self._topic_canvas.yview)
        self._topic_frame = ttk.Frame(self._topic_canvas)

        self._topic_window = self._topic_canvas.create_window(
            (0, 0), window=self._topic_frame, anchor='nw')

        def _on_topic_cw(event):
            self._topic_canvas.itemconfig(self._topic_window, width=event.width)
        self._topic_canvas.bind('<Configure>', _on_topic_cw)

        self._topic_frame.bind(
            '<Configure>',
            lambda e: self._topic_canvas.configure(
                scrollregion=self._topic_canvas.bbox('all')))
        self._topic_canvas.configure(yscrollcommand=topic_scroll.set)
        self._topic_canvas.pack(side='left', fill='both', expand=True)
        topic_scroll.pack(side='right', fill='y')

        # ---- 进度条 & 处理按钮（初始隐藏） ----
        self._action_frame = ttk.Frame(self._main_frame, padding=(0, 8))

        self._progress = ttk.Progressbar(self._action_frame, mode='determinate')
        self._progress.pack(fill='x', pady=(0, 8))

        self._progress_label = ttk.Label(self._action_frame, text="就绪",
                                          style='Muted.TLabel')
        self._progress_label.pack(anchor='center')

        self._btn_process = ttk.Button(self._action_frame, text="开始处理导出",
                                        command=self._process_bag,
                                        style='Primary.TButton')
        self._btn_process.pack(pady=(8, 0))

        # ---- Step 4: 结果（初始隐藏） ----
        self._card4 = ttk.Frame(self._main_frame, padding=(16, 8))

        ttk.Label(self._card4, text="④ 𝓡𝓮𝓼𝓾𝓵𝓽𝓼 ",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 8))

        self._result_info = ttk.Label(self._card4, text="", style='Muted.TLabel')
        self._result_info.pack(anchor='w')

        self._result_tree = ttk.Treeview(self._card4, columns=('file',),
                                          show='headings', height=4)
        self._result_tree.heading('file', text='CSV 文件')
        self._result_tree.column('file', width=500)
        self._result_tree.pack(fill='x')

    # ==================== 事件处理 ====================

    def _scan_directory(self):
        """扫描目录下的 .bag 文件"""
        path = filedialog.askdirectory(title="选择 Bag 文件所在目录")
        if not path:
            return
        abs_path = os.path.abspath(path)
        self._path_entry.delete(0, 'end')
        self._path_entry.insert(0, abs_path)

        # 清除旧状态 & 隐藏后续卡片
        self._clear_file_state()
        self._clear_topic_state()
        self._clear_result()
        self._hide_card(self._card2)
        self._hide_card(self._card3)
        self._hide_card(self._action_frame)
        self._hide_card(self._card4)

        # 扫描
        try:
            bag_files = []
            for entry in os.listdir(abs_path):
                full = os.path.join(abs_path, entry)
                if entry.endswith('.bag') and os.path.isfile(full):
                    bag_files.append({
                        'name': entry,
                        'path': full,
                        'size': os.path.getsize(full)
                    })
        except PermissionError:
            messagebox.showerror("错误", f"没有读取目录的权限: {abs_path}")
            return

        bag_files.sort(key=lambda x: x['name'])
        self.bag_files = bag_files
        self.scanned_path = abs_path

        if not bag_files:
            self._path_hint.config(text="该目录下没有找到 .bag 文件",
                                   foreground=config.TTK_STYLE["warning"])
        else:
            self._path_hint.config(
                text=f"  扫描完成，发现 {len(bag_files)} 个 bag 文件",
                foreground=config.TTK_STYLE["success"])
            self._populate_file_list(bag_files)
            self._show_card(self._card2, fill='x')

    def _populate_file_list(self, files):
        """填充文件列表"""
        self._file_tree.delete(*self._file_tree.get_children())
        for f in files:
            self._file_tree.insert('', 'end',
                                   values=(f['name'], _format_size(f['size'])))
        self._files_info.config(text=f"共 {len(files)} 个 bag 文件，请点击选择一个")

    def _on_file_selected(self, event):
        """选中某个 bag 文件时加载 topic"""
        selection = self._file_tree.selection()
        if not selection:
            return
        idx = self._file_tree.index(selection[0])
        if idx >= len(self.bag_files):
            return

        file_info = self.bag_files[idx]
        self.selected_bag = file_info
        self._clear_topic_state()
        self._clear_result()
        self._hide_card(self._card3)
        self._hide_card(self._action_frame)
        self._hide_card(self._card4)

        try:
            topics_info = get_topic_info(file_info['path'])
            topics_info = _filter_topics(topics_info)
            self.topics = [{'name': t, 'msg_type': i['msg_type'], 'msg_count': i['msg_count']}
                           for t, i in sorted(topics_info.items())]
        except Exception as e:
            messagebox.showerror("错误", f"读取 topic 失败: {e}")
            return

        if not self.topics:
            messagebox.showwarning("提示", "该 bag 文件中没有 topic（或被过滤规则全部排除）")
            return

        self._populate_topic_list(self.topics)
        self._topics_info.config(text=f"Bag: {file_info['name']} | {len(self.topics)} 个 topic",
                                 foreground=config.TTK_STYLE["fg_secondary"])
        self._show_card(self._card3, fill='both', expand=True)
        self._show_card(self._action_frame, fill='x')

    def _populate_topic_list(self, topics):
        """填充 topic 复选框列表"""
        for w in self._topic_frame.winfo_children():
            w.destroy()
        self.topic_vars.clear()

        for t in topics:
            var = tk.BooleanVar(value=True)
            self.topic_vars[t['name']] = var

            row = ttk.Frame(self._topic_frame)
            row.pack(fill='x', pady=1)
            cb = ttk.Checkbutton(row, text=t['name'], variable=var)
            cb.pack(side='left')
            ttk.Label(row, text=t['msg_type'], style='Muted.TLabel',
                      width=30, anchor='w').pack(side='left', padx=(12, 0))
            ttk.Label(row, text=f"{t['msg_count']} 条", style='Muted.TLabel',
                      width=10, anchor='e').pack(side='right')

    def _select_all_topics(self):
        for var in self.topic_vars.values():
            var.set(True)

    def _deselect_all_topics(self):
        for var in self.topic_vars.values():
            var.set(False)

    def _toggle_export_all(self):
        if self._export_all_var.get():
            self._max_msgs_entry.config(state='disabled')
        else:
            self._max_msgs_entry.config(state='normal')

    def _get_selected_topics(self):
        return [name for name, var in self.topic_vars.items() if var.get()]

    # ==================== 处理 ====================

    def _process_bag(self):
        """开始处理：读取消息 + 导出 CSV"""
        if self._processing:
            return
        if not self.selected_bag:
            messagebox.showwarning("提示", "请先选择一个 bag 文件")
            return

        selected = self._get_selected_topics()
        if not selected:
            messagebox.showwarning("提示", "请至少选择一个 topic")
            return

        export_all = self._export_all_var.get()
        try:
            max_msgs = -1 if export_all else int(self._max_msgs_var.get())
        except ValueError:
            max_msgs = 3
        if max_msgs == 0:
            max_msgs = -1

        self._processing = True
        self._btn_process.config(state='disabled', text="处理中...")
        self._clear_result()
        self._progress['value'] = 0
        self._progress_label.config(text="正在解析 bag 文件...",
                                    foreground=config.TTK_STYLE["primary"])

        # 在后台线程处理
        bag_path = self.selected_bag['path']
        bag_name = os.path.splitext(os.path.basename(bag_path))[0]

        # 打包后 sys.frozen=True，用 exe 所在目录而非 /tmp 临时目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, 'output', bag_name)

        def _run():
            try:
                unpack_set = _get_unpack_topics(selected)
                n_topics = len(selected)

                # ---- 阶段 1: 读取消息 ----
                self.root.after(0, lambda: self._progress.configure(value=10))
                self.root.after(0, lambda: self._progress_label.configure(
                    text=f"正在读取 Bag ({n_topics} 个 topic)..."))

                topic_data = read_messages(
                    bag_path, selected, max_msgs,
                    unpack_all_bytes_topics=unpack_set)

                # 统计实际读取的消息数
                total_msgs = sum(len(v) for v in topic_data.values())
                self.root.after(0, lambda: self._progress.configure(value=50))
                self.root.after(0, lambda: self._progress_label.configure(
                    text=f"读取完成 ({n_topics} 个 topic, 共 {total_msgs} 条消息)，正在导出..."))

                # ---- 阶段 2: 导出 CSV ----
                csv_paths = export_to_csv(
                    topic_data, output_dir, bag_name)

                self.result_files = csv_paths

                # 完成
                self.root.after(0, lambda: self._on_process_done(bag_name, output_dir, csv_paths))

            except Exception as e:
                self.root.after(0, lambda: self._on_process_error(str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _on_process_done(self, bag_name, output_dir, csv_paths):
        """处理完成回调"""
        self._processing = False
        self._btn_process.config(state='normal', text="  开始处理导出")
        self._progress['value'] = 100
        self._progress_label.config(text="  导出完成！",
                                    foreground=config.TTK_STYLE["success"])

        self._result_info.config(
            text=f"✓ 处理完成 | Bag: {bag_name} | 输出: {output_dir} | 共 {len(csv_paths)} 个 CSV",
            foreground=config.TTK_STYLE["success"])

        self._result_tree.delete(*self._result_tree.get_children())
        for p in csv_paths:
            self._result_tree.insert('', 'end', values=(os.path.basename(p),))

        self._show_card(self._card4, fill='x')

    def _on_process_error(self, error_msg):
        """处理失败回调"""
        self._processing = False
        self._btn_process.config(state='normal', text="  开始处理导出")
        self._progress_label.config(text=f"  处理失败: {error_msg}",
                                    foreground=config.TTK_STYLE["error"])
        messagebox.showerror("处理失败", error_msg)

    # ==================== 辅助 ====================

    @staticmethod
    def _show_card(card, **pack_kw):
        """显示卡片（如果尚未 pack）"""
        if not card.winfo_ismapped():
            card.pack(pady=(0, 12), **pack_kw)

    @staticmethod
    def _hide_card(card):
        """隐藏卡片"""
        if card.winfo_ismapped():
            card.pack_forget()

    def _clear_file_state(self):
        self.selected_bag = None
        self._file_tree.delete(*self._file_tree.get_children())
        self._files_info.config(text="")

    def _clear_topic_state(self):
        self.topics = []
        self.topic_vars.clear()
        for w in self._topic_frame.winfo_children():
            w.destroy()
        self._topics_info.config(text="")
        self._progress['value'] = 0
        self._progress_label.config(text="就绪", foreground=config.TTK_STYLE["fg_muted"])

    def _clear_result(self):
        self.result_files = []
        self._result_info.config(text="")
        self._result_tree.delete(*self._result_tree.get_children())


# ======================== 入口 ========================

if __name__ == '__main__':
    root = tk.Tk()
    app = BagParserApp(root)
    root.mainloop()
