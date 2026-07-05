// ===== admin.js — 后台管理交互 =====

function openCategoryEdit(id, name, desc) {
  document.getElementById('catEditName').value = name;
  document.getElementById('catEditDesc').value = desc;
  document.getElementById('catEditForm').action = '/admin/categories/' + id + '/edit';
  showModal('catEditModal');
}

function closeCategoryEdit() {
  hideModal('catEditModal');
}
