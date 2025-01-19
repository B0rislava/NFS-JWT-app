import logging
import os
from functools import wraps

import jwt
from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        print(f"Decode token with key {app.config['SECRET_KEY']}")
        try:
            jwt.decode(token, app.config['SECRET_KEY'], options={"verify_signature": False}, algorithms=['RS256'])
        except Exception as e:
            print(e)
            return jsonify({'message': 'Invalid token'}), 403

        return func(*args, **kwargs)

    return decorated

# 1. POST /file/upload: Качва нов файл.
@app.route('/file/upload', methods=['POST'])
@token_required
def upload_file():

    if 'file' in request.files:
        f = request.files['file']
        file_name = secure_filename(f.filename)
        print(f"Target file : {f.filename}")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        return "Success", 201

    return "Invalid request data", 400


# 2. GET /file/{file_id}: Връща съдържанието на файл по идентификатор.
# 3. PUT /file/{file_id}: Обновява съдържанието на съществуващ файл.
# 4. DELETE /file/{file_id}: Изтрива файл по идентификатор.
@app.route('/file/<file_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def get_file(file_id):
    file_path: str = str(os.path.join(app.config['UPLOAD_FOLDER'], file_id))
    if os.path.isfile(file_path) is False:
        return "File not found", 404

    if request.method == 'GET':
        return send_file(file_path, as_attachment=True)

    elif request.method == 'PUT':
        content = request.form['content']
        with open(file_path, "w") as f:
            f.write(content)
        return "Success", 201

    elif request.method == 'DELETE':
        os.remove(file_path)
        return "File deleted", 204

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)
