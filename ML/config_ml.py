# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Configuraciones Generales de la Capa de Machine Learning
Autor: Grupo 4 - Universidad Peruana
"""

import os

# Obtener directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")

# Crear carpeta de modelos si no existe
if not os.path.exists(MODELOS_DIR):
    os.makedirs(MODELOS_DIR)

# Rutas exactas para guardar los archivos pkl serializados
RUTA_MODELO_RIESGO = os.path.join(MODELOS_DIR, "modelo_riesgo.pkl")
RUTA_MODELO_PLAGIO = os.path.join(MODELOS_DIR, "modelo_plagio.pkl")
RUTA_MODELO_ANOMALIA = os.path.join(MODELOS_DIR, "modelo_anomalia.pkl")

# Características utilizadas en el modelo de Riesgo de Fraude (Random Forest)
FEATURES_RIESGO = [
    "promedio_notas_ciclo",
    "variacion_nota",
    "porcentaje_similitud",
    "tiempo_respuesta_examen",
    "accesos_lms_semana",
    "cambios_ip_examen"
]

# Configuración del NLP para detección de plagio
NLP_MAX_FEATURES = 5000
NLP_NGRAM_RANGE = (1, 2)
UMBRAL_PLAGIO_DEFECTO = 45.0  # Umbral en porcentaje (%)

# Configuración de detección de anomalías (Isolation Forest)
ANOMALY_CONTAMINATION = 0.05  # Proporción esperada de anomalías (5%)
FEATURES_ANOMALIA = [
    "nota_actual",
    "nota_anterior",
    "variacion_nota",
    "accesos_lms_semana"
]
