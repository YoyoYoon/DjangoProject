document.addEventListener('DOMContentLoaded', () => {
    // Helper to get CSRF token cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const c = cookie.trim();
                if (c.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Attach event listener to all checkboxes
    document.querySelectorAll('.task-toggle').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const taskId = e.target.getAttribute('data-task-id');
            const isDone = e.target.checked;

            fetch(`/tasks/${taskId}/toggle_done/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ done: isDone })
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to update task status');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Update status text and strike-through styling
                    const statusTextEl = e.target.closest('li').querySelector('.task-status-text');
                    statusTextEl.textContent = data.new_status_display;

                    const titleEl = e.target.closest('li').querySelector('strong');
                    if (isDone) {
                        titleEl.style.textDecoration = 'line-through';
                    } else {
                        titleEl.style.textDecoration = 'none';
                    }
                } else {
                    alert('Error updating task.');
                    e.target.checked = !isDone; // revert UI change
                }
            })
            .catch(err => {
                alert(err.message);
                e.target.checked = !isDone; // revert UI change
            });
        });
    });
});
