import os

themes = [
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
      "my_catppucin",
      "aurora",
      "twilight",
      ]

s = ""
for theme in themes:
    s+=f"""<li>
<input
    type="radio"
    name="theme-dropdown"
    class="theme-controller btn btn-sm btn-block btn-ghost justify-start"
    aria-label="{theme.title()}"
    value="{theme}"
    onclick="handleThemeChange(this.value)"
    onchange="handleThemeChange(this.value)" />
</li>\n"""
top = ""
bottom = ""
s = top + s + bottom
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Change to Root Assuming this is under /build

with open("src/templates/theme_controller.html", "w") as f:
    f.write(s)
