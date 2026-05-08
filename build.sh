#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$PROJECT_DIR/src"
DIST_DIR="$PROJECT_DIR/dist"

echo "============================================"
echo "  Bag Parser - Build Executable"
echo "============================================"
echo ""

echo "[1/4] 清理缓存和旧构建 ..."
find "$SRC_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SRC_DIR" -name "*.pyc" -delete 2>/dev/null || true
rm -rf "$DIST_DIR" "$PROJECT_DIR/build" "$SRC_DIR/server.spec" 2>/dev/null || true
echo "      清理完成"

echo "[2/4] 检查环境 ..."
python3 --version

echo "[3/4] 构建可执行文件 ..."
EXCLUDES=(
    # GUI / 图形
    PySide2 PySide6 PyQt5 PyQt6 PyQt6_sip sip PyQt5_sip
    tkinter customtkinter ttkbootstrap darkdetect
    PyGObject pycairo PyICU PyOpenGL
    matplotlib matplotlib_inline cycler kiwisolver

    # ROS GUI 工具
    rviz rqt_action rqt_bag rqt_bag_plugins rqt_console rqt_dep rqt_graph
    rqt_gui rqt_gui_py rqt_image_view rqt_launch rqt_logger_level
    rqt_moveit rqt_msg rqt_nav_view rqt_plot rqt_pose_view rqt_publisher
    rqt_py_common rqt_py_console rqt_reconfigure rqt_robot_dashboard
    rqt_robot_monitor rqt_robot_steering rqt_runtime_monitor rqt_rviz
    rqt_service_caller rqt_shell rqt_srv rqt_tf_tree rqt_top rqt_topic
    rqt_web qt_dotgraph qt_gui qt_gui_cpp qt_gui_py_common python_qt_binding
    joint_state_publisher joint_state_publisher_gui nicegui vbuild

    # Jupyter / IPython
    jupyter jupyter_client jupyter_console jupyter_core jupyter_events
    jupyter_lsp jupyter_server jupyter_server_terminals jupyterlab
    jupyterlab_pygments jupyterlab_server jupyterlab_widgets
    notebook notebook_shim nbclient nbconvert nbformat nbclassic
    ipykernel ipython ipywidgets widgetsnbextension
    traitlets jedi parso pickleshare backcall stack_data
    debugpy pyzmq terminado Send2Trash
    argon2_cffi argon2_cffi_bindings prometheus_client
    mistune pandocfilters tinycss2 comm
    pure_eval executing asttokens decorator

    # 科学计算 / 数据处理
    numpy scipy scikit_learn pandas pillow
    joblib threadpoolctl openpyxl et_xmlfile
    sensor_msgs

    # 其他 Web 框架/服务
    aiohttp aiofiles aiohappyeyeballs aiosignal frozenlist multidict yarl
    async_timeout propcache
    uvicorn uvloop starlette fastapi pydantic pydantic_core
    httpx httpcore httptools anyio sniffio h11
    tornado Twisted txaio autobahn hyperlink constantly zope_interface
    websockets websocket_client simple_websocket wsproto wsaccel
    nicegui vbuild simplejson

    # ORM / DB / 网络
    sqlalchemy psycopg2 pymysql redis hiredis
    paramiko pycrypto pycryptodomex PyNaCl bcrypt
    cryptography cffi pycparser
    SecretStorage keyring jeepney
    openai orjson diskcache

    # 测试
    pytest pytest_cov coverage cov_core nose nose2 mock
    pluggy iniconfig tomli py

    # 构建 / 打包
    pip setuptools wheel distlib
    pyinstaller pyinstaller_hooks_contrib altgraph pyelftools
    Nuitka meson

    # 杂项大库
    grpcio protobuf
    lxml beautifulsoup4 soupsieve
    pydot
    markdown_it_py markdown2 mdit_py_plugins mdurl rich
    mpi4py
    pydocstyle pycodestyle pyflakes flake8 mccabe snowballstemmer
    bandit
    pylint astroid
    scp
    Cython
    line_profiler line_profiler_pycharm
)

EXCLUDE_ARGS=""
for mod in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude-module $mod"
done

pyinstaller \
    --onefile \
    --name bag_parser_server \
    --add-data "$SRC_DIR/templates:templates" \
    --add-data "$SRC_DIR/static:static" \
    --add-data "$SRC_DIR/bag_parser:bag_parser" \
    --add-data "$SRC_DIR/config.py:." \
    --hidden-import rosbag \
    --exclude-module pkg_resources \
    --exclude-module jaraco \
    --exclude-module jaraco.text \
    --exclude-module jaraco.functools \
    --exclude-module jaraco.context \
    $EXCLUDE_ARGS \
    --clean \
    "$SRC_DIR/server.py"

echo ""
echo "[4/4] 复制可执行文件 ..."
chmod +x "$DIST_DIR/bag_parser_server"
cp "$DIST_DIR/bag_parser_server" "$PROJECT_DIR/bag_parser_server"

echo ""
echo "============================================"
echo "  构建完成!"
echo "  可执行文件: bag_parser_server"
echo "  大小: $(du -h "$PROJECT_DIR/bag_parser_server" | cut -f1)"
echo ""
echo "  使用方式:"
echo "    ./bag_parser_server"
echo "    (服务启动后访问 http://127.0.0.1:5000)"
echo "============================================"