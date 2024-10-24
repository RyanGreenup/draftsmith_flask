serve:
    poetry run gunicorn -w 4 -b 0.0.0.0:37239 src.server:app
sass:
    cd src/static
    npx sass --no-source-map src/static/styles:src/static/css
