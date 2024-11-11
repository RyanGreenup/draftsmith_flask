document.addEventListener('DOMContentLoaded', function() {
    const tagItems = document.querySelectorAll('.tag-item');
    const noteItems = document.querySelectorAll('.note-item');
    let draggedTagId = null;
    let draggedNoteId = null;

    // Make tags draggable
    tagItems.forEach(item => {
        item.setAttribute('draggable', 'true');
        
        // Handle drag start
        item.addEventListener('dragstart', function(e) {
            e.stopPropagation();
            draggedTagId = this.dataset.tagId;
            draggedNoteId = null;
            e.dataTransfer.setData('text/plain', draggedTagId);
            this.classList.add('dragging');
        });

        item.addEventListener('dragend', function(e) {
            e.stopPropagation();
            this.classList.remove('dragging');
        });

        // Handle drag over
        item.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            document.querySelectorAll('.tag-item.drag-over').forEach(el => {
                if (el !== this) {
                    el.classList.remove('drag-over');
                }
            });
            
            this.classList.add('drag-over');
        });

        item.addEventListener('dragleave', function(e) {
            e.stopPropagation();
            this.classList.remove('drag-over');
        });

        // Handle drop
        item.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('drag-over');
            
            if (draggedTagId) {
                handleTagDrop(this.dataset.tagId);
            } else if (draggedNoteId) {
                handleNoteToTagDrop(draggedNoteId, this.dataset.tagId);
            }
        });

        // Handle summary element events for folded tags
        const summary = item.querySelector('summary');
        if (summary) {
            summary.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();

                document.querySelectorAll('.tag-item.drag-over').forEach(el => {
                    if (el !== item) {
                        el.classList.remove('drag-over');
                    }
                });

                item.classList.add('drag-over');
            });

            summary.addEventListener('dragleave', function(e) {
                e.stopPropagation();
                item.classList.remove('drag-over');
            });

            summary.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                item.classList.remove('drag-over');
                
                if (draggedTagId) {
                    handleTagDrop(item.dataset.tagId);
                } else if (draggedNoteId) {
                    handleNoteToTagDrop(draggedNoteId, item.dataset.tagId);
                }
            });
        }
    });

    // Make notes draggable for tag assignment
    noteItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            e.stopPropagation();
            draggedNoteId = this.dataset.noteId;
            draggedTagId = null;
            e.dataTransfer.setData('text/plain', draggedNoteId);
            this.classList.add('dragging');
        });
    });

    function handleTagDrop(targetTagId) {
        if (draggedTagId === targetTagId) {
            return;
        }

        fetch(`/api/attach_child_tag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                parent_tag_id: targetTagId,
                child_tag_id: draggedTagId
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error('Failed to attach child tag', response);
            }
        }).catch(error => {
            console.error('Error attaching child tag', error);
        });
    }

    function handleNoteToTagDrop(noteId, tagId) {
        fetch(`/api/attach_note_to_tag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                note_id: noteId,
                tag_id: tagId
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error('Failed to attach note to tag', response);
            }
        }).catch(error => {
            console.error('Error attaching note to tag', error);
        });
    }

    function getCSRFToken() {
        const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
    }
});
