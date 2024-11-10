document.addEventListener('DOMContentLoaded', function() {
    const sidebarItems = document.querySelectorAll('.note-item');
    let draggedItem = null;
    
    sidebarItems.forEach(item => {
        item.setAttribute('draggable', true);
        
        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            e.dataTransfer.setData('text/plain', item.dataset.noteId);
            item.classList.add('dragging');
        });
        
        item.addEventListener('dragend', () => {
            draggedItem = null;
            item.classList.remove('dragging');
            document.querySelectorAll('.note-item').forEach(item => {
                item.classList.remove('drag-over');
            });
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (draggedItem !== item) {
                item.classList.add('drag-over');
            }
        });
        
        item.addEventListener('dragleave', () => {
            item.classList.remove('drag-over');
        });
        
        item.addEventListener('drop', async (e) => {
            e.preventDefault();
            item.classList.remove('drag-over');
            
            const draggedNoteId = e.dataTransfer.getData('text/plain');
            const targetNoteId = item.dataset.noteId;
            
            if (draggedNoteId === targetNoteId) return;
            
            try {
                // First detach the note from its current parent
                await fetch(`/note/${draggedNoteId}/move`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'detach=true'
                });
                
                // Then attach it to the new parent
                const response = await fetch(`/note/${draggedNoteId}/move`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `new_parent_id=${targetNoteId}`
                });
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    const error = await response.text();
                    console.error('Error moving note:', error);
                    alert('Failed to move note. Please try again.');
                }
            } catch (error) {
                console.error('Error moving note:', error);
                alert('Failed to move note. Please try again.');
            }
        });
    });
});
