// Theme handling functionality
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    // Update button icons visibility
    document.querySelectorAll('#theme-toggle svg').forEach(icon => {
        icon.classList.toggle('hidden', !icon.classList.contains(theme === 'dark' ? 'dark:block' : 'dark:hidden'));
    });
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Update theme immediately
    setTheme(newTheme);
    
    // Save theme preference via server
    fetch(`/set-theme/${newTheme}`, {
        method: 'GET',
        credentials: 'same-origin'
    }).catch(console.error);
}

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Set initial theme based on HTML data-theme attribute
    const initialTheme = document.documentElement.getAttribute('data-theme');
    setTheme(initialTheme || 'light');
});
