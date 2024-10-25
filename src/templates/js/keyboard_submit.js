/*
This script allows users to submit a form by pressing Ctrl + Enter (or Command + Enter on macOS) on their keyboard.

The id of the form element is content-edit-form.
*/

document.addEventListener('DOMContentLoaded', (event) => {
// Select the form element
const form = document.getElementById('content-edit-form');

document.addEventListener('keydown', (event) => {
    // Check if Ctrl (or Command on macOS) and Enter are pressed
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault(); // Prevent any default action for the keys
        if (form) {
            form.submit(); // Submit the form
        }
    }
});
});
