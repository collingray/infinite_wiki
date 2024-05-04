from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
import os
import time

from utils import generate_file
from file_db import FileDB

N_GENERATION_RETRIES = 3

app = Flask(__name__)

db = FileDB(load_dir='data/html')


@app.route('/')
@app.route('/index')
@app.route('/wiki')
def serve_random_file():
    """Redirect to serve a random HTML file from the database via the specific file-serving route."""
    file = db.get_random_file()
    if file:
        filename = file['filename'].replace(' ', '_')
        return redirect(url_for('serve_file', filename=filename))
    else:
        return 'No files available', 404


@app.route('/wiki/<filename>')
def serve_file(filename):
    """Serve an existing file or generate a missing file."""
    filename = filename.replace('_', ' ')
    file = db.get_file(filename)
    if file:
        return render_template_string(file['content'])
    else:
        retries = 0

        while retries <= N_GENERATION_RETRIES:
            try:
                content = generate_file(filename)
                break
            except Exception as e:
                if retries >= N_GENERATION_RETRIES:
                    return "Internal server error. Please try again later.", 500

                retries += 1

        db.add_file(filename, content)
        return render_template_string(content)


@app.route('/static/images/<path:filename>')
def serve_loading_image(filename):
    """We generate these images async, so we need to wait until the file becomes available"""
    timeout = 10000
    interval = 250

    path = f'static/images/{filename}'
    while not os.path.exists(path) and timeout > 0:
        time.sleep(min(interval, timeout) / 1000)
        timeout -= interval

    if os.path.exists(path):
        return send_from_directory('static/images', filename)
    else:
        return 'Image not found', 404


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files like CSS and JS."""
    return send_from_directory('static', filename)


@app.route('/api/fetch_titles')
def fetch_titles():
    """Fetch all titles from the database."""
    titles = db.get_filenames()
    return jsonify([title['filename'] for title in titles])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
