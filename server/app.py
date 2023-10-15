from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from sqlalchemy import func
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


# Endpoint to get all messages ordered by created_at in ascending order
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_serialized = [{
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "updated_at": message.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
    } for message in messages]
    return jsonify(messages_serialized)

# Endpoint to create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')

    if body is None or username is None:
        return jsonify(error='Both body and username are required'), 400

    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()

    message_data = {
        "id": new_message.id,
        "body": new_message.body,
        "username": new_message.username,
        "created_at": new_message.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "updated_at": new_message.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
    }

    return jsonify(message_data), 201

# Endpoint to update a message by ID
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)

    if message is None:
        return jsonify(error='Message not found'), 404

    data = request.get_json()
    new_body = data.get('body')

    if new_body:
        message.body = new_body
        db.session.commit()

        message_data = {
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": message.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
        }

        return jsonify(message_data), 200
    else:
        return jsonify(error='No data provided for update'), 400

# Endpoint to delete a message by ID
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)

    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify(message='Message successfully deleted'), 200
    else:
        return jsonify(error='Message not found'), 404
    


if __name__ == '__main__':
    app.run(port=5555)
