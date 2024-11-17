document.addEventListener('DOMContentLoaded', function() {
    let dragSrcEl = null;
    let touchStartX = 0;
    let touchStartY = 0;
    const items = document.querySelectorAll('.note-item');

    items.forEach(item => {
        const link = item.querySelector('a');
        if (link) {
            // Add touch event listeners only to the hyperlink
            link.addEventListener('touchstart', handleTouchStart, false);
            link.addEventListener('touchmove', handleTouchMove, false);
            link.addEventListener('touchend', handleTouchEnd, false);
        }
    });

    let dragStartTimer;
    const DRAG_DELAY = 500; // 500ms hold before drag starts
    const DRAG_THRESHOLD = 10; // Pixels of movement required to initiate drag

    function handleTouchStart(e) {
        const touch = e.touches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
        
        // Don't prevent default immediately - allow link clicking
        dragStartTimer = setTimeout(() => {
            dragSrcEl = this.closest('.note-item');
            dragSrcEl.classList.add('dragging');
        }, DRAG_DELAY);
    }

    function handleTouchMove(e) {
        const touch = e.touches[0];
        const moveX = Math.abs(touch.clientX - touchStartX);
        const moveY = Math.abs(touch.clientY - touchStartY);
        
        // Clear drag timer if movement is detected before hold time
        if (!dragSrcEl && (moveX > DRAG_THRESHOLD || moveY > DRAG_THRESHOLD)) {
            clearTimeout(dragStartTimer);
            return;
        }
        
        if (dragSrcEl) {
            const deltaX = touch.clientX - touchStartX;
            const deltaY = touch.clientY - touchStartY;
            dragSrcEl.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
            e.preventDefault(); // Only prevent default if actually dragging
        }
    }

    function handleTouchEnd(e) {
        clearTimeout(dragStartTimer);
        if (!dragSrcEl) return;

        // Reset styles
        dragSrcEl.style.transform = '';
        dragSrcEl.classList.remove('dragging');

        // Find the element we're dropping onto
        const touch = e.changedTouches[0];
        const dropTarget = document.elementFromPoint(touch.clientX, touch.clientY);
        const dropItem = dropTarget.closest('.note-item');

        if (dropItem && dropItem !== dragSrcEl) {
            const childNoteId = dragSrcEl.dataset.noteId;
            const parentNoteId = dropItem.dataset.noteId;

            // Make the API call to update the parent-child relationship
            fetch('/api/attach_child_note', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    child_note_id: childNoteId,
                    parent_note_id: parentNoteId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload the page to show the updated structure
                    window.location.reload();
                } else {
                    console.error('Failed to update note relationship');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        dragSrcEl = null;
    }
});
