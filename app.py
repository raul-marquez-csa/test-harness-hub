from flask import Flask, request, jsonify, render_template
import os
import subprocess
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

def get_git_details(directory):
    details = {
        'repo_name': os.path.basename(directory),
        'commit_sha': '',
        'commit_message': '',
        'commit_author': '',
        'commit_date': '',
        'branch': ''
    }
    try:
        # Get the current branch or HEAD
        status = subprocess.check_output(['git', '-C', directory, 'status'], stderr=subprocess.STDOUT)
        status_lines = status.decode('utf-8').splitlines()

        if 'HEAD detached at' in status_lines[0]:
            details['branch'] = status_lines[0].strip()
        else:
            branch_parts = status_lines[0].split(' ')
            local_branch = branch_parts[2]
            try:
                tracking_branch = subprocess.check_output(['git', '-C', directory, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], stderr=subprocess.STDOUT)
                tracking_branch = tracking_branch.decode('utf-8').strip()
                details['branch'] = f"{local_branch} (tracking {tracking_branch})"
            except subprocess.CalledProcessError:
                details['branch'] = local_branch

        # Get the last commit details
        log = subprocess.check_output(['git', '-C', directory, 'log', '-1', '--pretty=format:%H%n%s%n%an%n%ad'], stderr=subprocess.STDOUT)
        log_lines = log.decode('utf-8').splitlines()
        details['commit_sha'] = log_lines[0]
        details['commit_message'] = log_lines[1]
        details['commit_author'] = log_lines[2]
        details['commit_date'] = log_lines[3]

    except subprocess.CalledProcessError as e:
        details['error'] = e.output.decode('utf-8') if hasattr(e, 'output') else str(e)
    return details

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify-folder', methods=['POST'])
def verify_folder():
    data = request.get_json()
    folder_path = data.get('folder_path', '')

    # Log the received folder path
    app.logger.info(f"Received folder path: {folder_path}")

    # Expand the user directory and normalize the path
    expanded_path = os.path.expanduser(folder_path)
    normalized_path = os.path.abspath(expanded_path)
    app.logger.info(f"Normalized folder path: {normalized_path}")

    # Check if the directory exists
    if not os.path.isdir(normalized_path):
        return jsonify(valid=False, message="Directory does not exist")

    # Check git status for the main folder and subfolders
    git_dirs = [
        ('Test Harness', normalized_path),
        ('Frontend', os.path.join(normalized_path, 'frontend')),
        ('Backend', os.path.join(normalized_path, 'backend')),
        ('CLI', os.path.join(normalized_path, 'cli'))
    ]

    git_details = {}
    for name, directory in git_dirs:
        if os.path.isdir(directory):
            git_details[name] = get_git_details(directory)
        else:
            git_details[name] = {'error': 'Directory does not exist'}

    return jsonify(valid=True, git_details=git_details)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('run_command')
def handle_run_command(command):
    # Execute the command here and emit the output back to the client
    output = f"Executed command: {command}"  # Replace with actual command execution
    socketio.emit('command_output', {'data': output})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
