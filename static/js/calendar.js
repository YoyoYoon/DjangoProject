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
      document.getElementById('eventId').value = '';
      document.getElementById('deleteEventBtn').style.display = 'none';

      document.getElementById('eventTitle').value = '';
      document.getElementById('startDate').value = toDateTimeLocal(selectionInfo.start);
      document.getElementById('endDate').value = toDateTimeLocal(new Date(selectionInfo.end.getTime() - 60000));

      document.getElementById('repeat').value = 'none';
      document.getElementById('repeatUntil').value = '';
      document.getElementById('allDay').checked = false;  // Reset all-day

      new bootstrap.Modal(document.getElementById('eventModal')).show();
    },
    eventClick: function(info) {
      const eventId = info.event.id;

      fetch(`/api/calendar/events/${eventId}/update/`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to load event data');
          return res.json();
        })
        .then(data => {
          document.getElementById('eventId').value = eventId;
          document.getElementById('eventTitle').value = data.title;
          document.getElementById('startDate').value = toDateTimeLocal(data.start_time || data.start);
          document.getElementById('endDate').value = toDateTimeLocal(data.end_time || data.end);
          document.getElementById('repeat').value = data.repeat || 'none';
          document.getElementById('repeatUntil').value = data.repeat_until || '';
          document.getElementById('allDay').checked = !!data.all_day; // Set all-day

          document.getElementById('deleteEventBtn').style.display = 'inline-block';

          new bootstrap.Modal(document.getElementById('eventModal')).show();
        })
        .catch(err => alert(err.message));
    }
  });

  calendar.render();

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      });
    }
    return cookieValue;
  }

  document.getElementById('eventForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = e.target;
    const eventId = document.getElementById('eventId').value;

    let url = '/api/calendar/events/create/';
    if (eventId) url = `/api/calendar/events/${eventId}/update/`;

    const formData = new FormData(form);
    formData.set('all_day', document.getElementById('allDay').checked ? 'true' : 'false'); // Include all-day

    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: formData
    })
    .then(res => {
      if (!res.ok) return res.text().then(text => { throw new Error(text) });
      return res.json();
    })
    .then(data => {
      if (data.status === 'success') {
        bootstrap.Modal.getInstance(document.getElementById('eventModal')).hide();
        form.reset();
        calendar.refetchEvents();
      } else {
        console.log(data.errors);
        alert('Error saving event');
      }
    })
    .catch(err => alert('Failed to save event: ' + err.message));
  });

  document.getElementById('deleteEventBtn').addEventListener('click', function() {
    const eventId = document.getElementById('eventId').value;
    if (!eventId || !confirm('Are you sure you want to delete this event?')) return;

    fetch(`/api/calendar/events/${eventId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        bootstrap.Modal.getInstance(document.getElementById('eventModal')).hide();
        calendar.refetchEvents();
      } else alert('Error deleting event');
    })
    .catch(err => alert(err.message));
  });
});
