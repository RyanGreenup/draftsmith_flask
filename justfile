serve:
    cd src && poetry run gunicorn -w 4 -b 0.0.0.0:5000 server:app

serve-dev:
    poetry run python src/main.py --port 5000 --host 0.0.0.0 --api-host vidar

sass:
    cd src/static
    npx sass --no-source-map src/static/styles:src/static/css
    build/compile_css.py

format:
    ruff format      src
    ruff check --fix src

install-deps:
    # poetry install
    npm install
    mkdir -p ./src/static/css/ ./src/static/js/
    cp -r ./node_modules/katex ./src/static/

tailwind-init:
    npm install -D tailwindcss
    npx tailwindcss init
