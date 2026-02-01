function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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

function openShareModal(warehouseId, warehouseName, sharedCount) {
    const modal = document.getElementById('shareModal');
    document.getElementById('shareModalTitle').innerText = `Совместный доступ: ${warehouseName}`;
    document.getElementById('sharedUsersCount').innerText = sharedCount;
    
    const usersList = document.getElementById('usersList');
    usersList.innerHTML = '';
    
    const usersDataElement = document.getElementById(`users-data-${warehouseId}`);
    if (usersDataElement) {
        const users = JSON.parse(usersDataElement.textContent);
        if (users.length === 0) {
            usersList.innerHTML = '<li>Список пуст</li>';
        } else {
            users.forEach(user => {
                const li = document.createElement('li');
                li.className = 'user-item';
                li.innerHTML = `
                    <div class="user-info">
                        <span class="user-username">${user.username}</span>
                        <span class="user-role">${user.role}</span>
                    </div>
                    <button class="btn-remove-user" onclick="removeUser(${warehouseId}, ${user.id})">Удалить</button>
                `;
                usersList.appendChild(li);
            });
        }
    }
    
    const addUserForm = document.getElementById('addUserForm');
    addUserForm.dataset.warehouseId = warehouseId;
    modal.style.display = 'flex';
}

function removeUser(warehouseId, userId) {
    const url = `/warehouse/${warehouseId}/remove_user/${userId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            console.error('Server returned error status:', response.status);
            alert('Ошибка сервера при удалении. Проверьте консоль Django.');
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Произошла системная ошибка при удалении.');
    });
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
}

function openAddUserModal() {
    closeShareModal();
    const errorDiv = document.getElementById('userLoginError');
    errorDiv.style.display = 'none';
    errorDiv.innerText = '';
    document.getElementById('addUserModal').style.display = 'flex';
}

function closeAddUserModal() {
    document.getElementById('addUserModal').style.display = 'none';
}

window.onclick = function(event) {
    const deleteModal = document.getElementById('deleteModal');
    const shareModal = document.getElementById('shareModal');
    const addUserModal = document.getElementById('addUserModal');
    
    if (event.target == deleteModal) closeDeleteModal();
    if (event.target == shareModal) closeShareModal();
    if (event.target == addUserModal) closeAddUserModal();
}

document.addEventListener('DOMContentLoaded', function() {
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const warehouseId = addUserForm.dataset.warehouseId;
            const formData = new FormData(addUserForm);
            const errorDiv = document.getElementById('userLoginError');
            errorDiv.style.display = 'none';
            fetch(`/warehouse/${warehouseId}/add_shared_user/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    return response.json().then(data => ({ status: response.status, body: data }));
                } else {
                    return { status: response.status, body: { message: "Сервер вернул некорректный ответ (не JSON)." } };
                }
            })
            .then(result => {
                if (result.status === 200) {
                    location.reload();
                } else {
                    errorDiv.innerText = result.body.message || "Ошибка при добавлении.";
                    errorDiv.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Add user error:', error);
                errorDiv.innerText = 'Произошла системная ошибка.';
                errorDiv.style.display = 'block';
            });
        });
    }
});