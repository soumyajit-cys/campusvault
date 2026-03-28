import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY        = os.getenv("SECRET_KEY", "fallback-secret")
    JWT_SECRET        = os.getenv("JWT_SECRET", "fallback-jwt-secret")
    FACULTY_CODE      = os.getenv("FACULTY_CODE", "FACULTY2024")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///campusvault.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False