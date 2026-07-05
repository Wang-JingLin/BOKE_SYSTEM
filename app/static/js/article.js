// ===== article.js — 文章详情交互 =====

function toggleLike(articleId) {
  fetch('/interact/like/' + articleId, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var c = document.getElementById('likeCount');
      if (c) c.textContent = data.count;
      var b = document.getElementById('likeBtn');
      if (b) {
        if (data.liked) { b.style.color = '#1677ff'; }
        else { b.style.color = ''; }
      }
    })
    .catch(function () {});
}

function toggleFavorite(articleId) {
  fetch('/interact/favorite/' + articleId, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var c = document.getElementById('favCount');
      if (c) c.textContent = data.count;
      var i = document.getElementById('favIcon');
      if (i) i.textContent = data.favorited ? '★' : '☆';
      var b = document.getElementById('favBtn');
      if (b) {
        b.style.color = data.favorited ? '#faad14' : '';
      }
    })
    .catch(function () {});
}

function showReply(commentId) {
  var box = document.getElementById('replyBox-' + commentId);
  if (box) {
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
  }
}
