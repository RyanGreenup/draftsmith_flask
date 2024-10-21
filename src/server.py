from flask import Flask, request

app = Flask(__name__)

@app.route('/<path:path>')
def show_path(path):
    full_url = request.url
    return f"You visited: {full_url}"

@app.route('/')
def root():
    return "You visited the root URL: " + request.url

if __name__ == '__main__':
    app.run(debug=True)
