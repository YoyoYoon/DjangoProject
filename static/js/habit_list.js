document.querySelectorAll('.habit-completed-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
      const label = e.target.nextElementSibling;
      if (e.target.checked) {
        label.style.textDecoration = 'line-through';
      } else {
        label.style.textDecoration = 'none';
      }
    });
  });