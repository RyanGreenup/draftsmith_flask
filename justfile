serve:
    poetry run gunicorn -w 4 -b 0.0.0.0:37239 src.server:app
sass:
    cd src/static
    npx sass --no-source-map src/static/styles:src/static/css
    # TODO this needs to do all
    # npx tailwindcss -i ./src/input.css -o ./src/output.css --watch
    build/compile_css.py

format:
    ruff format      src
    ruff check --fix src

install-deps:
    poetry install
    npm install

tailwind-init:
    npm install -D tailwindcss
    npx tailwindcss init

