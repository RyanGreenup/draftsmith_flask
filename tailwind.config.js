/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/*.{html,js}",
    "./src/templates/**/*.{html,js}",
    "./src/static/css/{html,js}",
    "./src/static/styles/{html,js}",
    "./src/static/js/{html,js}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      "light",
      "dark",
      "cupcake",
      "bumblebee",
      "emerald",
      "corporate",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "autumn",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "winter",
      "dim",
      "nord",
      "sunset",
      {
        my_catppucin: {

          "primary": "#c792ea",    // Replacing with a softer purple
          "secondary": "#89b4fa",  // Softer blue to align with the pastel style
          "accent": "#91d7ff",     // Keeping this light and soft
          "neutral": "#1e1e2e",    // A dark, muted tone for contrast
          "base-100": "#2b213a",   // Adjusted for better background consistency
          "info": "#74c7ec",       // A more subdued blue
          "success": "#a6e3a1",    // Light green for success messages
          "warning": "#f9e2af",    // Pastel yellow for warnings
          "error": "#f38ba8",      // Softer red for error messages
        },
        aurora: {
          "primary": "#d800ff",
          "secondary": "#002cff",
          "accent": "#00cdff",
          "neutral": "#09140f",
          "base-100": "#2e2328",
          "info": "#00beff",
          "success": "#669e00",
          "warning": "#d97100",
          "error": "#cf002b",
        },
        twilight: {
          "primary": "#e100ff",
          "secondary": "#00bd62",
          "accent": "#654f00",
          "neutral": "#1a1c26",
          "base-100": "#fff5ff",
          "info": "#00c4ff",
          "success": "#569a00",
          "warning": "#da0000",
          "error": "#ff7c84",
        },
      },
    ],
  },
}


