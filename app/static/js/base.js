// ===== base.js — 全局交互 =====

document.addEventListener('DOMContentLoaded', function () {
  // Flash 消息 4 秒后自动淡出
  document.querySelectorAll('.flash-message').forEach(function (msg) {
    setTimeout(function () {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.4s';
      setTimeout(function () { msg.remove(); }, 400);
    }, 4000);
  });

  // 点击模态遮罩关闭
  document.querySelectorAll('.modal-overlay').forEach(function (m) {
    m.addEventListener('click', function (e) {
      if (e.target === m) m.style.display = 'none';
    });
  });
});

// 显示模态框
function showModal(id) {
  var el = document.getElementById(id);
  if (el) el.style.display = 'flex';
}

// 隐藏模态框
function hideModal(id) {
  var el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

// 点击遮罩外部关闭（配合 onclick="closeModalOutside(event, 'id')"）
function closeModalOutside(event, id) {
  if (event.target === document.getElementById(id)) {
    hideModal(id);
  }
}
