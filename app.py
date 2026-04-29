from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__, template_folder=os.path.join('birds', 'templates'))

DB_PATH = os.path.join('birds', 'ptaci.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ptaci ORDER BY nazev ASC')
    ptaci = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', ptaci=ptaci)

if __name__ == "__main__":
    app.run(debug=True)