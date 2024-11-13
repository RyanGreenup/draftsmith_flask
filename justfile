serve:
    # API_SCHEME=http API_PORT=37240 API_HOST=vidar poetry run draftsmith_flask/server.py
    API_SCHEME=http API_PORT=37240 API_HOST=vidar gunicorn -w 4 -b 0.0.0.0:5000 server:app

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
