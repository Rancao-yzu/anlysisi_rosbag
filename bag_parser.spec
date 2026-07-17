# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/zjh/桌面/anlysisi_rosbag/src/app.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/zjh/桌面/anlysisi_rosbag/src/bag_parser', 'bag_parser'), ('/home/zjh/桌面/anlysisi_rosbag/src/config.py', '.')],
    hiddenimports=['rosbag', 'tkinter', 'tkinter.ttk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources', 'jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.context', 'PySide2', 'PySide6', 'PyQt5', 'PyQt6', 'PyQt6_sip', 'sip', 'PyQt5_sip', 'customtkinter', 'ttkbootstrap', 'darkdetect', 'PyGObject', 'pycairo', 'PyICU', 'PyOpenGL', 'matplotlib', 'matplotlib_inline', 'cycler', 'kiwisolver', 'rviz', 'rqt_action', 'rqt_bag', 'rqt_bag_plugins', 'rqt_console', 'rqt_dep', 'rqt_graph', 'rqt_gui', 'rqt_gui_py', 'rqt_image_view', 'rqt_launch', 'rqt_logger_level', 'rqt_moveit', 'rqt_msg', 'rqt_nav_view', 'rqt_plot', 'rqt_pose_view', 'rqt_publisher', 'rqt_py_common', 'rqt_py_console', 'rqt_reconfigure', 'rqt_robot_dashboard', 'rqt_robot_monitor', 'rqt_robot_steering', 'rqt_runtime_monitor', 'rqt_rviz', 'rqt_service_caller', 'rqt_shell', 'rqt_srv', 'rqt_tf_tree', 'rqt_top', 'rqt_topic', 'rqt_web', 'qt_dotgraph', 'qt_gui', 'qt_gui_cpp', 'qt_gui_py_common', 'python_qt_binding', 'joint_state_publisher', 'joint_state_publisher_gui', 'nicegui', 'vbuild', 'jupyter', 'jupyter_client', 'jupyter_console', 'jupyter_core', 'jupyter_events', 'jupyter_lsp', 'jupyter_server', 'jupyter_server_terminals', 'jupyterlab', 'jupyterlab_pygments', 'jupyterlab_server', 'jupyterlab_widgets', 'notebook', 'notebook_shim', 'nbclient', 'nbconvert', 'nbformat', 'nbclassic', 'ipykernel', 'ipython', 'ipywidgets', 'widgetsnbextension', 'traitlets', 'jedi', 'parso', 'pickleshare', 'backcall', 'stack_data', 'debugpy', 'pyzmq', 'terminado', 'Send2Trash', 'argon2_cffi', 'argon2_cffi_bindings', 'prometheus_client', 'mistune', 'pandocfilters', 'tinycss2', 'comm', 'pure_eval', 'executing', 'asttokens', 'decorator', 'numpy', 'scipy', 'scikit_learn', 'pandas', 'pillow', 'joblib', 'threadpoolctl', 'openpyxl', 'et_xmlfile', 'sensor_msgs', 'aiohttp', 'aiofiles', 'aiohappyeyeballs', 'aiosignal', 'frozenlist', 'multidict', 'yarl', 'async_timeout', 'propcache', 'uvicorn', 'uvloop', 'starlette', 'fastapi', 'pydantic', 'pydantic_core', 'httpx', 'httpcore', 'httptools', 'anyio', 'sniffio', 'h11', 'tornado', 'Twisted', 'txaio', 'autobahn', 'hyperlink', 'constantly', 'zope_interface', 'websockets', 'websocket_client', 'simple_websocket', 'wsproto', 'wsaccel', 'nicegui', 'vbuild', 'simplejson', 'sqlalchemy', 'psycopg2', 'pymysql', 'redis', 'hiredis', 'paramiko', 'pycrypto', 'pycryptodomex', 'PyNaCl', 'bcrypt', 'cryptography', 'cffi', 'pycparser', 'SecretStorage', 'keyring', 'jeepney', 'openai', 'orjson', 'diskcache', 'pytest', 'pytest_cov', 'coverage', 'cov_core', 'nose', 'nose2', 'mock', 'pluggy', 'iniconfig', 'tomli', 'py', 'pip', 'setuptools', 'wheel', 'distlib', 'pyinstaller', 'pyinstaller_hooks_contrib', 'altgraph', 'pyelftools', 'Nuitka', 'meson', 'grpcio', 'protobuf', 'lxml', 'beautifulsoup4', 'soupsieve', 'pydot', 'markdown_it_py', 'markdown2', 'mdit_py_plugins', 'mdurl', 'rich', 'mpi4py', 'pydocstyle', 'pycodestyle', 'pyflakes', 'flake8', 'mccabe', 'snowballstemmer', 'bandit', 'pylint', 'astroid', 'scp', 'Cython', 'line_profiler', 'line_profiler_pycharm'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bag_parser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
