import sqlite3
import os


class FileDB:
    def __init__(self, load_dir=None):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        self.conn.commit()

        if load_dir:
            self.load_dir(load_dir)

    def add_file(self, filename, content):
        self.conn.execute("INSERT INTO files (filename, content) VALUES (?, ?)", (filename, content))
        self.conn.commit()

    def get_file(self, filename):
        return self.conn.execute("SELECT * FROM files WHERE filename = ?", (filename,)).fetchone()

    def get_random_file(self):
        return self.conn.execute("SELECT * FROM files ORDER BY RANDOM() LIMIT 1;").fetchone()

    def get_filenames(self):
        return self.conn.execute("SELECT filename FROM files;").fetchall()

    def load_dir(self, d):
        # load every file in the directory
        for file in os.listdir(d):
            with open(os.path.join(d, file), 'r') as f:
                filename = os.path.splitext(file)[0]
                content = f.read()
                self.add_file(filename, content)

    def close(self):
        self.conn.close()
