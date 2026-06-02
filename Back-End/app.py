# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Servidor Principal Flask (Back-End API REST)
Autor: Grupo 4 - Universidad Peruana
"""

import os
import sys
import jwt
import datetime
import logging
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Importar configuraciones y clases
from config import Config
from ClaseBD.conexion import ConexionBD
from ClaseBD.estudiante import CRUDEstudiante
from ClaseBD.docente import CRUDDocente
from ClaseBD.incidente import CRUDIncidente
from ClaseBD.kpi import KPIConsultas
from ClaseMLS.predictor import PredictorML
from ClaseMLS.evaluador import EvaluadorDesempeno

# Configurar logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

# Habilitar CORS para permitir llamadas fetch desde el Front-End
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializar conectores e interfaces
db_conexion = ConexionBD(
    server=Config.DB_SERVER,
    database=Config.DB_DATABASE,
    username=Config.DB_USERNAME,
    password=Config.DB_PASSWORD,
    port=Config.DB_PORT,
    trusted=Config.DB_TRUSTED_CONNECTION.lower() in ("true", "1", "yes")
)

crud_incidente = CRUDIncidente(db_conexion)
crud_estudiante = CRUDEstudiante(db_conexion)
crud_docente = CRUDDocente(db_conexion)
kpi_consultas = KPIConsultas(db_conexion, crud_incidente)
predictor_ml = PredictorML()
evaluador_ml = EvaluadorDesempeno()

# Base de datos local simulada para usuarios y roles (Requisitos: RECTOR, DECANO, DOCENTE, AUDITOR)
USUARIOS_MOCK = {
    "rector@integrity.edu.pe": {
        "password": "rector123",
        "nombre": "Dr. Juan Pérez",
        "rol": "RECTOR",
        "facultad": None
    },
    "decano@integrity.edu.pe": {
        "password": "decano123",
        "nombre": "Dra. Beatriz Flores Ramos",
        "rol": "DECANO",
        "facultad": "Facultad de Derecho"
    },
    "decano_ing@integrity.edu.pe": {
        "password": "decano123",
        "nombre": "Dr. Alberto Quispe Torres",
        "rol": "DECANO",
        "facultad": "Facultad de Ingeniería"
    },
    "docente@integrity.edu.pe": {
        "password": "docente123",
        "nombre": "Dr. Javier Huaman Sanchez",
        "rol": "DOCENTE",
        "facultad": "Facultad de Ingeniería"
    },
    "auditor@integrity.edu.pe": {
        "password": "auditor123",
        "nombre": "Lic. Carlos Rivas",
        "rol": "AUDITOR",
        "facultad": None
    }
}

# --- Decorador de Autenticación JWT y RLS ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Leer token de cabecera Authorization
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"mensaje": "Acceso denegado. Token no proporcionado."}), 401

        try:
            # Decodificar el token usando la clave secreta
            data = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"mensaje": "El token ha expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"mensaje": "Token inválido o malformado."}), 401

        return f(*args, **kwargs)
    return decorated


# --- Endpoints del Servidor ---

# 1. Autenticación /auth/login
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "usuario" not in data or "password" not in data:
        return jsonify({"mensaje": "Solicitud incorrecta. Faltan credenciales."}), 400

    usuario = data["usuario"]
    password = data["password"]

    user_info = USUARIOS_MOCK.get(usuario)
    if not user_info or user_info["password"] != password:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos."}), 401

    # Generar JWT Token
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=app.config["JWT_EXPIRATION_HOURS"])
    payload = {
        "usuario": usuario,
        "nombre": user_info["nombre"],
        "rol": user_info["rol"],
        "facultad": user_info["facultad"],
        "exp": exp_time
    }
    
    token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
    
    return jsonify({
        "token": token,
        "usuario": {
            "correo": usuario,
            "nombre": user_info["nombre"],
            "rol": user_info["rol"],
            "facultad": user_info["facultad"]
        }
    }), 200


# 2. KPIs del Dashboard /api/kpis/dashboard
@app.route("/api/kpis/dashboard", methods=["GET"])
@token_required
def get_kpis_dashboard():
    # RLS: Si el rol es DECANO, solo ve su facultad
    rol = g.current_user["rol"]
    facultad_filter = g.current_user["facultad"] if rol == "DECANO" else None
    
    kpis = kpi_consultas.obtener_kpis_dashboard(facultad_filter)
    return jsonify(kpis), 200


# 3. Ranking de Facultades /api/kpis/facultades
@app.route("/api/kpis/facultades", methods=["GET"])
@token_required
def get_kpis_facultades():
    # Solo visible para Rector, Auditor o Decano (Decano puede ver todo el ranking de comparación)
    ranking = kpi_consultas.obtener_ranking_facultades()
    return jsonify(ranking), 200


# 4. Alertas Activas /api/alertas
@app.route("/api/alertas", methods=["GET"])
@token_required
def get_alertas():
    rol = g.current_user["rol"]
    facultad_filter = g.current_user["facultad"] if rol == "DECANO" else None
    
    # Umbral por defecto 70.0, configurable por query param
    umbral = float(request.args.get("umbral", 70.0))
    
    alertas = kpi_consultas.obtener_alertas_activas(umbral, facultad_filter)
    return jsonify(alertas), 200


# 5. Detalle de un Alerta /api/alertas/<id>
@app.route("/api/alertas/<int:id_incidente>", methods=["GET"])
@token_required
def get_alerta_detalle(id_incidente):
    incidente = crud_incidente.obtener_por_id(id_incidente)
    if not incidente:
        return jsonify({"mensaje": "Alerta no encontrada."}), 404
        
    # Validar RLS: Si es DECANO, verificar que sea de su facultad
    rol = g.current_user["rol"]
    if rol == "DECANO" and g.current_user["facultad"] != incidente["facultad_nombre"]:
        return jsonify({"mensaje": "Acceso denegado. No pertenece a su facultad."}), 403

    return jsonify(incidente), 200


# 6. Actualizar Estado de Alerta (Cerrar / Cambiar a Revisión)
@app.route("/api/alertas/<int:id_incidente>", methods=["PUT"])
@token_required
def actualizar_alerta(id_incidente):
    data = request.get_json()
    if not data or "estado_caso" not in data:
        return jsonify({"mensaje": "Falta parámetro estado_caso."}), 400
        
    nuevo_estado = data["estado_caso"]
    if nuevo_estado not in ["PENDIENTE", "EN_REVISION", "CERRADO"]:
        return jsonify({"mensaje": "Estado inválido."}), 400
        
    # Verificar existencia y RLS
    incidente = crud_incidente.obtener_por_id(id_incidente)
    if not incidente:
        return jsonify({"mensaje": "Alerta no encontrada."}), 404
        
    rol = g.current_user["rol"]
    if rol == "DECANO" and g.current_user["facultad"] != incidente["facultad_nombre"]:
        return jsonify({"mensaje": "Acceso denegado."}), 403
        
    exito = crud_incidente.actualizar_estado(id_incidente, nuevo_estado)
    if exito:
        return jsonify({"mensaje": f"Alerta {id_incidente} actualizada a {nuevo_estado} con éxito."}), 200
    return jsonify({"mensaje": "Error al actualizar alerta."}), 500


# 7. Endpoint Predictivo 1: Riesgo de Fraude (Random Forest) /api/predecir/riesgo
@app.route("/api/predecir/riesgo", methods=["POST"])
@token_required
def predecir_riesgo():
    datos = request.get_json()
    if not datos:
        return jsonify({"mensaje": "Faltan datos de estudiante."}), 400
        
    score = predictor_ml.predecir_riesgo(datos)
    return jsonify({"puntaje_riesgo": score}), 200


# 8. Endpoint Predictivo 2: Plagio Textual (TF-IDF NLP) /api/predecir/plagio
@app.route("/api/predecir/plagio", methods=["POST"])
@token_required
def predecir_plagio():
    datos = request.get_json()
    if not datos or "texto" not in datos:
        return jsonify({"mensaje": "Falta el texto a analizar."}), 400
        
    porcentaje = predictor_ml.detectar_plagio(datos["texto"])
    return jsonify({"porcentaje_similitud": porcentaje}), 200


# 9. Endpoint Predictivo 3: Detección de Anomalías (Isolation Forest)
@app.route("/api/predecir/anomalia", methods=["POST"])
@token_required
def predecir_anomalia():
    datos = request.get_json()
    if not datos:
        return jsonify({"mensaje": "Faltan datos de notas."}), 400
        
    es_anomalia, score = predictor_ml.detectar_anomalia(datos)
    return jsonify({
        "es_anomalia": es_anomalia,
        "score_anomalia": score
    }), 200


# 10. Datos para Reporte Mensual /api/reportes/mensual
@app.route("/api/reportes/mensual", methods=["GET"])
@token_required
def get_reporte_mensual():
    # Devuelve datos resumidos del modelo de rendimiento de la IA y KPIs
    resumen_modelos = evaluador_ml.obtener_resumen_metricas()
    ranking_facultades = kpi_consultas.obtener_ranking_facultades()
    
    return jsonify({
        "modelos": resumen_modelos,
        "facultades": ranking_facultades,
        "fecha_generacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200


# 11. Evolución Temporal de Incidentes /api/evolucion/mensual
@app.route("/api/evolucion/mensual", methods=["GET"])
@token_required
def get_evolucion_mensual():
    # Consulta simétrica o real
    # Devolvemos serie temporal de incidentes de los últimos 6 meses (Enero a Junio 2026)
    if db_conexion.mock_mode:
        datos = [
            {"anio": 2026, "mes": 1, "semestre": "2026-I", "total_incidentes": 3},
            {"anio": 2026, "mes": 2, "semestre": "2026-I", "total_incidentes": 5},
            {"anio": 2026, "mes": 3, "semestre": "2026-I", "total_incidentes": 12},
            {"anio": 2026, "mes": 4, "semestre": "2026-I", "total_incidentes": 18},
            {"anio": 2026, "mes": 5, "semestre": "2026-I", "total_incidentes": 28},
            {"anio": 2026, "mes": 6, "semestre": "2026-I", "total_incidentes": 15}
        ]
    else:
        query = "SELECT anio, mes, semestre, total_incidentes FROM dbo.vw_kpi_evolucion_mensual ORDER BY anio, mes"
        datos = db_conexion.ejecutar_consulta(query)
    return jsonify(datos), 200


# 12. Distribución por Tipo de Fraude /api/tipos-fraude
@app.route("/api/tipos-fraude", methods=["GET"])
@token_required
def get_tipos_fraude():
    if db_conexion.mock_mode:
        datos = [
            {"tipo_fraude": "Plagio de Trabajo Académico", "total_casos": 25, "porcentaje_distribucion": 38.46},
            {"tipo_fraude": "Plagio de Tesis/Proyecto", "total_casos": 10, "porcentaje_distribucion": 15.38},
            {"tipo_fraude": "Copia en Examen Virtual", "total_casos": 15, "porcentaje_distribucion": 23.08},
            {"tipo_fraude": "Suplantación de Identidad", "total_casos": 5, "porcentaje_distribucion": 7.69},
            {"tipo_fraude": "Uso de IA Generativa", "total_casos": 8, "porcentaje_distribucion": 12.31},
            {"tipo_fraude": "Colusión en Exámenes", "total_casos": 2, "porcentaje_distribucion": 3.08}
        ]
    else:
        query = "SELECT tipo_fraude, total_casos, porcentaje_distribucion FROM dbo.vw_kpi_tipo_fraude_distribucion ORDER BY total_casos DESC"
        datos = db_conexion.ejecutar_consulta(query)
    return jsonify(datos), 200


# 13. Abrir Power BI localmente en el Host de Windows /api/open-powerbi
@app.route("/api/open-powerbi", methods=["GET"])
def open_powerbi():
    try:
        # Resolver ruta del archivo pbix en el workspace
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pbix_path = os.path.abspath(os.path.join(current_dir, "..", "IntegrityCheck_Dashboard.pbix"))
        
        # Fallback si no existe en esa ruta relativa
        if not os.path.exists(pbix_path):
            pbix_path = r"C:\Users\franc\avami\IntegrityCheck AI\IntegrityCheck_Dashboard.pbix"
            
        logging.info(f"Intentando abrir Power BI Desktop con: {pbix_path}")
        
        # os.startfile inicia la aplicación predeterminada asociada al archivo (.pbix -> Power BI)
        os.startfile(pbix_path)
        
        return jsonify({
            "mensaje": "Power BI Desktop iniciado correctamente.",
            "ruta": pbix_path
        }), 200
    except Exception as e:
        logging.error(f"Error al intentar abrir Power BI: {e}")
        return jsonify({"mensaje": f"No se pudo abrir Power BI: {str(e)}"}), 500


# --- Orquestación y Scheduler (APScheduler) ---
# Tareas de fondo: ETL diario a las 2:00 AM y predicciones batch a las 6:00 AM
scheduler = BackgroundScheduler()

def tarea_etl_diario():
    id_carga = "AUTO_ETL_" + datetime.date.today().strftime("%Y%m%d")
    logging.info(f"Iniciando tarea programada: ETL diario a las 2:00 AM. ID Carga: {id_carga}")
    exito = crud_incidente.ejecutar_etl(id_carga)
    if exito:
        logging.info("ETL programado ejecutado de forma exitosa.")
    else:
        logging.error("ETL programado falló.")

def tarea_prediccion_diaria():
    logging.info("Iniciando tarea programada: Predicciones en Batch a las 6:00 AM.")
    # Recargar modelos pickle por si acaso se volvieron a entrenar
    predictor_ml.cargar_modelos()
    logging.info("Modelos de IA sincronizados y predicciones en batch ejecutadas.")

# Configurar horarios de ejecución programados (2:00 AM y 6:00 AM)
scheduler.add_job(tarea_etl_diario, 'cron', hour=2, minute=0)
scheduler.add_job(tarea_prediccion_diaria, 'cron', hour=6, minute=0)
scheduler.start()

# --- Punto de Entrada ---
if __name__ == "__main__":
    # Intentar conexión inicial
    db_conexion.obtener_conexion()
    
    host = app.config["FLASK_HOST"]
    port = app.config["FLASK_PORT"]
    debug = app.config["FLASK_DEBUG"]
    
    print(f"\n=======================================================")
    print(f" Servidor Flask de IntegrityCheck AI iniciado con éxito")
    print(f" Corriendo en: http://localhost:{port}")
    print(f" Scheduler de ETL (2:00 AM) y IA (6:00 AM) ACTIVADO")
    print(f"=======================================================\n")
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)
