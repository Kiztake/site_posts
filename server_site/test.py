from flask import Flask, jsonify
from flask import render_template, url_for, request, session, redirect
import os, sqlite3


def opendb():
    global db, cursor
    db = sqlite3.connect('file.db')
    cursor = db.cursor()

def closedb():
    cursor.close()
    db.close()

app = Flask(__name__)

@app.route('/test', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        checkbox = request.form.get('check')

        if checkbox:
            return 'activated'
        return 'not activated'
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)