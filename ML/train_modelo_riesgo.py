# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Entrenamiento del Modelo 1: Riesgo de Fraude (Random Forest Classifier)
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from config_ml import RUTA_MODELO_RIESGO, FEATURES_RIESGO

def generar_datos_sinteticos(n_samples: int = 1000) -> pd.DataFrame:
    """
    Genera un conjunto de datos sintético realista para entrenamiento.
    """
    np.random.seed(42)
    
    # Features
    promedio_notas = np.random.uniform(5.0, 20.0, n_samples)
    variacion_nota = np.random.uniform(-5.0, 5.0, n_samples)
    porcentaje_similitud = np.random.uniform(0.0, 100.0, n_samples)
    tiempo_respuesta = np.random.uniform(10.0, 120.0, n_samples) # minutos
    accesos_lms = np.random.uniform(2.0, 50.0, n_samples)
    cambios_ip = np.random.randint(0, 5, n_samples)
    
    df = pd.DataFrame({
        "promedio_notas_ciclo": promedio_notas,
        "variacion_nota": variacion_nota,
        "porcentaje_similitud": porcentaje_similitud,
        "tiempo_respuesta_examen": tiempo_respuesta,
        "accesos_lms_semana": accesos_lms,
        "cambios_ip_examen": cambios_ip
    })
    
    # Lógica simplificada para etiquetar fraude
    # Se sospecha fraude si la similitud es alta, hay variaciones de nota bruscas con pocos accesos o cambios de IP altos.
    scoring = (
        (df["porcentaje_similitud"] > 70) * 2.5 +
        (df["cambios_ip_examen"] >= 3) * 2.0 +
        (df["variacion_nota"] > 3.5) * 1.5 +
        (df["accesos_lms_semana"] < 5) * 1.5 +
        (df["tiempo_respuesta_examen"] < 20) * 1.5
    )
    
    # Target (1 = Fraude Confirmado, 0 = Normal)
    # Si el score acumulado es alto, aumentamos la probabilidad de fraude
    prob = 1 / (1 + np.exp(-(scoring - 4.5)))
    df["fraude_confirmado"] = (np.random.rand(n_samples) < prob).astype(int)
    
    return df

def entrenar() -> None:
    print("=== Entrenando Modelo de Riesgo de Fraude (Random Forest) ===")
    
    # 1. Generar datos
    df = generar_datos_sinteticos(1200)
    
    X = df[FEATURES_RIESGO]
    y = df["fraude_confirmado"]
    
    # 2. Dividir entrenamiento/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    # 3. Modelar
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)
    
    # 4. Predecir
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    
    # 5. Métricas
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    print("\nMétricas de Evaluación:")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"AUC-ROC  : {auc:.4f}")
    
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, y_pred))
    
    # 6. Guardar modelo serializado
    joblib.dump(clf, RUTA_MODELO_RIESGO)
    print(f"\nModelo guardado exitosamente en: {RUTA_MODELO_RIESGO}")

if __name__ == "__main__":
    entrenar()
