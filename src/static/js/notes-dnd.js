document.addEventListener('DOMContentLoaded', function() {
  const noteItems = document.querySelectorAll('.note-item');
  let draggedNoteId = null;

  noteItems.forEach(item => {
    // Handle direct note item events
    item.addEventListener('dragstart', function(e) {
      draggedNoteId = this.dataset.noteId;
      e.dataTransfer.setData('text/plain', draggedNoteId);
      this.classList.add('dragging');
    });

    item.addEventListener('dragend', function(e) {
      this.classList.remove('dragging');
    });

    item.addEventListener('dragover', function(e) {
      e.preventDefault();
      this.classList.add('drag-over');
    });

    item.addEventListener('dragleave', function(e) {
      this.classList.remove('drag-over');
    });

    item.addEventListener('drop', function(e) {
      e.preventDefault();
      this.classList.remove('drag-over');
      handleDrop(this.dataset.noteId);
    });

    // Handle summary element events for folded notes
    const summary = item.querySelector('summary');
    if (summary) {
      summary.addEventListener('dragover', function(e) {
        e.preventDefault();
        item.classList.add('drag-over');
      });

      summary.addEventListener('dragleave', function(e) {
        item.classList.remove('drag-over');
      });

      summary.addEventListener('drop', function(e) {
        e.preventDefault();
        item.classList.remove('drag-over');
        handleDrop(item.dataset.noteId);
      });
    }
  });

  function handleDrop(targetNoteId) {
    if (draggedNoteId === targetNoteId) {
      return;
    }

    fetch(`/api/attach_child_note`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        parent_note_id: targetNoteId,
        child_note_id: draggedNoteId
      })
    }).then(response => {
      if (response.ok) {
        location.reload();
      } else {
        console.error('Failed to attach child note', response);
      }
    }).catch(error => {
      console.error('Error attaching child note', error);
    });
  }

  function getCSRFToken() {
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    return csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
  }
});
