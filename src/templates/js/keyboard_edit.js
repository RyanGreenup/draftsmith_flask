/*
This script allows users to navigate to the edit note page by pressing Alt + E on their keyboard.

The link for editing the note should have a unique identifier, such as an id.
*/

document.addEventListener('DOMContentLoaded', (event) => {
    // Select the anchor element for editing the note
    const editLink = document.querySelector('a[data-edit-link]');

    document.addEventListener('keydown', (event) => {
        // Check if Alt and E are pressed
        if (event.altKey && event.key === 'e') {
            event.preventDefault(); // Prevent any default action for the keys
            if (editLink) {
                window.location.href = editLink.href; // Navigate to the edit note page
            }
        }

        // Check if Alt and C are pressed
        if (event.altKey && event.key === 'z') {
            event.preventDefault(); // Prevent any default action for the keys
            insertText('λ#\(\)#');
            /* λ#(x)# */
        }
    });

    function insertText(text) {
        const selection = window.getSelection();
        const activeElement = document.activeElement;

        if (selection.rangeCount > 0 || (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA'))) {
            // If there is a selection or focus on an input element, insert text at the caret position
            let range;

            if (selection.rangeCount > 0) {
                range = selection.getRangeAt(0);
            } else {
                range = document.createRange();
                range.selectNodeContents(activeElement);
                range.collapse(true);
            }

            const textNode = document.createTextNode(text);
            range.insertNode(textNode);

            // Move the cursor to the end of the inserted text
            range.setStartAfter(textNode);
            range.setEndAfter(textNode);
            selection.removeAllRanges();
            selection.addRange(range);
        } else {
            console.warn('No input field or textarea is active.');
        }
    }
});

