// Function to set theme and save to localStorage
function setTheme(themeName) {
    // Save to localStorage first
    localStorage.setItem('theme', themeName);
    // Set theme on html element
    requestAnimationFrame(() => {
        document.documentElement.setAttribute('data-theme', themeName);
    });
    // Update radio button selection
    const radioButton = document.querySelector(`input[name="theme-dropdown"][value="${themeName}"]`);
    if (radioButton) {
        radioButton.checked = true;
    }
}

// Function to load saved theme
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    }
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSavedTheme();

    // Add event listeners to all theme radio buttons
    const themeRadios = document.querySelectorAll('.theme-controller');
    themeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            setTheme(e.target.value);
        });
    });
});
