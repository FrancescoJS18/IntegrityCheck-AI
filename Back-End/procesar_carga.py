# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Procesador de Carga por 7 Capas
Autor: Grupo 4 - Universidad Peruana
Uso: python procesar_carga.py <archivo_excel>
"""

import sys
import os
import json
import time
import pandas as pd
import numpy as np
import joblib
import pyodbc
from datetime import datetime

# ─── CONFIGURACIÓN ───────────────────────────────────────────────
from dotenv import load_dotenv
# Intentar cargar .env del directorio del script o del directorio padre
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_SERVER   = os.getenv("DB_SERVER", "MELIODAS\\INTEGRITY")
DB_DATABASE = os.getenv("DB_DATABASE", "IntegrityCheckAI")
DB_USER     = os.getenv("DB_USERNAME", "sa")
DB_PASS     = os.getenv("DB_PASSWORD", "Admin123!")
MODELOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ML", "modelos"))

def log(capa, msg, ok=True):
    estado = "✅" if ok else "❌"
    print(f"{estado} [CAPA {capa}] {msg}", flush=True)

def conectar_bd():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USER};PWD={DB_PASS};TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

# ─── CAPA 1: FUENTES DE DATOS ─────────────────────────────────────
def capa1_leer_excel(ruta_excel):
    log(1, f"Leyendo fuente de datos: {os.path.basename(ruta_excel)}")
    df = pd.read_excel(ruta_excel)
    log(1, f"{len(df)} registros cargados desde Excel")
    columnas_requeridas = ["codigo_estudiante","nombre_completo","carrera",
                           "facultad","sede","ciclo","promedio_notas",
                           "similitud_turnitin","accesos_lms_semana",
                           "cambios_ip_examen","tiempo_respuesta_examen_min",
                           "variacion_nota","fraude_confirmado"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Columna faltante: {col}")
    log(1, "Estructura del Excel validada correctamente")
    return df

# ─── CAPA 2: STAGING AREA ─────────────────────────────────────────
def capa2_staging(df, conn):
    log(2, "Cargando datos a Staging Area (stg_estudiantes)...")
    cursor = conn.cursor()
    fecha = datetime.now()
    insertados = 0
    invalidos  = 0

    for _, row in df.iterrows():
        # Validación básica
        if pd.isna(row["nombre_completo"]) or pd.isna(row["promedio_notas"]):
            estado = "INVALIDO"
            error  = "Campos obligatorios nulos"
            invalidos += 1
        elif not (0 <= row["promedio_notas"] <= 20):
            estado = "CUARENTENA"
            error  = f"Promedio fuera de rango: {row['promedio_notas']}"
            invalidos += 1
        else:
            estado = "VALIDO"
            error  = None

        try:
            cursor.execute("""
                INSERT INTO dbo.stg_estudiantes
                    (codigo_estudiante, nombre_completo, carrera, facultad, sede,
                     ciclo, promedio_notas, similitud_turnitin, accesos_lms_semana,
                     cambios_ip_examen, tiempo_respuesta_examen_min, variacion_nota,
                     fraude_confirmado, fecha_ingesta, estado_validacion, error_detalle)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                str(row["codigo_estudiante"]), str(row["nombre_completo"]),
                str(row["carrera"]),           str(row["facultad"]),
                str(row["sede"]),              int(row["ciclo"]),
                float(row["promedio_notas"]),  float(row["similitud_turnitin"]),
                int(row["accesos_lms_semana"]),int(row["cambios_ip_examen"]),
                int(row["tiempo_respuesta_examen_min"]), float(row["variacion_nota"]),
                int(row["fraude_confirmado"]), fecha, estado, error
            ))
            insertados += 1
        except Exception as e:
            invalidos += 1

    conn.commit()
    log(2, f"Staging: {insertados} válidos, {invalidos} con problemas")
    return df[df.apply(lambda r: (0 <= r["promedio_notas"] <= 20) and 
                                  pd.notna(r["nombre_completo"]), axis=1)]

# ─── CAPA 3: ETL ──────────────────────────────────────────────────
def capa3_etl(df_valido):
    log(3, "Ejecutando transformaciones ETL...")
    df = df_valido.copy()
    df["promedio_notas"]         = df["promedio_notas"].round(2)
    df["similitud_turnitin"]     = df["similitud_turnitin"].clip(0, 100).round(2)
    df["accesos_lms_semana"]     = df["accesos_lms_semana"].clip(0)
    df["cambios_ip_examen"]      = df["cambios_ip_examen"].clip(0)
    df["variacion_nota"]         = df["variacion_nota"].round(2)
    df["carrera"]   = df["carrera"].str.strip().str.title()
    df["facultad"]  = df["facultad"].str.strip().str.title()
    df["sede"]      = df["sede"].str.strip().str.title()
    log(3, f"ETL completado: {len(df)} registros transformados y normalizados")
    return df

# ─── CAPA 4: DATA WAREHOUSE ───────────────────────────────────────
def capa4_dw(df, conn):
    log(4, "Cargando al Data Warehouse (dimensiones + FactIncidenteFraude)...")
    cursor = conn.cursor()

    def get_or_insert_dim(tabla, campo_codigo, codigo, **campos):
        cursor.execute(f"SELECT id_{tabla.replace('Dim','')} FROM dbo.{tabla} WHERE {campo_codigo}=?", codigo)
        row = cursor.fetchone()
        if row:
            return row[0]
        cols = [campo_codigo] + list(campos.keys())
        vals = [codigo] + list(campos.values())
        placeholders = ",".join(["?"]*len(cols))
        col_str = ",".join(cols)
        cursor.execute(f"INSERT INTO dbo.{tabla} ({col_str}) OUTPUT INSERTED.id_{tabla.replace('Dim','')} VALUES ({placeholders})", vals)
        return cursor.fetchone()[0]

    insertados = 0
    for _, row in df.iterrows():
        try:
            id_est = get_or_insert_dim("DimEstudiante","codigo_estudiante",
                row["codigo_estudiante"],
                nombre=str(row["nombre_completo"]),
                ciclo=int(row["ciclo"]),
                carrera=str(row["carrera"]),
                fecha_ingreso=datetime.now().date())

            id_fac = get_or_insert_dim("DimFacultad","codigo_facultad",
                str(hash(row["facultad"]))[:8],
                nombre=str(row["facultad"]),
                decano="Por asignar",
                sede=str(row["sede"]))

            cursor.execute("""
                INSERT INTO dbo.FactIncidenteFraude
                    (id_estudiante, id_facultad, puntaje_riesgo,
                     porcentaje_similitud, estado_caso, fecha_deteccion)
                VALUES (?,?,?,?,?,?)
            """, (id_est, id_fac,
                  float(row.get("puntaje_riesgo", 0)),
                  float(row["similitud_turnitin"]),
                  "PENDIENTE", datetime.now()))
            insertados += 1
        except Exception:
            pass

    conn.commit()
    log(4, f"Data Warehouse: {insertados} hechos insertados")

# ─── CAPA 5: MOTOR DE IA ──────────────────────────────────────────
def capa5_ia(df):
    log(5, "Ejecutando Motor de IA (Random Forest + Isolation Forest)...")
    
    modelo_riesgo   = joblib.load(os.path.join(MODELOS_DIR, "modelo_riesgo.pkl"))
    modelo_anomalia = joblib.load(os.path.join(MODELOS_DIR, "modelo_anomalia.pkl"))
    
    features_riesgo = ["promedio_notas","variacion_nota","similitud_turnitin",
                       "tiempo_respuesta_examen_min","accesos_lms_semana","cambios_ip_examen"]
    
    X = df[features_riesgo].fillna(0)
    df = df.copy()
    df["puntaje_riesgo"]  = (modelo_riesgo.predict_proba(X)[:,1] * 100).round(2)
    df["es_anomalia"]     = modelo_anomalia.predict(X) == -1
    df["score_anomalia"]  = ((0.5 - modelo_anomalia.decision_function(X)) * 100).clip(0, 100).round(2)
    
    alto_riesgo = (df["puntaje_riesgo"] > 70).sum()
    anomalias   = df["es_anomalia"].sum()
    log(5, f"IA completada: {alto_riesgo} casos alto riesgo, {anomalias} anomalías detectadas")
    return df

# ─── CAPA 6: KPIs ─────────────────────────────────────────────────
def capa6_kpis(df):
    log(6, "Calculando KPIs de la Capa Semántica...")
    kpis = {
        "total_estudiantes":    len(df),
        "tasa_riesgo_alto":     round((df["puntaje_riesgo"] > 70).mean() * 100, 2),
        "similitud_promedio":   round(df["similitud_turnitin"].mean(), 2),
        "indice_integridad":    round(100 - (df["fraude_confirmado"].mean() * 100), 2),
        "anomalias_detectadas": int(df["es_anomalia"].sum()),
        "puntaje_riesgo_prom":  round(df["puntaje_riesgo"].mean(), 2),
    }
    log(6, f"KPIs calculados → Índice Integridad: {kpis['indice_integridad']}% | "
            f"Riesgo Alto: {kpis['tasa_riesgo_alto']}% | "
            f"Similitud prom: {kpis['similitud_promedio']}%")
    return kpis

# ─── CAPA 7: VISUALIZACIÓN ────────────────────────────────────────
def capa7_resultado(kpis, n_total):
    log(7, "Datos listos para visualización en Dashboard y Power BI")
    print("\n" + "="*55)
    print("   📊 RESUMEN FINAL — IntegrityCheck AI")
    print("="*55)
    print(f"  Estudiantes procesados : {n_total}")
    print(f"  Índice de Integridad   : {kpis['indice_integridad']}%")
    print(f"  Casos Alto Riesgo      : {kpis['tasa_riesgo_alto']}%")
    print(f"  Similitud Prom Turnitin: {kpis['similitud_promedio']}%")
    print(f"  Anomalías detectadas   : {kpis['anomalias_detectadas']}")
    print(f"  Puntaje Riesgo Promedio: {kpis['puntaje_riesgo_prom']}")
    print("="*55)
    print("  ✅ Proceso completado. Abra Power BI para ver el")
    print("     dashboard con los datos actualizados.")
    print("="*55)
    return kpis

# ─── MAIN ─────────────────────────────────────────────────────────
def procesar(ruta_excel):
    print(f"\n🚀 IntegrityCheck AI — Procesando {os.path.basename(ruta_excel)}")
    print("="*55)
    inicio = time.time()

    # Capa 1
    df = capa1_leer_excel(ruta_excel)
    n_total = len(df)

    # Conectar BD
    try:
        conn = conectar_bd()
        log("BD", "Conexión a SQL Server exitosa")
        usar_bd = True
    except Exception as e:
        log("BD", f"Modo sin BD: {e}", ok=False)
        usar_bd = False
        conn = None

    # Capas 2-4 (requieren BD)
    if usar_bd:
        df_valido = capa2_staging(df, conn)
        df_valido = capa3_etl(df_valido)
    else:
        log(2, "Staging omitido (sin conexión BD)", ok=False)
        log(3, "ETL ejecutado en memoria (sin BD)", ok=True)
        df_valido = capa3_etl(df)

    # Capas 5-7 (solo Python)
    df_valido = capa5_ia(df_valido)

    if usar_bd:
        capa4_dw(df_valido, conn)
        conn.close()

    kpis = capa6_kpis(df_valido)
    resultado = capa7_resultado(kpis, n_total)

    print(f"\n⏱  Tiempo total: {round(time.time()-inicio, 2)}s")
    return json.dumps(resultado)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python procesar_carga.py <ruta_excel>")
        sys.exit(1)
    procesar(sys.argv[1])