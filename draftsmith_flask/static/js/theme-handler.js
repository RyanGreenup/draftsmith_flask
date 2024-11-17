function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Update theme immediately
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Save theme preference via server
    fetch(`/set-theme/${newTheme}`).catch(console.error);
}

// Add event listener to theme toggle button when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});
