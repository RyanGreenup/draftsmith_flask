/*
This script allows users to navigate to the edit note page by pressing Alt + E on their keyboard.

The link for editing the note should have a unique identifier, such as an id.
*/

document.addEventListener('DOMContentLoaded', (event) => {
    const editLink = document.querySelector('a[data-edit-link]');

    document.addEventListener('keydown', (event) => {
        if (event.altKey && event.key === 'e') {
            event.preventDefault();
            if (editLink) {
                window.location.href = editLink.href;
            }
        }

        if (event.altKey && event.key === 'z') {
            event.preventDefault();
            insertTextAtCaret('λ#()#');
        }
    });

    function insertTextAtCaret(text) {
        const activeElement = document.activeElement;

        if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
            const startPos = activeElement.selectionStart;
            const endPos = activeElement.selectionEnd;

            const originalText = activeElement.value;
            activeElement.value = originalText.slice(0, startPos) + text + originalText.slice(endPos);

            // Move the caret just after the '(' in the inserted text
            const newCaretPosition = startPos + text.indexOf('(') + 1;

            // Set selection/cursor position
            activeElement.setSelectionRange(newCaretPosition, newCaretPosition);
            activeElement.focus();
        } else {
            console.warn('No input field or textarea is active.');
        }
    }
});

