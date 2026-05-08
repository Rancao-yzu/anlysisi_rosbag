(function () {
    'use strict';

    const $ = function (sel) { return document.querySelector(sel); };
    const $$ = function (sel) { return document.querySelectorAll(sel); };

    const state = {
        scannedPath: '',
        bagFiles: [],
        selectedBag: null,
        topics: [],
        selectedTopics: new Set(),
        resultFiles: []
    };

    function showLoading(text) {
        $('#loading-text').textContent = text || '处理中...';
        $('#loading-overlay').style.display = 'flex';
    }

    function hideLoading() {
        $('#loading-overlay').style.display = 'none';
    }

    function showToast(message, type) {
        var toast = $('#toast');
        toast.textContent = message;
        toast.className = 'toast ' + (type || 'error') + ' show';
        clearTimeout(toast._timer);
        toast._timer = setTimeout(function () {
            toast.classList.remove('show');
        }, 3500);
    }

    async function apiPost(url, body) {
        var resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        var data = await resp.json();
        if (!resp.ok || !data.ok) {
            throw new Error(data.error || '请求失败');
        }
        return data;
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    }

    // ========== 第一步：扫描路径 ==========

    $('#btn-scan').addEventListener('click', async function () {
        var path = $('#path-input').value.trim();
        if (!path) {
            showToast('请输入目录路径', 'warning');
            return;
        }

        var btn = $('#btn-scan');
        btn.disabled = true;
        btn.querySelector('span').textContent = '扫描中...';
        showLoading('正在扫描目录...');

        try {
            var data = await apiPost('/api/scan', { path: path });
            state.scannedPath = data.path;
            state.bagFiles = data.files;
            state.selectedBag = null;
            state.topics = [];
            state.selectedTopics.clear();
            state.resultFiles = [];

            hideSection('section-files');
            hideSection('section-topics');
            hideSection('section-result');

            if (data.files.length === 0) {
                $('#path-hint').innerHTML = '<span style="color:#f59e0b;">⚠ 该目录下没有找到 .bag 文件</span>';
                showToast('该目录下没有 .bag 文件', 'warning');
            } else {
                $('#path-hint').innerHTML =
                    '<span style="color:#22c55e;">✓ 扫描完成，发现 <b>' + data.count + '</b> 个 bag 文件</span>';
                renderFileList(data.files);
                showSection('section-files');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.querySelector('span').textContent = '扫描';
            hideLoading();
        }
    });

    $('#path-input').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            $('#btn-scan').click();
        }
    });

    function renderFileList(files) {
        var container = $('#file-list');
        container.innerHTML = '';

        files.forEach(function (file) {
            var div = document.createElement('div');
            div.className = 'file-item';
            div.innerHTML =
                '<span class="file-name">' + escapeHtml(file.name) + '</span>' +
                '<span class="file-size">' + formatSize(file.size) + '</span>';
            div.addEventListener('click', function () {
                selectBagFile(file, div);
            });
            container.appendChild(div);
        });

        $('#files-info').textContent = '共 ' + files.length + ' 个 bag 文件，请点击选择一个';
    }

    async function selectBagFile(file, element) {
        $$('.file-item').forEach(function (el) { el.classList.remove('selected'); });
        element.classList.add('selected');
        state.selectedBag = file;
        state.topics = [];
        state.selectedTopics.clear();
        state.resultFiles = [];
        hideSection('section-topics');
        hideSection('section-result');

        showLoading('正在读取 topic 列表...');

        try {
            var data = await apiPost('/api/topics', { path: file.path });
            state.topics = data.topics;

            if (data.topics.length === 0) {
                showToast('该 bag 文件中没有 topic（或被过滤规则全部排除）', 'warning');
            } else {
                state.selectedTopics = new Set(data.topics.map(function (t) { return t.name; }));
                renderTopicList(data.topics);
                showSection('section-topics');
                $('#topics-info').textContent =
                    'Bag: ' + file.name + ' | ' + data.count + ' 个 topic';
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // ========== 第三步：Topic 选择 ==========

    function renderTopicList(topics) {
        var container = $('#topic-list');
        container.innerHTML = '';

        topics.forEach(function (topic) {
            var div = document.createElement('div');
            div.className = 'topic-item';
            div.innerHTML =
                '<input type="checkbox" checked data-topic="' + escapeHtml(topic.name) + '">' +
                '<span class="topic-name">' + escapeHtml(topic.name) + '</span>' +
                '<span class="topic-type">' + escapeHtml(topic.msg_type) + '</span>' +
                '<span class="topic-count">' + topic.msg_count + ' 条</span>';

            var checkbox = div.querySelector('input');
            checkbox.addEventListener('change', function () {
                if (checkbox.checked) {
                    state.selectedTopics.add(topic.name);
                } else {
                    state.selectedTopics.delete(topic.name);
                }
                updateProcessButton();
            });

            container.appendChild(div);
        });

        updateProcessButton();
    }

    function updateProcessButton() {
        var btn = $('#btn-process');
        btn.disabled = state.selectedTopics.size === 0;
    }

    $('#btn-select-all').addEventListener('click', function () {
        state.selectedTopics = new Set(state.topics.map(function (t) { return t.name; }));
        $$('.topic-item input[type="checkbox"]').forEach(function (cb) {
            cb.checked = true;
        });
        updateProcessButton();
    });

    $('#btn-deselect-all').addEventListener('click', function () {
        state.selectedTopics.clear();
        $$('.topic-item input[type="checkbox"]').forEach(function (cb) {
            cb.checked = false;
        });
        updateProcessButton();
    });

    // ========== 处理导出 ==========

    $('#btn-process').addEventListener('click', async function () {
        if (!state.selectedBag) {
            showToast('请先选择一个 bag 文件', 'warning');
            return;
        }
        if (state.selectedTopics.size === 0) {
            showToast('请至少选择一个 topic', 'warning');
            return;
        }

        var exportAll = $('#export-all').checked;
        var maxMsgs = exportAll ? -1 : (parseInt($('#max-msgs').value, 10) || 3);
        if (maxMsgs > 1000) maxMsgs = 1000;

        var btn = $('#btn-process');
        btn.disabled = true;
        btn.querySelector('span').textContent = '处理中...';
        showLoading('正在解析 bag 文件并导出 CSV...');
        hideSection('section-result');

        try {
            var data = await apiPost('/api/process', {
                path: state.selectedBag.path,
                topics: Array.from(state.selectedTopics),
                max_msgs: maxMsgs
            });

            state.resultFiles = data.files;
            renderResults(data);
            showSection('section-result');

            var scrollTarget = $('#section-result');
            if (scrollTarget) {
                scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            showToast('导出完成！共生成 ' + data.file_count + ' 个 CSV 文件', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.querySelector('span').textContent = '开始处理导出';
            hideLoading();
        }
    });

    function renderResults(data) {
        var html = '<div>✓ 处理完成</div>';
        html += '<div>Bag: ' + escapeHtml(data.bag_name) + '</div>';
        html += '<div>输出目录: ' + escapeHtml(data.output_dir) + '</div>';
        html += '<div>共 ' + data.file_count + ' 个 CSV 文件</div>';
        $('#result-info').innerHTML = html;

        var container = $('#result-files');
        container.innerHTML = '';

        data.files.forEach(function (file) {
            var div = document.createElement('div');
            div.className = 'result-file-item';
            div.innerHTML =
                '<span class="csv-name">' + escapeHtml(file.name) + '</span>';
            container.appendChild(div);
        });
    }

    // ========== UI 辅助 ==========

    var stepMap = {
        'section-path': 1,
        'section-files': 2,
        'section-topics': 3,
        'section-result': 4
    };

    function updateSteps() {
        var maxVisible = 0;
        var sections = ['section-path', 'section-files', 'section-topics', 'section-result'];
        sections.forEach(function (id) {
            var el = $('#' + id);
            if (el && el.style.display !== 'none') {
                var step = stepMap[id];
                if (step > maxVisible) maxVisible = step;
            }
        });

        for (var i = 1; i <= 4; i++) {
            var indicator = document.querySelector('.step-indicator[data-step="' + i + '"]');
            var line = indicator && indicator.nextElementSibling;
            if (!indicator) continue;

            indicator.classList.remove('active', 'done');

            if (i < maxVisible) {
                indicator.classList.add('done');
                if (line && line.classList.contains('step-line')) {
                    line.classList.add('done');
                }
            } else if (i === maxVisible) {
                indicator.classList.add('active');
                if (line && line.classList.contains('step-line')) {
                    line.classList.remove('done');
                }
            } else {
                if (line && line.classList.contains('step-line')) {
                    line.classList.remove('done');
                }
            }
        }
    }

    function showSection(id) {
        var el = $('#' + id);
        if (el) el.style.display = '';
        updateSteps();
    }

    function hideSection(id) {
        var el = $('#' + id);
        if (el) el.style.display = 'none';
        updateSteps();
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // ========== 初始化：自动填入默认路径 ==========

    (function init() {
        $('#path-input').value = '';
        $('#path-hint').textContent = '提示：请输入包含 .bag 文件的目录绝对路径';

        $('#export-all').addEventListener('change', function () {
            var checked = this.checked;
            $('#max-msgs').disabled = checked;
        });

        updateSteps();
    })();

})();
