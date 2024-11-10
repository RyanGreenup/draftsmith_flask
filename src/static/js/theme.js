function handleThemeChange(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('selectedTheme', themeName);
}

document.addEventListener('DOMContentLoaded', function() {
    const storedTheme = localStorage.getItem('selectedTheme');
    if (storedTheme) {
        document.documentElement.setAttribute('data-theme', storedTheme);
    }

    // Add event listeners to theme controllers
    const themeControllers = document.querySelectorAll('.theme-controller');
    themeControllers.forEach(function(controller) {
        controller.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior
            const selectedTheme = controller.getAttribute('data-theme-value');
            handleThemeChange(selectedTheme);
        });
    });
});
