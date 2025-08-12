from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short TEXT UNIQUE,
                original TEXT NOT NULL
            )
        """)

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_code = generate_short_code()

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short_code, original_url))
            conn.commit()
        short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_to_original(short_code):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original FROM urls WHERE short = ?", (short_code,))
        result = cursor.fetchone()
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
