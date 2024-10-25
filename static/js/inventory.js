document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('.inventory-table');
    if (table) {
        table.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-edit')) {
                const itemId = e.target.getAttribute('data-item-id');
                editItem(itemId);
            }
        });
    }

    const addBtn = document.getElementById('addFoodStockBtn');
    const modal = document.getElementById('addFoodStockForm');
    const closeBtn = modal.querySelector('.close');

    addBtn.onclick = function() {
        modal.style.display = 'block';
    }

    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

function editItem(itemId) {
    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
    const cells = row.querySelectorAll('td');

    cells.forEach((cell, index) => {
        if (index < cells.length - 1) {  // Skip the last cell (Actions)
            const input = document.createElement('input');
            input.type = cell.classList.contains('date-cell') ? 'date' : 'text';
            input.name = cell.dataset.field;
            input.value = cell.textContent.trim();
            cell.textContent = '';
            cell.appendChild(input);
        }
    });

    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.classList.add('btn', 'btn-save');
    saveButton.onclick = () => saveItem(itemId);

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.classList.add('btn', 'btn-cancel');
    cancelButton.onclick = () => cancelEdit(itemId);

    const actionsCell = cells[cells.length - 1];
    actionsCell.innerHTML = '';
    actionsCell.appendChild(saveButton);
    actionsCell.appendChild(cancelButton);
}

function saveItem(itemId) {
    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
    const inputs = row.querySelectorAll('input');
    const data = {};

    inputs.forEach(input => {
        data[input.name] = input.value;
    });

    fetch(`/update_food_stock/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrf_token')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            location.reload();
        } else {
            alert('Failed to update item');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the item');
    });
}

function cancelEdit(itemId) {
    location.reload();
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
