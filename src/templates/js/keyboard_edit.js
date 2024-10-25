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
    });
});

