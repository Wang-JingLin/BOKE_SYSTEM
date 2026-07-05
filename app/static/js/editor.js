// ===== editor.js — 富文本编辑器完整实现 =====

(function () {
  'use strict';

  // ---------- DOM 引用 ----------
  var editor, hiddenArea, toolbar, titleInput, inspireBlock, tocBody, tocFold;

  function init() {
    editor = document.getElementById('richtextArea');
    hiddenArea = document.getElementById('contentHidden');
    toolbar = document.getElementById('editorToolbar');
    titleInput = document.querySelector('.editor-title-input');
    inspireBlock = document.getElementById('inspireBlock');
    tocBody = document.getElementById('tocBody');
    tocFold = document.getElementById('tocFold');

    if (!editor) return;

    // 初始同步
    syncContent();

    // 点击工具栏按钮
    if (toolbar) {
      toolbar.addEventListener('click', function (e) {
        var btn = e.target.closest('.tool-btn');
        if (btn) {
          e.preventDefault();
          execTool(btn);
        }
        var toggle = e.target.closest('#mdToggle');
        if (toggle) {
          e.preventDefault();
          toggleMdMode();
        }
      });
    }

    // 编辑区输入：同步 + 字数 + 灵感
    editor.addEventListener('input', function () {
      syncContent();
      updateWordCount();
      if (inspireBlock && editor.textContent.trim().length > 0) {
        inspireBlock.style.display = 'none';
      }
    });

    // 标题输入
    if (titleInput) {
      titleInput.addEventListener('input', function () { updateTitleHint(this); });
    }

    // 格式下拉菜单
    document.addEventListener('click', function (e) {
      var dropdown = document.getElementById('headingDropdown');
      var formatBtn = document.querySelector('[data-cmd="headingMenu"]');
      if (!dropdown || !formatBtn) return;
      // 点击下拉项时应用格式（先判断，避免被格式按钮拦截）
      var item = e.target.closest('.heading-item');
      if (item && dropdown.contains(item)) {
        var tag = item.getAttribute('data-tag');
        editor.focus();
        // 方式1：尝试 execCommand
        var worked = false;
        try {
          if (tag === 'p') {
            worked = document.execCommand('formatBlock', false, '<p>');
          } else {
            worked = document.execCommand('formatBlock', false, '<' + tag + '>');
          }
        } catch (ex) {
          worked = false;
        }
        // 方式2：如果 execCommand 失败，用 wrapContent 方式
        if (!worked) {
          var sel = window.getSelection();
          if (sel.rangeCount) {
            var range = sel.getRangeAt(0);
            var selectedText = range.toString();
            if (selectedText) {
              var wrapper = document.createElement(tag);
              wrapper.appendChild(range.extractContents());
              range.insertNode(wrapper);
              // 折叠选区到末尾
              range.setStartAfter(wrapper);
              sel.removeAllRanges();
              sel.addRange(range);
            } else {
              // 无选中文字，直接插入空标签
              var wrapper = document.createElement(tag);
              wrapper.innerHTML = '<br>';
              range.insertNode(wrapper);
              var newRange = document.createRange();
              newRange.setStart(wrapper, 0);
              sel.removeAllRanges();
              sel.addRange(newRange);
            }
          }
        }
        syncContent();
        dropdown.classList.remove('show');
        editor.focus();
        return;
      }
      // 点击格式按钮时切换下拉（排除已处理的 heading-item）
      if (formatBtn.contains(e.target) || e.target.closest('[data-cmd="headingMenu"]')) {
        e.preventDefault();
        dropdown.classList.toggle('show');
        if (dropdown.classList.contains('show')) {
          var rect = formatBtn.getBoundingClientRect();
          dropdown.style.top = (rect.bottom + 4) + 'px';
          dropdown.style.left = rect.left + 'px';
          dropdown.style.minWidth = '130px';
          // 更新当前选中项的打勾标记
          updateHeadingCheckmark();
        }
        return;
      }
      // 点击外部关闭下拉
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });

    // 目录折叠
    if (tocFold) {
      tocFold.addEventListener('click', function () {
        var toc = document.getElementById('editorToc');
        if (toc) {
          var isCollapsed = toc.classList.toggle('collapsed');
          tocFold.textContent = isCollapsed ? '›' : '‹';
        }
      });
    }

    // 初始化字数
    updateWordCount();
    updateTitleHint(titleInput);

    // Ctrl+B / Ctrl+K 等快捷键
    editor.addEventListener('keydown', function (e) {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'b') { e.preventDefault(); document.execCommand('bold'); }
        if (e.key === 'i') { e.preventDefault(); document.execCommand('italic'); }
        if (e.key === 'u') { e.preventDefault(); document.execCommand('underline'); }
        if (e.key === 'k') { e.preventDefault(); insertLink(); }
        if (e.key === 'z') {
          if (e.shiftKey) { e.preventDefault(); document.execCommand('redo'); }
          else { e.preventDefault(); document.execCommand('undo'); }
        }
      }
    });
  }

  // ---------- 工具栏命令分发 ----------
  function execTool(btn) {
    var cmd = btn.getAttribute('data-cmd');
    var val = btn.getAttribute('data-val');
    if (!cmd) return;
    editor.focus();

    switch (cmd) {
      // --- 原生 execCommand ---
      case 'bold':          document.execCommand('bold'); break;
      case 'italic':        document.execCommand('italic'); break;
      case 'underline':     document.execCommand('underline'); break;
      case 'removeFormat':  document.execCommand('removeFormat'); break;
      case 'insertUnorderedList': document.execCommand('insertUnorderedList'); break;
      case 'insertOrderedList':   document.execCommand('insertOrderedList'); break;
      case 'listMenu': showListMenu(btn); break;
      case 'insertHorizontalRule': document.execCommand('insertHorizontalRule'); break;
      case 'justifyLeft':   document.execCommand('justifyLeft'); break;
      case 'justifyCenter': document.execCommand('justifyCenter'); break;
      case 'justifyRight':  document.execCommand('justifyRight'); break;
      case 'alignMenu': showAlignMenu(btn); break;
      case 'undo':          document.execCommand('undo'); break;
      case 'redo':          document.execCommand('redo'); break;
      case 'foreColor':
        var lastF = btn.getAttribute('data-last-color') || '#e53e3e';
        document.execCommand('foreColor', false, lastF);
        break;
      case 'foreColorPalette':
        // 查找同组的主按钮获取 last-color
        var mainF = btn.parentElement.querySelector('.tool-btn-main');
        pickColor('foreColor', mainF || btn);
        break;
      case 'hiliteColor':
        var lastH = btn.getAttribute('data-last-color') || '#ffeeba';
        document.execCommand('hiliteColor', false, lastH);
        break;
      case 'hiliteColorPalette':
        var mainH = btn.parentElement.querySelector('.tool-btn-main');
        pickColor('hiliteColor', mainH || btn);
        break;

      // --- 标题 / 引用 ---
      case 'formatBlock':
        document.execCommand('formatBlock', false, val || '<h2>');
        break;

      // --- 代码块 ---
      case 'code':
        insertCodeBlock();
        break;

      // --- 表格 ---
      case 'table':
        insertTable();
        break;

      // --- 图像 ---
      case 'image':
        // 保存选区后再打开文件选择器
        editor.focus();
        try {
          var sel = window.getSelection();
          if (sel.rangeCount) window._savedRange = sel.getRangeAt(0).cloneRange();
        } catch(e) {}
        document.getElementById('imageUpload').click();
        break;

      // --- 视频 ---
      case 'video':
        insertVideo();
        break;

      // --- 公式 ---
      case 'formula':
        insertFormula();
        break;

      // --- 链接 ---
      case 'link':
        insertLink();
        break;

      // --- 历史 / 目录 / 投票 / 宽屏（功能提示）---
      case 'history':  alert('历史版本功能即将上线'); break;
      case 'toc':      scrollToToc(); break;
      case 'vote':     alert('投票功能即将上线'); break;
      case 'wide':     toggleWide(); break;

      default: break;
    }

    syncContent();
    updateWordCount();
  }

  // ---------- 列表选择菜单 ----------
  function showListMenu(btn) {
    var existing = document.getElementById('listMenuPanel');
    if (existing) { document.body.removeChild(existing); return; }

    // 保存选区
    editor.focus();
    var savedRange = null;
    try {
      var sel = window.getSelection();
      if (sel.rangeCount) savedRange = sel.getRangeAt(0).cloneRange();
    } catch(e) {}

    var panel = document.createElement('div');
    panel.id = 'listMenuPanel';
    panel.style.cssText = 'position:fixed;z-index:99999;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12);padding:6px;min-width:120px;';

    var rect = btn.getBoundingClientRect();
    panel.style.top = (rect.bottom + 4) + 'px';
    panel.style.left = rect.left + 'px';

    var items = [
      { cmd: 'insertUnorderedList', icon: '☰', label: '无序列表' },
      { cmd: 'insertOrderedList', icon: '1.', label: '有序列表' },
    ];

    items.forEach(function(item) {
      var el = document.createElement('div');
      el.style.cssText = 'padding:6px 12px;border-radius:4px;cursor:pointer;font-size:0.82rem;color:#333;display:flex;align-items:center;gap:8px;transition:background 0.1s;';
      el.innerHTML = '<span style="font-size:1rem;">' + item.icon + '</span>' + item.label;
      el.addEventListener('mouseenter', function() { this.style.background = '#f5f5f5'; });
      el.addEventListener('mouseleave', function() { this.style.background = 'transparent'; });
      el.addEventListener('click', function() {
        if (savedRange) { try { var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(savedRange); } catch(e) {} }
        editor.focus();
        document.execCommand(item.cmd);
        syncContent();
        if (panel.parentNode) panel.parentNode.removeChild(panel);
      });
      panel.appendChild(el);
    });

    document.body.appendChild(panel);

    setTimeout(function() {
      document.addEventListener('click', closePanel);
    }, 0);

    function closePanel(e) {
      if (panel && !panel.contains(e.target) && e.target !== btn && !(btn && btn.contains(e.target))) {
        if (panel.parentNode) panel.parentNode.removeChild(panel);
        document.removeEventListener('click', closePanel);
      }
    }
  }

  // ---------- 对齐菜单 ----------
  function showAlignMenu(btn) {
    var existing = document.getElementById('alignMenuPanel');
    if (existing) { document.body.removeChild(existing); return; }

    editor.focus();
    var savedRange = null;
    try { var sel = window.getSelection(); if (sel.rangeCount) savedRange = sel.getRangeAt(0).cloneRange(); } catch(e) {}

    var panel = document.createElement('div');
    panel.id = 'alignMenuPanel';
    panel.style.cssText = 'position:fixed;z-index:99999;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12);padding:6px;min-width:120px;';
    var rect = btn.getBoundingClientRect();
    panel.style.top = (rect.bottom + 4) + 'px';
    panel.style.left = rect.left + 'px';

    var items = [
      { cmd: 'justifyLeft', icon: '≡', label: '左对齐' },
      { cmd: 'justifyCenter', icon: '≡', label: '居中' },
      { cmd: 'justifyRight', icon: '≡', label: '右对齐' },
    ];

    items.forEach(function(item) {
      var el = document.createElement('div');
      el.style.cssText = 'padding:6px 12px;border-radius:4px;cursor:pointer;font-size:0.82rem;color:#333;display:flex;align-items:center;gap:8px;transition:background 0.1s;';
      el.innerHTML = '<span style="font-size:1rem;">' + item.icon + '</span>' + item.label;
      el.addEventListener('mouseenter', function() { this.style.background = '#f5f5f5'; });
      el.addEventListener('mouseleave', function() { this.style.background = 'transparent'; });
      el.addEventListener('click', function() {
        if (savedRange) { try { var s = window.getSelection(); s.removeAllRanges(); s.addRange(savedRange); } catch(e) {} }
        editor.focus();
        document.execCommand(item.cmd);
        syncContent();
        if (panel.parentNode) panel.parentNode.removeChild(panel);
      });
      panel.appendChild(el);
    });

    document.body.appendChild(panel);
    setTimeout(function() { document.addEventListener('click', closeP); }, 0);
    function closeP(e) {
      if (panel && !panel.contains(e.target) && e.target !== btn && !(btn && btn.contains(e.target))) {
        if (panel.parentNode) panel.parentNode.removeChild(panel);
        document.removeEventListener('click', closeP);
      }
    }
  }

  // ---------- 颜色选择面板（20色） ----------
  var COLORS = [
    '#000000','#434343','#666666','#999999','#cccccc',
    '#ff0000','#ff4444','#ff8800','#ffcc00','#ffff00',
    '#88ff00','#00cc44','#00cccc','#0088ff','#0066ff',
    '#4444ff','#8800ff','#cc00ff','#ff00cc','#ff0066',
  ];

  function pickColor(cmd, btn) {
    // 关闭已有的颜色面板
    var existing = document.getElementById('colorPalette');
    if (existing) { document.body.removeChild(existing); return; }

    // 保存编辑器选区
    editor.focus();
    var savedRange = null;
    try {
      var sel = window.getSelection();
      if (sel.rangeCount) savedRange = sel.getRangeAt(0).cloneRange();
    } catch(e) {}

    var palette = document.createElement('div');
    palette.id = 'colorPalette';
    palette.style.cssText = 'position:fixed;z-index:99999;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12);padding:8px;';

    // 定位
    var rect = btn.getBoundingClientRect();
    palette.style.top = (rect.bottom + 4) + 'px';
    palette.style.left = rect.left + 'px';

    // 4x5 网格
    var grid = document.createElement('div');
    grid.style.cssText = 'display:grid;grid-template-columns:repeat(5,28px);gap:4px;';

    COLORS.forEach(function(color) {
      var cell = document.createElement('div');
      cell.style.cssText = 'width:28px;height:28px;border-radius:4px;cursor:pointer;border:2px solid transparent;transition:all 0.1s;';
      cell.style.background = color;
      if (color === '#ffffff' || color === '#ffff00' || color === '#88ff00' || color === '#00cc44') {
        cell.style.border = '2px solid #ddd';
      }
      cell.title = color;

      cell.addEventListener('mouseenter', function() { this.style.transform = 'scale(1.15)'; });
      cell.addEventListener('mouseleave', function() { this.style.transform = 'scale(1)'; });

      cell.addEventListener('click', function(e) {
        e.stopPropagation();
        applyColor(color);
      });

      grid.appendChild(cell);

      // 每行最后一个后加换行（grid自动换行，不需要）
    });

    // 清除格式按钮
    var clearBtn = document.createElement('div');
    clearBtn.textContent = '清除颜色';
    clearBtn.style.cssText = 'margin-top:6px;padding:4px 0;text-align:center;font-size:0.72rem;color:#999;cursor:pointer;border-radius:4px;border:1px dashed #ddd;transition:all 0.1s;';
    clearBtn.addEventListener('mouseenter', function() { this.style.background = '#f5f5f5'; });
    clearBtn.addEventListener('mouseleave', function() { this.style.background = 'transparent'; });
    clearBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      document.execCommand(cmd, false, '');
      editor.focus();
      syncContent();
      var icon = btn.querySelector('.tool-icon');
      if (icon) { icon.style.color = ''; icon.style.background = ''; }
      if (palette.parentNode) palette.parentNode.removeChild(palette);
    });

    palette.appendChild(grid);
    palette.appendChild(clearBtn);
    document.body.appendChild(palette);

    // 点击外部关闭
    setTimeout(function() {
      document.addEventListener('click', closePalette);
    }, 0);

    function closePalette(e) {
      if (!palette.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
        if (palette.parentNode) palette.parentNode.removeChild(palette);
        document.removeEventListener('click', closePalette);
      }
    }

    function applyColor(color) {
      // 恢复选区
      if (savedRange) {
        try {
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(savedRange);
        } catch(e) {}
      }
      editor.focus();
      document.execCommand(cmd, false, color);
      syncContent();
      // 同步图标颜色
      var icon = btn.querySelector('.tool-icon');
      if (icon) {
        if (cmd === 'hiliteColor') { icon.style.background = color; icon.style.borderRadius = '2px'; }
        else { icon.style.color = color; }
      }
      if (palette.parentNode) palette.parentNode.removeChild(palette);
      document.removeEventListener('click', closePalette);
    }
  }

  // ---------- 标题下拉打勾标记 ----------
  function updateHeadingCheckmark() {
    var dropdown = document.getElementById('headingDropdown');
    if (!dropdown) return;
    // 先清除所有勾选
    dropdown.querySelectorAll('.heading-check').forEach(function(el) { el.textContent = ''; });
    // 获取当前块标签
    var activeTag = 'p';
    try {
      var sel = window.getSelection();
      if (sel.rangeCount) {
        var node = sel.getRangeAt(0).startContainer;
        // 向上查找最近的标题或段落标签
        var el = node.nodeType === 3 ? node.parentNode : node;
        while (el && el !== editor && el !== document.body) {
          var tag = el.tagName ? el.tagName.toLowerCase() : '';
          if (['h1','h2','h3','h4','h5','h6','p'].indexOf(tag) >= 0) {
            activeTag = tag;
            break;
          }
          // 检查是否在 pre/code 内部
          if (tag === 'pre' || tag === 'code') { activeTag = 'p'; break; }
          el = el.parentNode;
        }
      }
    } catch(e) {}
    // 标记打勾
    var target = dropdown.querySelector('.heading-item[data-tag="' + activeTag + '"]');
    if (target) {
      var check = target.querySelector('.heading-check');
      if (check) check.textContent = '✓ ';
    } else {
      // 默认正文打勾
      var pItem = dropdown.querySelector('.heading-item[data-tag="p"]');
      if (pItem) pItem.querySelector('.heading-check').textContent = '✓ ';
    }
  }

  // ---------- 插入代码块（嵌入式） ----------
  function insertCodeBlock() {
    editor.focus();
    var sel = window.getSelection();
    var range = sel.rangeCount ? sel.getRangeAt(0) : document.createRange();
    if (!sel.rangeCount) { range.setStart(editor, 0); sel.addRange(range); }

    // 生成唯一 ID 用于后续操作
    var blockId = 'code-block-' + Date.now();
    var html = '<div class="code-block-wrap" id="' + blockId + '">'
             + '<div class="code-block-header">'
             + '<input class="code-block-lang-input" list="code-langs" placeholder="语言" value="plain">'
             + '<datalist id="code-langs">'
             + '<option value="plain"><option value="python"><option value="javascript"><option value="typescript">'
             + '<option value="html"><option value="css"><option value="scss"><option value="less">'
             + '<option value="sql"><option value="mysql"><option value="postgresql"><option value="sqlite">'
             + '<option value="java"><option value="kotlin"><option value="groovy"><option value="scala">'
             + '<option value="bash"><option value="shell"><option value="powershell"><option value="zsh">'
             + '<option value="json"><option value="yaml"><option value="xml"><option value="toml">'
             + '<option value="markdown"><option value="text"><option value="diff"><option value="regex">'
             + '<option value="go"><option value="rust"><option value="cpp"><option value="c">'
             + '<option value="csharp"><option value="fsharp"><option value="swift"><option value="objectivec">'
             + '<option value="php"><option value="ruby"><option value="perl"><option value="lua">'
             + '<option value="r"><option value="matlab"><option value="julia"><option value="fortran">'
             + '<option value="dart"><option value="flutter"><option value="vue"><option value="jsx">'
             + '<option value="dockerfile"><option value="makefile"><option value="cmake"><option value="gradle">'
             + '</datalist>'
             + '<button class="code-block-remove" onclick="removeCodeBlock(\'' + blockId + '\')" title="删除">✕</button>'
             + '</div>'
             + '<pre><code class="code-block-editor" contenteditable="true" spellcheck="false" data-placeholder="在此输入代码…"></code></pre>'
             + '</div><p><br></p>';

    document.execCommand('insertHTML', false, html);

    // 自动聚焦到代码编辑区
    var block = document.getElementById(blockId);
    if (block) {
      var codeEditor = block.querySelector('.code-block-editor');
      if (codeEditor) { codeEditor.focus(); }
    }
  }

  // 删除代码块
  window.removeCodeBlock = function (id) {
    var block = document.getElementById(id);
    if (block && confirm('删除此代码块？')) {
      block.parentNode.removeChild(block);
      syncContent();
    }
  };


  // ---------- 插入表格（网格选择器） ----------
  function insertTable() {
    // 关闭已有面板
    var existing = document.getElementById('tableGridPicker');
    if (existing) { document.body.removeChild(existing); return; }

    editor.focus();
    var btn = document.querySelector('[data-cmd="table"]');
    var rect = btn ? btn.getBoundingClientRect() : { bottom: 0, left: 0 };

    var picker = document.createElement('div');
    picker.id = 'tableGridPicker';
    picker.style.cssText = 'position:fixed;z-index:99999;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12);padding:10px;';
    picker.style.top = (rect.bottom + 4) + 'px';
    picker.style.left = (rect.left || 0) + 'px';

    var label = document.createElement('div');
    label.style.cssText = 'font-size:0.72rem;color:#999;text-align:center;margin-bottom:6px;';
    label.textContent = '1 × 1';
    picker.appendChild(label);

    var grid = document.createElement('div');
    grid.style.cssText = 'display:grid;grid-template-columns:repeat(10,22px);gap:3px;';

    var cells = [];
    var maxRows = 8, maxCols = 10;
    for (var r = 0; r < maxRows; r++) {
      for (var c = 0; c < maxCols; c++) {
        (function(row, col) {
          var cell = document.createElement('div');
          cell.style.cssText = 'width:22px;height:22px;border:1px solid #d9d9d9;border-radius:2px;background:#fff;cursor:pointer;transition:all 0.1s;';
          cell.dataset.row = row;
          cell.dataset.col = col;

          cell.addEventListener('mouseenter', function() {
            var r2 = parseInt(this.dataset.row);
            var c2 = parseInt(this.dataset.col);
            label.textContent = (r2 + 1) + ' × ' + (c2 + 1);
            cells.forEach(function(ce) {
              var cr = parseInt(ce.dataset.row);
              var cc = parseInt(ce.dataset.col);
              if (cr <= r2 && cc <= c2) {
                ce.style.background = '#e0e7ff';
                ce.style.borderColor = '#818cf8';
              } else {
                ce.style.background = '#fff';
                ce.style.borderColor = '#d9d9d9';
              }
            });
          });

          cell.addEventListener('click', function() {
            var r3 = parseInt(this.dataset.row) + 1;
            var c3 = parseInt(this.dataset.col) + 1;
            document.body.removeChild(picker);
            insertTableHtml(r3, c3);
          });

          grid.appendChild(cell);
          cells.push(cell);
        })(r, c);
      }
    }

    picker.appendChild(grid);

    // 手动输入行列
    var manualRow = document.createElement('div');
    manualRow.style.cssText = 'display:flex;align-items:center;gap:6px;margin-top:8px;padding-top:8px;border-top:1px solid #eee;';
    manualRow.innerHTML = '<span style="font-size:0.72rem;color:#999;white-space:nowrap;">行</span>'
      + '<input id="tbl-rows" type="number" min="1" max="20" value="3" style="width:40px;padding:2px 4px;border:1px solid #ddd;border-radius:4px;font-size:0.75rem;text-align:center;">'
      + '<span style="font-size:0.72rem;color:#999;white-space:nowrap;">列</span>'
      + '<input id="tbl-cols" type="number" min="1" max="20" value="3" style="width:40px;padding:2px 4px;border:1px solid #ddd;border-radius:4px;font-size:0.75rem;text-align:center;">'
      + '<button id="tbl-insert-btn" style="margin-left:auto;padding:3px 12px;border:none;border-radius:4px;background:#4f46e5;color:#fff;font-size:0.72rem;cursor:pointer;">插入</button>';
    picker.appendChild(manualRow);

    document.body.appendChild(picker);

    // 手动插入按钮
    document.getElementById('tbl-insert-btn').addEventListener('click', function() {
      var r = parseInt(document.getElementById('tbl-rows').value) || 3;
      var c = parseInt(document.getElementById('tbl-cols').value) || 3;
      document.body.removeChild(picker);
      insertTableHtml(r, c);
    });

    // 点击外部关闭
    setTimeout(function() {
      document.addEventListener('click', closePicker);
    }, 0);

    function closePicker(e) {
      if (picker && !picker.contains(e.target) && e.target !== btn && !(btn && btn.contains(e.target))) {
        if (picker.parentNode) picker.parentNode.removeChild(picker);
        document.removeEventListener('click', closePicker);
      }
    }
  }

  function insertTableHtml(rows, cols) {
    editor.focus();
    // 恢复选区
    try {
      var sel = window.getSelection();
      if (!sel.rangeCount) {
        var range = document.createRange();
        range.setStart(editor, editor.childNodes.length || 0);
        sel.addRange(range);
      }
    } catch(e) {}
    var html = '<table style="border-collapse:collapse;width:100%;margin:12px 0;">';
    for (var r = 0; r < rows; r++) {
      html += '<tr>';
      for (var c = 0; c < cols; c++) {
        html += '<td style="border:1px solid #d9d9d9;padding:8px 12px;min-width:40px;">&nbsp;</td>';
      }
      html += '</tr>';
    }
    html += '</table><p><br></p>';
    document.execCommand('insertHTML', false, html);
    syncContent();
    if (inspireBlock) inspireBlock.style.display = 'none';
  }

  // ---------- 插入链接 ----------
  function insertLink() {
    var url = prompt('输入链接地址：', 'https://');
    if (!url) return;
    var text = prompt('链接文字（留空使用 URL）：') || url;
    document.execCommand('insertHTML', false, '<a href="' + url + '" target="_blank">' + escapeHtml(text) + '</a>');
  }

  // ---------- 插入视频 (iframe) ----------
  function insertVideo() {
    var url = prompt('输入视频嵌入 URL（如 YouTube / Bilibili 分享链接）：');
    if (!url) return;
    // 简单判断，生成 iframe
    var iframe = '<div style="position:relative;padding-bottom:56.25%;height:0;margin:16px 0;">'
               + '<iframe src="' + url + '" frameborder="0" allowfullscreen '
               + 'style="position:absolute;top:0;left:0;width:100%;height:100%;border-radius:8px;"></iframe>'
               + '</div><p><br></p>';
    document.execCommand('insertHTML', false, iframe);
  }

  // ---------- 插入公式 (MathJax LaTeX) ----------
  function insertFormula() {
    var latex = prompt('输入 LaTeX 公式（如 E=mc^2）：');
    if (!latex) return;
    document.execCommand('insertHTML', false,
      '<span class="formula">$$' + escapeHtml(latex) + '$$</span> ');
  }

  // ---------- 插入上传的图片 ----------
  window.insertUploadedImage = function (input) {
    if (!input.files || !input.files[0]) return;
    var reader = new FileReader();
    reader.onload = function (e) {
      // 恢复选区
      editor.focus();
      if (window._savedRange) {
        try {
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(window._savedRange);
        } catch(ex) {}
        window._savedRange = null;
      }
      // 插入图片
      var imgHtml = '<p><img src="' + e.target.result + '" alt="uploaded" style="max-width:100%;border-radius:8px;display:block;margin:8px 0;"></p>';
      // 方式1：execCommand
      var worked = false;
      try { worked = document.execCommand('insertHTML', false, imgHtml); } catch(ex) {}
      // 方式2：直接选区操作（兜底）
      if (!worked) {
        try {
          var sel = window.getSelection();
          if (sel.rangeCount) {
            var range = sel.getRangeAt(0);
            var temp = document.createElement('div');
            temp.innerHTML = imgHtml;
            var frag = document.createDocumentFragment();
            while (temp.firstChild) frag.appendChild(temp.firstChild);
            range.deleteContents();
            range.insertNode(frag);
            range.collapse(false);
          }
        } catch(ex2) {}
      }
      syncContent();
      if (inspireBlock) inspireBlock.style.display = 'none';
      input.value = '';
    };
    reader.readAsDataURL(input.files[0]);
  }

  // ---------- 切换到目录位置 ----------
  function scrollToToc() {
    var toc = document.getElementById('editorToc');
    if (toc) toc.scrollIntoView({ behavior: 'smooth' });
  }

  // ---------- 宽屏切换 ----------
  function toggleWide() {
    var main = document.getElementById('editorMain');
    if (main) {
      main.classList.toggle('wide');
      var btn = document.querySelector('[data-cmd="wide"]');
      if (btn) btn.classList.toggle('active');
    }
  }

  // ---------- MD 切换 ----------
  function toggleMdMode() {
    alert('Markdown 编辑器模式即将上线，目前使用富文本模式。');
  }

  // ---------- 同步内容到隐藏 textarea ----------
  function syncContent() {
    if (!editor || !hiddenArea) return;
    // 隐藏灵感提示（有内容时）
    if (inspireBlock && editor.textContent.trim().length > 0) {
      inspireBlock.style.display = 'none';
    }
    var html = editor.innerHTML;
    // 空内容处理
    if (html === '' || html === '<br>' || html === '<br>') {
      hiddenArea.value = '';
    } else {
      hiddenArea.value = html;
    }
  }

  // ---------- 字数统计 ----------
  function updateWordCount() {
    if (!editor) return;
    var text = editor.textContent || '';
    var count = text.trim().length;
    var el = document.getElementById('wordCount');
    if (el) el.textContent = count;
  }

  // ---------- 标题提示 ----------
  function updateTitleHint(input) {
    if (!input) return;
    var len = input.value.length;
    var hint = document.getElementById('titleHint');
    if (!hint) return;
    if (len === 0) {
      hint.textContent = '还需输入 5 个字';
      hint.style.color = '#bbb';
    } else if (len < 5) {
      hint.textContent = '还需输入 ' + (5 - len) + ' 个字';
      hint.style.color = '#bbb';
    } else if (len >= 100) {
      input.value = input.value.substring(0, 100);
      hint.textContent = '已达字数上限';
      hint.style.color = '#ff4d4f';
    } else {
      hint.textContent = '已输入 ' + len + ' 个字';
      hint.style.color = '#52c41a';
    }
  }

  // ---------- HTML 转义 ----------
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // ---------- 发布 / 草稿 ----------
  window.submitPublish = function () {
    syncContent();
    document.getElementById('isPublishedInput').value = '1';
    document.getElementById('articleForm').submit();
  };

  window.saveDraft = function () {
    syncContent();
    document.getElementById('isPublishedInput').value = '0';
    document.getElementById('articleForm').submit();
  };

  // ---------- 初始化 ----------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
