from flask import Flask, request, jsonify, send_from_directory, abort
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for all routes
auth = HTTPBasicAuth()

users = {
    "admin": "password123"  # Change this for production
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

@app.route('/upload', methods=['PUT'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or file type not allowed'}), 400
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({'message': 'File uploaded successfully'}), 201

@app.route('/download/<filename>', methods=['GET'])
@auth.login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
@auth.login_required
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully'}), 204
    return jsonify({'error': 'File not found'}), 404

@app.route('/list', methods=['GET'])
@auth.login_required
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/bucket/create/<bucket_name>', methods=['POST'])
@auth.login_required
def create_bucket(bucket_name):
    bucket_path = os.path.join(app.config['UPLOAD_FOLDER'], bucket_name)
    if not os.path.exists(bucket_path):
        os.makedirs(bucket_path)
        return jsonify({'message': f'Bucket {bucket_name} created successfully'}), 201
    return jsonify({'error': 'Bucket already exists'}), 400

@app.route('/bucket/list', methods=['GET'])
@auth.login_required
def list_buckets():
    buckets = [d for d in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], d))]
    return jsonify(buckets)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
