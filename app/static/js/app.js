document.addEventListener('DOMContentLoaded', function () {
  var sessionKey = 'ardhiya_session_id';
  var sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {
    sessionId = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
    localStorage.setItem(sessionKey, sessionId);
  }
  document.querySelectorAll('#session_id_specs, #session_id_image').forEach(function (el) {
    el.value = sessionId;
  });
});

# file: app/static/js/app.js
