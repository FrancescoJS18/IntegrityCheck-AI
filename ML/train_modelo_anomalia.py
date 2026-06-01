# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Entrenamiento del Modelo 3: Detección de Anomalías en Notas (Isolation Forest)
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from config_ml import RUTA_MODELO_ANOMALIA, ANOMALY_CONTAMINATION, FEATURES_ANOMALIA

def generar_datos_historicos_notas(n_samples: int = 800) -> pd.DataFrame:
    """
    Genera un conjunto de datos histórico de notas y accesos.
    Incluye anomalías inducidas (notas infladas con bajos accesos).
    """
    np.random.seed(24)
    
    # 1. Comportamiento Normal (95%)
    n_normal = int(n_samples * (1.0 - ANOMALY_CONTAMINATION))
    
    nota_anterior_n = np.random.uniform(8.0, 18.0, n_normal)
    # Variación lógica acorde al esfuerzo
    variacion_n = np.random.normal(0.0, 1.5, n_normal)
    nota_actual_n = np.clip(nota_anterior_n + variacion_n, 0.0, 20.0)
    # A mayor nota anterior/actual, más accesos LMS por lo general
    accesos_n = np.clip(nota_actual_n * 2.5 + np.random.normal(5, 4, n_normal), 2.0, 60.0)
    
    # 2. Comportamiento Anómalo (5%) - Notas elevadas con CERO esfuerzo/accesos
    n_anomalo = n_samples - n_normal
    nota_anterior_a = np.random.uniform(4.0, 8.0, n_anomalo)
    # Variación de nota abrupta hacia arriba (ej. de 05 a 20)
    variacion_a = np.random.uniform(7.0, 14.0, n_anomalo)
    nota_actual_a = np.clip(nota_anterior_a + variacion_a, 17.0, 20.0)
    # Bajos accesos LMS en comparación con su nota
    accesos_a = np.random.uniform(0.0, 3.0, n_anomalo)
    
    # Unir datos
    df_normal = pd.DataFrame({
        "nota_anterior": nota_anterior_n,
        "variacion_nota": nota_actual_n - nota_anterior_n,
        "nota_actual": nota_actual_n,
        "accesos_lms_semana": accesos_n
    })
    
    df_anomalo = pd.DataFrame({
        "nota_anterior": nota_anterior_a,
        "variacion_nota": nota_actual_a - nota_anterior_a,
        "nota_actual": nota_actual_a,
        "accesos_lms_semana": accesos_a
    })
    
    df = pd.concat([df_normal, df_anomalo], ignore_index=True)
    return df

def entrenar() -> None:
    print("=== Entrenando Modelo de Anomalías en Notas (Isolation Forest) ===")
    
    df = generar_datos_historicos_notas(1000)
    X = df[FEATURES_ANOMALIA]
    
    # Inicializar Isolation Forest según parámetros configurados
    clf = IsolationForest(
        contamination=ANOMALY_CONTAMINATION,
        random_state=42,
        n_estimators=100
    )
    
    # Ajustar modelo
    clf.fit(X)
    
    # Evaluar sobre el mismo set para control de anomalías
    preds = clf.predict(X) # 1 = normal, -1 = anomalía
    n_anomalias = (preds == -1).sum()
    
    print(f"\nEntrenamiento completo.")
    print(f"Total registros analizados: {len(X)}")
    print(f"Anomalías detectadas en set de entrenamiento: {n_anomalias} ({n_anomalias/len(X)*100:.1f}%)")
    
    # Guardar en archivo pickle
    joblib.dump(clf, RUTA_MODELO_ANOMALIA)
    print(f"Modelo Isolation Forest guardado exitosamente en: {RUTA_MODELO_ANOMALIA}")

if __name__ == "__main__":
    entrenar()
