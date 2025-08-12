document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');

  // Injected from Django template
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
    // Merge events from API and projects
    events: function(fetchInfo, successCallback, failureCallback) {
      fetch('/api/calendar/events/')
        .then(res => res.json())
        .then(apiEvents => {
          // Combine API events and project events
          successCallback(apiEvents.concat(projectEvents));
        })
        .catch(err => {
          console.error('Error fetching API events:', err);
          failureCallback(err);
        });
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

      const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
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

          document.getElementById('repeat').value = data.repeat || 'none';
          document.getElementById('repeatUntil').value = data.repeat_until || '';

          document.getElementById('deleteEventBtn').style.display = 'inline-block';

          const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
          eventModal.show();
        })
        .catch(error => {
          alert(error.message);
        });
    }
  });

  calendar.render();

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

  document.getElementById('eventForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const form = e.target;
    const eventId = document.getElementById('eventId').value;

    let url = '/api/calendar/events/create/';
    let method = 'POST';

    if (eventId) {
      url = `/api/calendar/events/${eventId}/update/`;
      method = 'POST'; // or PATCH
    }

    const formData = new FormData(form);

    fetch(url, {
      method: method,
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        return response.text().then(text => {
          console.error('Server response:', response.status, text);
          throw new Error('Network response was not ok: ' + response.status);
        });
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        const modalEl = document.getElementById('eventModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        form.reset();
        calendar.refetchEvents();
      } else {
        alert('Error saving event');
        console.log(data.errors);
      }
    })
    .catch(error => {
      alert('Failed to save event: ' + error.message);
    });
  });

  document.getElementById('deleteEventBtn').addEventListener('click', function() {
    const eventId = document.getElementById('eventId').value;
    if (!eventId) return;

    if (!confirm('Are you sure you want to delete this event?')) return;

    fetch(`/api/calendar/events/${eventId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to delete event.');
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        const modalEl = document.getElementById('eventModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        calendar.refetchEvents();
      } else {
        alert('Error deleting event');
      }
    })
    .catch(error => {
      alert(error.message);
    });
  });

});
