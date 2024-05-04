from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
import sqlite3
import os
import time

from utils import generate_file

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'file_database.db')
N_GENERATION_RETRIES = 3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by names
    return conn


def init_db():
    """Initialize the database and create the 'files' table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()


if not os.path.exists(DATABASE_PATH):
    init_db()


@app.route('/')
@app.route('/index')
@app.route('/wiki')
def serve_random_file():
    """Redirect to serve a random HTML file from the database via the specific file-serving route."""
    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files ORDER BY RANDOM() LIMIT 1;").fetchone()
    conn.close()
    if file:
        filename = file['filename'].replace(' ', '_')
        return redirect(url_for('serve_file', filename=filename))
    else:
        return 'No files available', 404


@app.route('/wiki/<filename>')
def serve_file(filename):
    """Serve an existing file or generate a missing file."""
    filename = filename.replace('_', ' ')
    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files WHERE filename = ?", (filename,)).fetchone()
    conn.close()
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

        conn = get_db_connection()
        conn.execute("INSERT INTO files (filename, content) VALUES (?, ?)", (filename, content))
        conn.commit()
        conn.close()
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
    conn = get_db_connection()
    titles = conn.execute("SELECT filename FROM files;").fetchall()
    conn.close()
    return jsonify([title['filename'] for title in titles])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
