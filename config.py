import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "RWbKgXV60eLWxma6X5qhtGmiBi1ta3Fi5fVWHJtptdo="
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql+psycopg2://gdpr_admin:gdpr_12345@localhost:5432/gdpr_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY") or "GItkp1wE5iAdHTsYf6INWX1ftR8jjWXMKEO3oPj7cD8="
