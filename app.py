from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_usage():
    app_name = request.form['app_name']
    minutes = request.form['minutes']

    conn = sqlite3.connect("detox.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usage_logs(app_name, usage_minutes) VALUES (?, ?)",
        (app_name, minutes)
    )

    conn.commit()
    conn.close()

    return "Usage Added Successfully"

@app.route('/view')
def view_usage():
    conn = sqlite3.connect("detox.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usage_logs")
    data = cursor.fetchall()

    conn.close()

    return render_template('usage.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)