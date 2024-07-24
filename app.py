import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('run_command')
def handle_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for stdout_line in iter(process.stdout.readline, ''):
        emit('command_output', {'data': stdout_line})
    process.stdout.close()
    
    for stderr_line in iter(process.stderr.readline, ''):
        emit('command_output', {'data': stderr_line})
    process.stderr.close()

    process.wait()

if __name__ == '__main__':
    socketio.run(app, debug=True)
