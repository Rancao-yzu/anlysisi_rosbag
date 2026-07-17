"""
开发者配置文件

所有参数在此定义，修改后重启 app.py 即可生效。
"""

# 跳过包含这些关键词的 topic（大小写不敏感）
TOPIC_EXCLUDE_KEYWORDS = ["image"]

# 指定 topic 关键词，匹配到的 topic 中所有 list/bytes 字段全部逐字节展开
# （保留展开列 key_b0..bN，丢弃原始列 key）
BYTE_UNPACK_TOPIC_KEYWORDS = ["warning_status"]


# 配色方案：橙色 + 白色，扁平无渐变

TTK_STYLE = {
    # ---- 主色调 ----
    "primary":       "#FF8C00",   # 主橙色（按钮、高亮）
    "primary_hover": "#E67E00",   # 橙色悬停
    "primary_active":"#CC7000",   # 橙色按下
    "primarynone" :"#9900FF", 

    # ---- 背景 ----
    "bg":            "#FFFFFF",   # 主背景
    "bg_secondary":  "#FFF5EB",   # 次背景（浅橙色底）
    "bg_card":       "#FFFFFF",   # 卡片背景

    # ---- 文字 ----
    "fg":            "#2D2D2D",   # 主文字
    "fg_secondary":  "#6B6B6B",   # 次要文字
    "fg_muted":      "#9E9E9E",   # 弱化文字

    # ---- 边框 & 分隔 ----
    "border":        "#E0D5C7",   # 边框色（暖灰）
    "separator":     "#F0E6D6",   # 分隔线

    # ---- 功能色 ----
    "success":       "#4CAF50",   # 成功绿
    "error":         "#E53935",   # 错误红
    "warning":       "#FF9800",   # 警告橙

    # ---- 字体 ----
    "font_family":   "Microsoft YaHei",
    "font_size":     10,
    "font_size_sm":  9,
    "font_size_lg":  14,
}


def apply_flat_style(style=None):
    """从 TTK_STYLE 读取配色并应用到 ttk，返回 (style_dict, ttk.Style)。

    参数:
        style: 可选，已有的 ttk.Style 实例（复用则不再 new）

    返回:
        (dict, ttk.Style)
    """
    from tkinter import ttk

    s = TTK_STYLE
    if style is None:
        style = ttk.Style()
    style.theme_use('clam')  # 扁平主题，无渐变

    font = (s["font_family"], s["font_size"])
    font_sm = (s["font_family"], s["font_size_sm"])

    # ---- 通用 ----
    style.configure('.',
                    background=s["bg"],
                    foreground=s["fg"],
                    font=font,
                    borderwidth=0,
                    relief='flat')

    # ---- 标签 ----
    style.configure('TLabel',
                    background=s["bg"],
                    foreground=s["fg"],
                    font=font)
    style.configure('Title.TLabel',
                    background=s["bg"],
                    foreground=s["primary"],
                    font=(s["font_family"], 24, 'bold'))
    style.configure('Muted.TLabel',
                    background=s["bg"],
                    foreground=s["fg_muted"],
                    font=font_sm)

    # ---- 按钮 ----
    style.configure('TButton',
                    background=s["primary"],
                    foreground="#FFFFFF",
                    borderwidth=0,
                    relief='flat',
                    padding=(16, 8),
                    font=font)
    style.map('TButton',
              background=[('active', s["primary_hover"]),
                          ('disabled', s["border"])],
              foreground=[('disabled', s["fg_muted"])])

    style.configure('Outline.TButton',
                    background=s["bg_secondary"],
                    foreground=s["primary"],
                    borderwidth=0,
                    relief='flat',
                    padding=(10, 4),
                    font=font_sm)
    style.map('Outline.TButton',
              background=[('active', s["bg"]),
                          ('disabled', s["bg"])])

    style.configure('Primary.TButton',
                    background=s["primary"],
                    foreground="#FFFFFF",
                    borderwidth=0,
                    relief='flat',
                    padding=(24, 10),
                    font=font)
    style.map('Primary.TButton',
              background=[('active', s["primary_hover"]),
                          ('disabled', s["border"])])

    # ---- Checkbutton ----
    style.configure('TCheckbutton',
                    background=s["bg"],
                    foreground=s["fg"],
                    font=font,
                    padding=(4, 2))
    style.map('TCheckbutton',
              background=[('active', s["bg_secondary"])],
              foreground=[('selected', s["primary"])])

    # ---- Treeview (文件/结果列表) ----
    style.configure('Treeview',
                    background=s["bg"],
                    foreground=s["fg"],
                    fieldbackground=s["bg"],
                    borderwidth=0,
                    rowheight=30)
    style.configure('Treeview.Heading',
                    background=s["bg_secondary"],
                    foreground=s["primary"],
                    font=(s["font_family"], s["font_size_sm"], 'bold'),
                    borderwidth=0,
                    padding=(8, 4))
    style.map('Treeview',
              background=[('selected', s["bg_secondary"])],
              foreground=[('selected', s["fg"])])


    return s, style
