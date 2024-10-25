serve:
    poetry run gunicorn -w 4 -b 0.0.0.0:37239 src.server:app
sass:
    cd src/static
    npx sass --no-source-map src/static/styles:src/static/css
    build/compile_css.py

format:
    ruff format      src
    ruff check --fix src

install-deps:
    poetry install
    npm install
    mkdir -p ./src/static/css/ ./src/static/js/
    cp ./node_modules/katex/dist/katex.css ./src/static/css/
    cp ./node_modules/katex/dist/katex.min.js ./src/static/js/

tailwind-init:
    npm install -D tailwindcss
    npx tailwindcss init

