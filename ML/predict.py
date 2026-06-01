# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Script de Inferencia/Predicción en Batch
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
import pandas as pd
import numpy as np
from config_ml import RUTA_MODELO_RIESGO, RUTA_MODELO_PLAGIO, RUTA_MODELO_ANOMALIA, FEATURES_RIESGO, FEATURES_ANOMALIA
from sklearn.metrics.pairwise import cosine_similarity

def cargar_modelos():
    """Carga los tres modelos pickle de la carpeta de compilados."""
    try:
        modelo_riesgo = joblib.load(RUTA_MODELO_RIESGO)
        modelo_plagio = joblib.load(RUTA_MODELO_PLAGIO)
        modelo_anomalia = joblib.load(RUTA_MODELO_ANOMALIA)
        return modelo_riesgo, modelo_plagio, modelo_anomalia
    except Exception as e:
        print(f"Error al cargar los modelos serializados (.pkl): {e}")
        print("Asegúrate de ejecutar primero los scripts de entrenamiento 'train_*.py'.")
        return None, None, None

def predecir_batch(datos_alumnos: pd.DataFrame, textos_trabajos: list = None) -> pd.DataFrame:
    """
    Ejecuta la inferencia en batch combinando los 3 modelos.
    Retorna un DataFrame con los puntajes consolidados.
    """
    clf_riesgo, nlp_plagio, clf_anomalia = cargar_modelos()
    if clf_riesgo is None:
        return datos_alumnos

    resultados = datos_alumnos.copy()
    
    # 1. Modelo de Riesgo de Fraude (Random Forest)
    # Validar que contenga todas las columnas requeridas
    for feat in FEATURES_RIESGO:
        if feat not in resultados.columns:
            resultados[feat] = 0.0 # fallback default
            
    X_riesgo = resultados[FEATURES_RIESGO]
    # Guardar la probabilidad de la clase 1 (fraude) convertida a porcentaje 0-100
    resultados["pred_puntaje_riesgo"] = np.round(clf_riesgo.predict_proba(X_riesgo)[:, 1] * 100, 2)
    
    # 2. Modelo de Anomalías (Isolation Forest)
    # Validar columnas
    for feat in FEATURES_ANOMALIA:
        if feat not in resultados.columns:
            resultados[feat] = 0.0
            
    X_anomalia = resultados[FEATURES_ANOMALIA]
    # Isolation Forest retorna 1 para normal y -1 para anómalo. 
    # Mapeamos -1 a True (Anomalía) y 1 a False.
    preds_anomalia = clf_anomalia.predict(X_anomalia)
    resultados["es_anomalia"] = preds_anomalia == -1
    
    # 3. Modelo de Plagio Textual (TF-IDF + Cosine Similarity)
    if nlp_plagio and textos_trabajos:
        vectorizer = nlp_plagio["vectorizer"]
        ref_matrix = nlp_plagio["tfidf_matrix"]
        corpus_ref = nlp_plagio["corpus_referencia"]
        
        similitudes = []
        fragmentos_sospechosos = []
        
        for texto in textos_trabajos:
            if not texto or len(texto.strip()) < 5:
                similitudes.append(0.0)
                fragmentos_sospechosos.append("Texto demasiado corto.")
                continue
                
            # Vectorizar texto entrante
            tfidf_nuevo = vectorizer.transform([texto])
            # Calcular coseno de similitud contra el corpus completo
            sim_scores = cosine_similarity(tfidf_nuevo, ref_matrix)[0]
            max_sim = np.max(sim_scores) * 100 # a porcentaje
            
            # Encontrar el fragmento/documento más similar
            idx_max = np.argmax(sim_scores)
            
            similitudes.append(round(max_sim, 2))
            if max_sim > 45.0:
                fragmentos_sospechosos.append(f"Copia cercana a corpus #{idx_max}: '{corpus_ref[idx_max][:60]}...'")
            else:
                fragmentos_sospechosos.append("Sin coincidencia crítica.")
                
        resultados["pred_porcentaje_similitud"] = similitudes
        resultados["detalle_similitud"] = fragmentos_sospechosos
    else:
        resultados["pred_porcentaje_similitud"] = 0.0
        resultados["detalle_similitud"] = "NLP deshabilitado o sin textos."
        
    return resultados

if __name__ == "__main__":
    print("=== Corriendo Prueba de Predicción en Batch ===")
    
    # Datos de prueba para simular lote entrante de 3 alumnos
    datos_lote = pd.DataFrame([
        # Caso 1: Estudiante normal
        {
            "estudiante": "Juan Quispe",
            "promedio_notas_ciclo": 14.5,
            "nota_anterior": 14.0,
            "nota_actual": 14.8,
            "variacion_nota": 0.8,
            "porcentaje_similitud": 12.0,
            "tiempo_respuesta_examen": 65,
            "accesos_lms_semana": 25,
            "cambios_ip_examen": 0
        },
        # Caso 2: Intento de plagio alto
        {
            "estudiante": "Maria Flores",
            "promedio_notas_ciclo": 11.2,
            "nota_anterior": 11.0,
            "nota_actual": 11.5,
            "variacion_nota": 0.5,
            "porcentaje_similitud": 85.0,
            "tiempo_respuesta_examen": 40,
            "accesos_lms_semana": 12,
            "cambios_ip_examen": 1
        },
        # Caso 3: Anomalía de notas (subió de 05 a 20 sin entrar a Moodle)
        {
            "estudiante": "Jose Sanchez",
            "promedio_notas_ciclo": 8.0,
            "nota_anterior": 5.0,
            "nota_actual": 20.0,
            "variacion_nota": 15.0,
            "porcentaje_similitud": 5.0,
            "tiempo_respuesta_examen": 15,
            "accesos_lms_semana": 1,
            "cambios_ip_examen": 4
        }
    ])
    
    # Textos correspondientes para plagio
    textos_lote = [
        "Este es un trabajo original de investigación sobre la historia de las redes en el Perú.",
        "Los principios de la constitución peruana de 1993 establecen un modelo económico social de mercado basado en la libre competencia e inversión.",
        "Un examen rápido sin mucho sentido textual."
    ]
    
    df_predicciones = predecir_batch(datos_lote, textos_lote)
    
    print("\nResultados de la Predicción en Batch:")
    print(df_predicciones[["estudiante", "pred_puntaje_riesgo", "es_anomalia", "pred_porcentaje_similitud", "detalle_similitud"]])
