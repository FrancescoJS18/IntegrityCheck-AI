# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase de Conexión a la Base de Datos SQL Server
Autor: Grupo 4 - Universidad Peruana
"""

import os
import sys
import logging
import pyodbc
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConexionBD:
    """Clase para manejar la conexión y transacciones con la base de datos SQL Server."""
    
    def __init__(self, server: Optional[str] = None, database: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None, 
                 port: Optional[str] = None, trusted: bool = True) -> None:
        """
        Inicializa los parámetros de conexión buscando primero en variables de entorno.
        """
        self.server = server or os.getenv("DB_SERVER", "localhost")
        self.database = database or os.getenv("DB_DATABASE", "IntegrityCheckAI")
        self.username = username or os.getenv("DB_USERNAME", "")
        self.password = password or os.getenv("DB_PASSWORD", "")
        self.port = port or os.getenv("DB_PORT", "1433")
        
        # Determinar si usamos autenticación de Windows o SQL Server Auth
        env_trusted = os.getenv("DB_TRUSTED_CONNECTION", "True")
        self.trusted = trusted if env_trusted.lower() in ("true", "1", "yes") else False
        
        self.conn: Optional[pyodbc.Connection] = None
        self.mock_mode: bool = False
        
    def obtener_conexion(self) -> Optional[pyodbc.Connection]:
        """
        Establece la conexión pyodbc con SQL Server. 
        Si falla, activa un modo simulado (mock_mode) para no romper el flujo del backend.
        """
        if self.conn:
            try:
                # Comprobar que siga abierta
                self.conn.cursor()
                return self.conn
            except Exception:
                self.conn = None
                
        # Construir Connection String
        # Nota: Usamos ODBC Driver 17 o 18 para SQL Server, que son los estándar
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        driver = next((d for d in drivers if '17' in d or '18' in d), drivers[0] if drivers else 'ODBC Driver 17 for SQL Server')
        
        conn_str = f"DRIVER={{{driver}}};SERVER={self.server},{self.port};DATABASE={self.database};"
        
        if self.trusted or not self.username:
            conn_str += "Trusted_Connection=yes;"
        else:
            conn_str += f"UID={self.username};PWD={self.password};"
            
        # SQL Server 2022 requiere encriptación predeterminada si usa Driver 18, añadimos TrustServerCertificate
        if "Driver 18" in driver:
            conn_str += "Encrypt=yes;TrustServerCertificate=yes;"
            
        try:
            logging.info(f"Intentando conectar a SQL Server con: {driver} en {self.server}:{self.port}")
            self.conn = pyodbc.connect(conn_str, timeout=3)
            self.mock_mode = False
            logging.info("Conexión exitosa a SQL Server.")
            return self.conn
        except Exception as e:
            logging.error(f"Error de conexión a SQL Server: {e}")
            logging.warning("Iniciando en MODO SIMULADO (MOCK MODE). Los datos se generarán dinámicamente en Python.")
            self.mock_mode = True
            return None

    def ejecutar_consulta(self, query: str, params: tuple = ()) -> list:
        """
        Ejecuta consultas de lectura SELECT y retorna una lista de diccionarios.
        """
        conexion = self.obtener_conexion()
        if self.mock_mode or not conexion:
            # Retorna lista vacía; las clases CRUD hijas implementarán fallbacks realistas
            return []
            
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute(query, params)
            columnas = [columna[0] for columna in cursor.description]
            resultados = []
            for fila in cursor.fetchall():
                resultados.append(dict(zip(columnas, fila)))
            return resultados
        except Exception as e:
            logging.error(f"Error al ejecutar consulta SELECT: {e}. Query: {query}")
            return []
        finally:
            if cursor:
                cursor.close()

    def ejecutar_comando(self, query: str, params: tuple = ()) -> bool:
        """
        Ejecuta comandos DML (INSERT, UPDATE, DELETE, Stored Procedure).
        """
        conexion = self.obtener_conexion()
        if self.mock_mode or not conexion:
            return False
            
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute(query, params)
            conexion.commit()
            return True
        except Exception as e:
            logging.error(f"Error al ejecutar comando SQL: {e}. Query: {query}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
                
    def cerrar_conexion(self) -> None:
        """Cierra la conexión actual."""
        if self.conn:
            try:
                self.conn.close()
                logging.info("Conexión a base de datos cerrada.")
            except Exception:
                pass
            self.conn = None
