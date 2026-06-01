# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase Interfaz del Motor Predictivo ML
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from ClaseMLS.preprocesador import PreprocesadorDatos
from sklearn.metrics.pairwise import cosine_similarity

class PredictorML:
    """Clase principal de interfaz para realizar predicciones y evaluar riesgos."""
    
    def __init__(self, modelos_dir: str = None) -> None:
        # Resolver directorio de modelos
        if not modelos_dir:
            # Asumimos estructura: SIS/Back-End/ClaseMLS/../../ML/modelos/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.modelos_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "ML", "modelos"))
        else:
            self.modelos_dir = modelos_dir
            
        self.ruta_riesgo = os.path.join(self.modelos_dir, "modelo_riesgo.pkl")
        self.ruta_plagio = os.path.join(self.modelos_dir, "modelo_plagio.pkl")
        self.ruta_anomalia = os.path.join(self.modelos_dir, "modelo_anomalia.pkl")
        
        self.preprocesador = PreprocesadorDatos()
        
        # Atributos para los modelos cargados
        self.modelo_riesgo = None
        self.modelo_plagio = None
        self.modelo_anomalia = None
        
        self.cargar_modelos()

    def cargar_modelos(self) -> None:
        """Carga los modelos desde el disco si existen."""
        # Cargar Modelo Riesgo
        if os.path.exists(self.ruta_riesgo):
            try:
                self.modelo_riesgo = joblib.load(self.ruta_riesgo)
                logging.info("Modelo de riesgo cargado correctamente.")
            except Exception as e:
                logging.error(f"Error al cargar modelo de riesgo: {e}")
        else:
            logging.warning(f"No se encontró el archivo del modelo de riesgo: {self.ruta_riesgo}")

        # Cargar Modelo Plagio
        if os.path.exists(self.ruta_plagio):
            try:
                self.modelo_plagio = joblib.load(self.ruta_plagio)
                logging.info("Modelo NLP de plagio cargado correctamente.")
            except Exception as e:
                logging.error(f"Error al cargar modelo de plagio: {e}")
        else:
            logging.warning(f"No se encontró el archivo del modelo de plagio: {self.ruta_plagio}")

        # Cargar Modelo Anomalías
        if os.path.exists(self.ruta_anomalia):
            try:
                self.modelo_anomalia = joblib.load(self.ruta_anomalia)
                logging.info("Modelo de anomalías cargado correctamente.")
            except Exception as e:
                logging.error(f"Error al cargar modelo de anomalías: {e}")
        else:
            logging.warning(f"No se encontró el archivo del modelo de anomalías: {self.ruta_anomalia}")

    def predecir_riesgo(self, datos_estudiante: Dict[str, Any]) -> float:
        """
        Retorna el score de riesgo de fraude (0 a 100).
        """
        # Preparar datos
        df_vector = self.preprocesador.preparar_vector_riesgo(datos_estudiante)
        
        if self.modelo_riesgo:
            try:
                # Predecir probabilidad de la clase 1 (fraude)
                prob = self.modelo_riesgo.predict_proba(df_vector)[0][1]
                return round(float(prob * 100.0), 2)
            except Exception as e:
                logging.error(f"Error al ejecutar predicción de riesgo con el modelo: {e}")
                
        # Fallback analítico si no hay modelo entrenado
        logging.warning("Usando simulador de riesgo analítico (fallback).")
        similitud = df_vector["porcentaje_similitud"].values[0]
        cambios_ip = df_vector["cambios_ip_examen"].values[0]
        variacion_nota = df_vector["variacion_nota"].values[0]
        accesos = df_vector["accesos_lms_semana"].values[0]
        
        # Regla empírica aproximada
        score = similitud * 0.4 + (cambios_ip * 15.0) + (variacion_nota * 3.0) + (max(0.0, 30.0 - accesos) * 0.5)
        score = min(100.0, max(0.0, score))
        return round(score, 2)

    def detectar_plagio(self, texto: str) -> float:
        """
        Retorna el porcentaje de similitud del texto ingresado contra el corpus de referencia (0 a 100).
        """
        texto_limpio = self.preprocesador.limpiar_texto_plagio(texto)
        if not texto_limpio or len(texto_limpio) < 5:
            return 0.0
            
        if self.modelo_plagio:
            try:
                vectorizer = self.modelo_plagio["vectorizer"]
                ref_matrix = self.modelo_plagio["tfidf_matrix"]
                
                # Transformar entrada
                nuevo_tfidf = vectorizer.transform([texto_limpio])
                
                # Calcular coseno de similitud
                sim_scores = cosine_similarity(nuevo_tfidf, ref_matrix)[0]
                max_sim = np.max(sim_scores)
                return round(float(max_sim * 100.0), 2)
            except Exception as e:
                logging.error(f"Error al ejecutar detección de plagio: {e}")

        # Fallback si no hay modelo cargado
        logging.warning("Usando simulador de plagio (fallback).")
        # Simulación simple basada en palabras clave
        palabras_sospechosas = ["constitución", "cinco fuerzas de porter", "cuatro cavidades", "absorción", "delito"]
        coincidencias = sum(1 for p in palabras_sospechosas if p in texto_limpio)
        sim = (coincidencias / len(palabras_sospechosas)) * 85.0
        return round(sim, 2)

    def detectar_anomalia(self, historial_notas: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Determina si el historial de notas presenta un comportamiento anómalo.
        Retorna (es_anomalia, score_anomalia).
        """
        df_vector = self.preprocesador.preparar_vector_anomalia(historial_notas)
        
        if self.modelo_anomalia:
            try:
                pred = self.modelo_anomalia.predict(df_vector)[0]
                # Isolation forest score (a menor score, más anómalo)
                decision_score = self.modelo_anomalia.decision_function(df_vector)[0]
                es_anomalia = (pred == -1)
                
                # Convertir decision_score a un indicador 0-100 para visibilidad
                # Score de decision suele ir de -0.5 a 0.5. Mapeamos a 0-100 (100 = extremadamente anómalo)
                score_anomalia = round(float((0.5 - decision_score) * 100.0), 2)
                score_anomalia = min(100.0, max(0.0, score_anomalia))
                
                return es_anomalia, score_anomalia
            except Exception as e:
                logging.error(f"Error al predecir anomalías: {e}")

        # Fallback si no hay modelo
        logging.warning("Usando simulador de anomalías (fallback).")
        nota_act = df_vector["nota_actual"].values[0]
        nota_ant = df_vector["nota_anterior"].values[0]
        accesos = df_vector["accesos_lms_semana"].values[0]
        
        # Si sube más de 8 puntos y tiene menos de 3 accesos, se marca como anomalía
        es_anomalia = (nota_act - nota_ant >= 8.0) and (accesos <= 3.0)
        score_anomalia = 85.0 if es_anomalia else 15.0
        return es_anomalia, score_anomalia
