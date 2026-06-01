# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Configuraciones Generales de la Aplicación Flask (Back-End)
Autor: Grupo 4 - Universidad Peruana
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

class Config:
    """Configuración base de la API Flask."""
    SECRET_KEY = os.getenv("SECRET_KEY", "integritycheck_super_secret_key_12345!")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "integritycheck_jwt_secret_key_67890!")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 8))
    
    # Servidor Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # Parámetros Base de Datos SQL Server
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_DATABASE = os.getenv("DB_DATABASE", "IntegrityCheckAI")
    DB_PORT = os.getenv("DB_PORT", "1433")
    DB_USERNAME = os.getenv("DB_USERNAME", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "True")

    # Rutas para el Motor de IA
    MODELOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ML", "modelos"))
