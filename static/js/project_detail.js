document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');

  const projectEvents = typeof PROJECT_EVENTS !== 'undefined' ? PROJECT_EVENTS : [];

  function toDateTimeLocal(dateStr) {
    if (!dateStr) return '';
    const dt = new Date(dateStr);
    const year = dt.getFullYear();
    const month = String(dt.getMonth() + 1).padStart(2, '0');
    const day = String(dt.getDate()).padStart(2, '0');
    const hours = String(dt.getHours()).padStart(2, '0');
    const minutes = String(dt.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  // === FullCalendar setup ===
  if (calendarEl) {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      selectable: true,
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      events: function(fetchInfo, successCallback, failureCallback) {
        fetch('/api/calendar/events/')
          .then(res => res.json())
          .then(apiEvents => successCallback(apiEvents.concat(projectEvents)))
          .catch(err => failureCallback(err));
      },
      eventContent: function(info) {
        return { html: `<div>${info.event.title}</div>` };
      },
      select: function(selectionInfo) {
        const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
        document.getElementById('eventId').value = '';
        document.getElementById('deleteEventBtn').style.display = 'none';
        document.getElementById('eventTitle').value = '';
        document.getElementById('startDate').value = toDateTimeLocal(selectionInfo.start);
        document.getElementById('endDate').value = toDateTimeLocal(new Date(selectionInfo.end.getTime() - 60000));
        document.getElementById('allDayCheckbox').checked = false;
        eventModal.show();
      },
      eventClick: function(info) {
        const eventId = info.event.id;
        fetch(`/api/calendar/events/${eventId}/update/`)
          .then(response => {
            if (!response.ok) throw new Error('Failed to load event data');
            return response.json();
          })
          .then(data => {
            document.getElementById('eventId').value = eventId;
            document.getElementById('eventTitle').value = data.title;
            document.getElementById('startDate').value = toDateTimeLocal(data.start_time || data.start);
            document.getElementById('endDate').value = toDateTimeLocal(data.end_time || data.end);
            document.getElementById('allDayCheckbox').checked = data.allDay;
            document.getElementById('deleteEventBtn').style.display = 'inline-block';
            new bootstrap.Modal(document.getElementById('eventModal')).show();
          })
          .catch(error => alert(error.message));
      }
    });

    calendar.render();
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // === TASK STATUS UPDATE ONLY ===
  const taskList = document.getElementById('task-list');
  if (taskList) {
    taskList.addEventListener('change', function(e) {
      const target = e.target;
      if (!target.classList.contains('task-toggle')) return;

      const taskId = target.dataset.taskId;
      const isDone = target.checked;
      target.disabled = true;

      fetch(`/tasks/${taskId}/toggle_done/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ done: isDone })
      })
      .then(res => {
        if (!res.ok) throw new Error('Failed to update task status');
        return res.json();
      })
      .then(data => {
        const li = target.closest('li');
        const statusTextEl = li.querySelector('.task-status-text');
        // ONLY update status text
        statusTextEl.textContent = data.new_status_display;
      })
      .catch(err => {
        alert(err.message);
        target.checked = !isDone;
      })
      .finally(() => target.disabled = false);
    });
  }

  // === EVENT FORM SUBMIT & DELETE (unchanged) ===
  const eventForm = document.getElementById('eventForm');
  if (eventForm) {
    eventForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const startDate = new Date(document.getElementById('startDate').value);
      if (startDate < new Date()) { alert('Start time cannot be in the past.'); return; }

      const form = e.target;
      const eventId = document.getElementById('eventId').value;
      let url = '/api/calendar/events/create/', method = 'POST';
      if (eventId) { url = `/api/calendar/events/${eventId}/update/`; method = 'POST'; }

      fetch(url, { method, headers: { 'X-CSRFToken': getCookie('csrftoken') }, body: new FormData(form) })
        .then(res => {
          if (!res.ok) return res.text().then(text => { throw new Error(res.status + ' ' + text); });
          return res.json();
        })
        .then(data => {
          if (data.status === 'success') {
            const modalEl = document.getElementById('eventModal');
            bootstrap.Modal.getInstance(modalEl).hide();
            form.reset();
            if (calendar) calendar.refetchEvents();
          } else console.error(data.errors);
        })
        .catch(err => alert('Failed to save event: ' + err.message));
    });
  }

  const deleteBtn = document.getElementById('deleteEventBtn');
  if (deleteBtn) {
    deleteBtn.addEventListener('click', function() {
      const eventId = document.getElementById('eventId').value;
      if (!eventId || !confirm('Are you sure you want to delete this event?')) return;

      fetch(`/api/calendar/events/${eventId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      })
      .then(res => {
        if (!res.ok) throw new Error('Failed to delete event.');
        return res.json();
      })
      .then(data => {
        if (data.status === 'success') {
          const modalEl = document.getElementById('eventModal');
          bootstrap.Modal.getInstance(modalEl).hide();
          if (calendar) calendar.refetchEvents();
        } else alert('Error deleting event');
      })
      .catch(err => alert(err.message));
    });
  }
});
