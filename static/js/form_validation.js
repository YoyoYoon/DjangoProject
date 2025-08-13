document.addEventListener('DOMContentLoaded', function() {
  // Generic validation function
  function validateForm(form) {
    const title = form.querySelector('[name="title"]');
    if (!title || !title.value.trim()) {
      alert('Title is required.');
      title.focus();
      return false;
    }

    // For date/time fields
    const startInput = form.querySelector('[name="start_time"], [name="start_date"]');
    const endInput = form.querySelector('[name="end_time"], [name="end_date"]');
    const repeatUntilInput = form.querySelector('[name="repeat_until"]');

    if (startInput && endInput) {
      const start = new Date(startInput.value);
      const end = new Date(endInput.value);
      if (start >= end) {
        alert('End date/time must be after start date/time.');
        endInput.focus();
        return false;
      }
      const now = new Date();
      if (start < now) {
        alert('Start date/time cannot be in the past.');
        startInput.focus();
        return false;
      }
    }

    if (startInput && repeatUntilInput && repeatUntilInput.value) {
      const start = new Date(startInput.value);
      const repeatUntil = new Date(repeatUntilInput.value);
      if (repeatUntil < start) {
        alert('Repeat until date cannot be before start date.');
        repeatUntilInput.focus();
        return false;
      }
    }

    return true;
  }

  // Attach validation to all forms
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!validateForm(form)) {
        e.preventDefault();
      }
    });
  });
});
