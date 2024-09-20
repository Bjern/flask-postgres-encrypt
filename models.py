import uuid

from cryptography.fernet import Fernet
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
from sqlalchemy import Column, String, DateTime
from flask import current_app

from app import db

cipher = Fernet(current_app.config['ENCRYPTION_KEY'])


# Create a custom TypeDecorator for encrypted fields
class EncryptedType(TypeDecorator):
    impl = db.Text  # This defines how the field is stored in the DB

    def process_bind_param(self, value, dialect):
        """Encrypt data before storing it."""
        if value is None:
            return None
        return cipher.encrypt(value.encode('utf-8')).decode('utf-8')

    def process_result_value(self, value, dialect):
        """Decrypt data when reading from the database."""
        if value is None:
            return None
        return cipher.decrypt(value.encode('utf-8')).decode('utf-8')


# Custom metaclass for encryption behavior with Flask-SQLAlchemy's db.Model
class EncryptedMeta(type(db.Model)):
    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)

        encrypted_columns = getattr(self, '__encrypted_columns__', [])
        for column in encrypted_columns:
            if column in dct:
                original_column = dct[column]
                if isinstance(original_column, Column):
                    # Modify the existing column rather than creating a new one
                    original_column.type = EncryptedType()


class User(db.Model, metaclass=EncryptedMeta):
    __encrypted_columns__ = ['email', 'first_name', 'last_name']  # Fields to encrypt

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(String, nullable=False)
    first_name = db.Column(String, nullable=False)
    last_name = db.Column(String, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
