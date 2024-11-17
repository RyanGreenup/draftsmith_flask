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
    s += f"""<li>
<input
    type="radio"
    name="theme-dropdown"
    class="theme-controller btn btn-sm btn-block btn-ghost justify-start"
    aria-label="{theme.title()}"
    value="{theme}" />
</li>\n"""
top = """
<div class="dropdown mb-72">
  <div tabindex="0" role="button" class="btn m-1">
    Theme
    <svg
      width="12px"
      height="12px"
      class="inline-block h-2 w-2 fill-current opacity-60"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 2048 2048">
      <path d="M1799 349l242 241-1017 1017L7 590l242-241 775 775 775-775z"></path>
    </svg>
  </div>
  <ul tabindex="0" class="dropdown-content bg-base-300 rounded-box z-[1] w-52 p-2 shadow-2xl">
"""
bottom = """
  </ul>
</div>
"""
s = top + s + bottom
os.chdir(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # Change to Root Assuming this is under /build

with open("src/templates/theme_controller.html", "w") as f:
    f.write(s)
