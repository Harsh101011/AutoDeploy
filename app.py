import os
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        ''')
        mysql.connection.commit()  
        cur.close()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id, 'message': new_message})

@app.route('/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM messages WHERE id = %s', [msg_id])
    mysql.connection.commit()
    cur.close()
    return jsonify({'status': 'success'})

def wait_for_db():
    while True:
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.close()
                break
        except Exception as e:
            print(f"Waiting for MySQL... ({e})")
            time.sleep(2)

# Initialize database before handling requests
wait_for_db()
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
