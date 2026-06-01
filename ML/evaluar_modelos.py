# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Script de Evaluación Colectiva de Modelos
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from config_ml import RUTA_MODELO_RIESGO, RUTA_MODELO_PLAGIO, RUTA_MODELO_ANOMALIA, FEATURES_RIESGO, FEATURES_ANOMALIA

def evaluar():
    print("==========================================================")
    print("   IntegrityCheck AI - REPORTE DE EVALUACIÓN DE MODELOS   ")
    print("==========================================================\n")
    
    # 1. Cargar modelos
    if not os.path.exists(RUTA_MODELO_RIESGO) or not os.path.exists(RUTA_MODELO_ANOMALIA):
        print("Falta entrenar alguno de los modelos. Corre 'train_*.py' primero.")
        return
        
    clf_riesgo = joblib.load(RUTA_MODELO_RIESGO)
    clf_anomalia = joblib.load(RUTA_MODELO_ANOMALIA)
    
    # 2. Evaluación de Riesgo de Fraude (Random Forest)
    print("--- 1. EVALUACIÓN DE MODELO DE RIESGO (Random Forest) ---")
    # Generar un set de validación
    np.random.seed(99)
    n_val = 200
    
    promedio_notas = np.random.uniform(5.0, 20.0, n_val)
    variacion_nota = np.random.uniform(-5.0, 5.0, n_val)
    porcentaje_similitud = np.random.uniform(0.0, 100.0, n_val)
    tiempo_respuesta = np.random.uniform(10.0, 120.0, n_val)
    accesos_lms = np.random.uniform(2.0, 50.0, n_val)
    cambios_ip = np.random.randint(0, 5, n_val)
    
    df_val = pd.DataFrame({
        "promedio_notas_ciclo": promedio_notas,
        "variacion_nota": variacion_nota,
        "porcentaje_similitud": porcentaje_similitud,
        "tiempo_respuesta_examen": tiempo_respuesta,
        "accesos_lms_semana": accesos_lms,
        "cambios_ip_examen": cambios_ip
    })
    
    scoring = (
        (df_val["porcentaje_similitud"] > 70) * 2.5 +
        (df_val["cambios_ip_examen"] >= 3) * 2.0 +
        (df_val["variacion_nota"] > 3.5) * 1.5 +
        (df_val["accesos_lms_semana"] < 5) * 1.5 +
        (df_val["tiempo_respuesta_examen"] < 20) * 1.5
    )
    prob = 1 / (1 + np.exp(-(scoring - 4.5)))
    y_true = (np.random.rand(n_val) < prob).astype(int)
    
    X_val = df_val[FEATURES_RIESGO]
    y_pred = clf_riesgo.predict(X_val)
    y_proba = clf_riesgo.predict_proba(X_val)[:, 1]
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)
    
    print(f"Accuracy  : {acc * 100:.2f}%")
    print(f"Precision : {prec * 100:.2f}%")
    print(f"Recall    : {rec * 100:.2f}%")
    print(f"F1-Score  : {f1 * 100:.2f}%")
    print(f"AUC-ROC   : {auc:.4f}")
    print(f"Matriz de Confusión:\n{cm}\n")
    
    # 3. Evaluación de Anomalías en Notas (Isolation Forest)
    print("--- 2. EVALUACIÓN DE MODELO DE ANOMALÍAS (Isolation Forest) ---")
    # Generar muestras normales y anómalas conocidas para validación
    n_normal_val = 150
    n_anom_val = 15
    
    # Normales
    not_ant_n = np.random.uniform(10.0, 16.0, n_normal_val)
    var_n = np.random.normal(0.0, 1.0, n_normal_val)
    not_act_n = np.clip(not_ant_n + var_n, 0.0, 20.0)
    acc_n = np.clip(not_act_n * 2.5 + np.random.normal(5, 2, n_normal_val), 2.0, 50.0)
    
    # Anómalos (salto de nota de 05 a 20 con 0 accesos)
    not_ant_a = np.random.uniform(4.0, 7.0, n_anom_val)
    var_a = np.random.uniform(12.0, 15.0, n_anom_val)
    not_act_a = np.clip(not_ant_a + var_a, 18.0, 20.0)
    acc_a = np.random.uniform(0.0, 1.5, n_anom_val)
    
    df_val_anom = pd.concat([
        pd.DataFrame({"nota_anterior": not_ant_n, "variacion_nota": var_n, "nota_actual": not_act_n, "accesos_lms_semana": acc_n, "target": 1}), # 1 = normal
        pd.DataFrame({"nota_anterior": not_ant_a, "variacion_nota": var_a, "nota_actual": not_act_a, "accesos_lms_semana": acc_a, "target": -1}) # -1 = anomalo
    ], ignore_index=True)
    
    X_val_anom = df_val_anom[FEATURES_ANOMALIA]
    y_true_anom = df_val_anom["target"]
    
    y_pred_anom = clf_anomalia.predict(X_val_anom)
    
    acc_anom = accuracy_score(y_true_anom, y_pred_anom)
    # Contar cuántas anomalías reales fueron detectadas (True Positives en contexto de anomalías)
    anomalias_reales = df_val_anom["target"] == -1
    anomalias_predichas = y_pred_anom == -1
    detecciones = np.logical_and(anomalias_reales, anomalias_predichas).sum()
    
    print(f"Accuracy de Clasificación de Estructura : {acc_anom * 100:.2f}%")
    print(f"Anomalías reales evaluadas              : {n_anom_val}")
    print(f"Anomalías capturadas por el modelo      : {detecciones} ({detecciones/n_anom_val*100:.1f}% de recall de anomalías)")
    print("==========================================================\n")

if __name__ == "__main__":
    evaluar()
