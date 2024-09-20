import json

from flask import Flask, request, abort, Response, jsonify
from flask_migrate import Migrate
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, NoResultFound

db = SQLAlchemy()

# Init app
app = Flask(__name__)
app.config.from_object('config.Config')

# Database init
with app.app_context():
    db.init_app(app)
    from models import User
    Migrate(app, db)


@app.route('/')
def index():
    return 'You are not authorized to view this page!'


@app.route('/encrypt-data', methods=['POST'])
def generate_encrypted_response():
    """
    Generates an encrypted JWE string that you can use for testing.
    :param: Pass any JSON string to be converted
    :return: Encrypted string
    """
    data = request.get_data(as_text=True)
    if data:
        # Load the RSA public key (for encrypting the data)
        with open('public.pem', 'rb') as f:
            public_key = jwk.JWK.from_pem(f.read())

        payload = data.encode('utf-8')

        # Create the JWE object
        jwe_token = jwe.JWE(payload, json_encode({"alg": "RSA-OAEP", "enc": "A256GCM"}))
        jwe_token.add_recipient(public_key)
        jwe_token.serialize(compact=True)

        return jwe_token.serialize()

    abort(400)


@app.route('/register-user', methods=['POST'])
def register_user_information():
    """
    Store posted encrypted user data.
    :param: Pass any data, already encrypted for storage
    :return: Success response
    """
    if request.data:
        data = request.get_data(as_text=True)

        # Decrypt payload
        # Load the RSA private key (for decrypting the incoming JWE)
        with open('private.pem', 'rb') as f:
            private_key = jwk.JWK.from_pem(f.read())

        jwe_token = jwe.JWE()
        jwe_token.deserialize(data)
        jwe_token.decrypt(private_key)

        decrypted_payload = jwe_token.payload
        decrypted_data = json.loads(decrypted_payload.decode('utf-8'))

        try:
            user_data = User(**decrypted_data)
            db.session.add(user_data)
            db.session.commit()

            return Response(json.dumps({'status': 'success', 'id': str(user_data.id)}), 200)

        except IntegrityError:
            error_message = json.dumps({'message': 'There was a problem saving your data.'})
            abort(Response(error_message, 400))

    abort(400)


@app.route('/get-user/<string:user_id>', methods=['GET'])
def get_user_information(user_id):
    """
    Get the users information already stored, from postgres in its decrypted state and return it
    :param user_id: The users identification ID
    :return: User data
    """
    if request.method == 'GET':
        try:
            user = db.session.query(User).filter_by(id=user_id).first()

            return Response(
                json.dumps(
                    {
                        'status': 'user found',
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email
                    }
                ), 200)

        except NoResultFound:
            abort(404)

    abort(404)
