from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
import sqlite3
import os

from utils import generate_file

app = Flask(__name__)
DATABASE_PATH = 'file_database.db'


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


@app.route('/')
@app.route('/index')
@app.route('/wiki')
def serve_random_file():
    """Redirect to serve a random HTML file from the database via the specific file-serving route."""
    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files ORDER BY RANDOM() LIMIT 1;").fetchone()
    conn.close()
    if file:
        return redirect(url_for('serve_file', filename=file['filename']))
    else:
        return 'No files available', 404


@app.route('/wiki/<filename>')
def serve_file(filename):
    """Serve an existing file or generate a missing file."""
    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files WHERE filename = ?", (filename,)).fetchone()
    conn.close()
    if file:
        print("File found in database")
        return render_template_string(file['content'])
    else:
        print("File not found in database")
        content = generate_file(filename)  # Generate file dynamically
        conn = get_db_connection()
        conn.execute("INSERT INTO files (filename, content) VALUES (?, ?)", (filename, content))
        conn.commit()
        conn.close()
        return render_template_string(content)


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files like CSS and JS."""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    if not os.path.exists(DATABASE_PATH):
        init_db()
    app.run(debug=True, port=5001)
