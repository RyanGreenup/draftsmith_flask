from flask import Flask, render_template, request, redirect, url_for
from api.assets.upload import upload_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Notes App"

@app.route('/upload_asset', methods=['GET', 'POST'])
def upload_asset_page():
    if request.method == 'POST':
        file = request.files['file']
        note_id = request.form.get('note_id')
        description = request.form.get('description')
        
        if file and note_id:
            filename = file.filename
            file_path = os.path.join('temp', filename)
            file.save(file_path)
            
            try:
                result = upload_file(file_path, int(note_id), description)
                os.remove(file_path)  # Remove the temporary file
                return f"File uploaded successfully. {result.message}"
            except Exception as e:
                return f"Error uploading file: {str(e)}"
        else:
            return "No file or note ID provided"
    
    return render_template('upload_asset.html')

if __name__ == '__main__':
    app.run(debug=True)
