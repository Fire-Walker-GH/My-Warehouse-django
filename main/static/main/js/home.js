function openDeleteModal(warehouseId, warehouseName) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const text = document.getElementById('modalText');

    text.innerText = `Вы уверены, что хотите удалить склад "${warehouseName}"? Все товары на нем будут удалены безвозвратно.`;

    form.action = `/warehouse/delete/${warehouseId}/`; 

    modal.style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target == modal) {
        closeDeleteModal();
    }
}
