function setupEditDialog() {
    const dialog = document.getElementById('edit-dialog');
    if (!dialog) {
        return;
    }

    const form = document.getElementById('edit-expense-form');
    const cancelButton = document.getElementById('cancel-edit');

    if (form) {
        form.addEventListener('submit', (event) => {
            if (!form.action) {
                return;
            }
            event.preventDefault();

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton ? submitButton.textContent : '';
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Zapisywanie...';
            }

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
                .then((response) =>
                    response
                        .json()
                        .catch(() => ({}))
                        .then((data) => ({ response, data })),
                )
                .then(({ response, data }) => {
                    if (!response.ok) {
                        throw new Error(
                            (data && data.error) || 'Nie udało się zapisać zmian. Spróbuj ponownie.',
                        );
                    }

                    dialog.close();

                    if (data && data.redirect) {
                        window.location.href = data.redirect;
                        return;
                    }

                    if (response.redirected && response.url) {
                        window.location.href = response.url;
                        return;
                    }

                    window.location.reload();
                })
                .catch((error) => {
                    alert(error.message || 'Nie udało się zapisać zmian. Spróbuj ponownie.');
                })
                .finally(() => {
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = originalText;
                    }
                });
        });
    }

    document.querySelectorAll('[data-action="edit"]').forEach((button) => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            if (!row) {
                return;
            }
            const payload = row.dataset.expense ? JSON.parse(row.dataset.expense) : {};
            form.action = row.dataset.updateUrl;
            form.querySelector('#edit_expense_date').value = payload.expense_date || '';
            form.querySelector('#edit_merchant').value = payload.merchant || '';
            form.querySelector('#edit_amount').value = payload.amount !== undefined ? Number(payload.amount).toFixed(2) : '';
            form.querySelector('#edit_category').value = payload.category || '';
            form.querySelector('#edit_expense_type').value = payload.expense_type || '';
            form.querySelector('#edit_notes').value = payload.notes || '';
            form.querySelector('#edit_bank').value = payload.bank || '';
            form.querySelector('#edit_description').value = payload.description || '';
            dialog.showModal();
        });
    });

    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            dialog.close();
        });
    }
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.draggable-row:not(.dragging)')];

    return draggableElements.reduce(
        (closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            }
            return closest;
        },
        { offset: Number.NEGATIVE_INFINITY, element: null },
    ).element;
}

function sendReorder(tbody, url) {
    const order = [...tbody.querySelectorAll('.draggable-row')].map((row, index) => {
        row.dataset.position = index;
        return Number(row.dataset.expenseId);
    });

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({ order }),
    }).catch(() => {
        alert('Nie udało się zapisać nowej kolejności. Odśwież stronę i spróbuj ponownie.');
    });
}

function setupDragAndDrop() {
    const table = document.querySelector('[data-expenses-table]');
    if (!table) {
        return;
    }

    const canReorder = table.dataset.canReorder === 'true';
    if (!canReorder) {
        return;
    }

    const reorderUrl = table.dataset.reorderUrl;
    const tbody = table.querySelector('tbody');
    if (!tbody) {
        return;
    }

    tbody.querySelectorAll('.draggable-row').forEach((row) => {
        row.setAttribute('draggable', 'true');
    });

    tbody.addEventListener('dragstart', (event) => {
        const target = event.target;
        if (target && target.classList && target.classList.contains('draggable-row')) {
            target.classList.add('dragging');
        }
    });

    tbody.addEventListener('dragend', (event) => {
        const target = event.target;
        if (target && target.classList && target.classList.contains('draggable-row')) {
            target.classList.remove('dragging');
            sendReorder(tbody, reorderUrl);
        }
    });

    tbody.addEventListener('dragover', (event) => {
        event.preventDefault();
        const afterElement = getDragAfterElement(tbody, event.clientY);
        const dragging = tbody.querySelector('.dragging');
        if (!dragging) {
            return;
        }
        if (afterElement == null) {
            tbody.appendChild(dragging);
        } else {
            tbody.insertBefore(dragging, afterElement);
        }
    });
}

function setupImportDialog() {
    const trigger = document.querySelector('[data-open-import]');
    const dialog = document.getElementById('import-dialog');
    if (!trigger || !dialog) {
        return;
    }

    const cancel = document.getElementById('cancel-import');

    trigger.addEventListener('click', () => {
        dialog.showModal();
    });

    if (cancel) {
        cancel.addEventListener('click', () => {
            dialog.close();
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setupEditDialog();
    setupDragAndDrop();
    setupImportDialog();
});
