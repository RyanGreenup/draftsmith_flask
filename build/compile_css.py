#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

# Change to Root Assuming this is under /build
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Now in /
dir = Path("src/static/css")
for file in dir.glob("*.css"):
    file = str(file)
    # TODO consider minifying
    subprocess.run(["npx", "tailwindcss", "-i", file, "-o", file])
