# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase de Preprocesamiento de Datos para Modelos ML
Autor: Grupo 4 - Universidad Peruana
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

class PreprocesadorDatos:
    """Clase responsable de la limpieza y formateo de datos para su paso por el motor ML."""
    
    def __init__(self, features_riesgo: List[str] = None, features_anomalia: List[str] = None) -> None:
        self.features_riesgo = features_riesgo or [
            "promedio_notas_ciclo", "variacion_nota", "porcentaje_similitud",
            "tiempo_respuesta_examen", "accesos_lms_semana", "cambios_ip_examen"
        ]
        self.features_anomalia = features_anomalia or [
            "nota_actual", "nota_anterior", "variacion_nota", "accesos_lms_semana"
        ]

    def preparar_vector_riesgo(self, datos_estudiante: Dict[str, Any]) -> pd.DataFrame:
        """
        Limpia e imputa valores por defecto para predecir el riesgo de un estudiante.
        Retorna un DataFrame de una fila listo para el clasificador.
        """
        # Valores por defecto para prevenir errores
        vector = {
            "promedio_notas_ciclo": float(datos_estudiante.get("promedio_notas_ciclo", 12.0)),
            "variacion_nota": float(datos_estudiante.get("variacion_nota", 0.0)),
            "porcentaje_similitud": float(datos_estudiante.get("porcentaje_similitud", 0.0)),
            "tiempo_respuesta_examen": float(datos_estudiante.get("tiempo_respuesta_examen", 60.0)),
            "accesos_lms_semana": float(datos_estudiante.get("accesos_lms_semana", 10.0)),
            "cambios_ip_examen": int(datos_estudiante.get("cambios_ip_examen", 0))
        }
        
        # Generar DataFrame con las columnas ordenadas
        df = pd.DataFrame([vector])
        return df[self.features_riesgo]

    def preparar_vector_anomalia(self, historial_notas: Dict[str, Any]) -> pd.DataFrame:
        """
        Limpia los datos históricos de un alumno para evaluar si existe anomalía en su nota.
        """
        nota_act = float(historial_notas.get("nota_actual", 11.0))
        nota_ant = float(historial_notas.get("nota_anterior", 11.0))
        
        vector = {
            "nota_actual": nota_act,
            "nota_anterior": nota_ant,
            "variacion_nota": float(historial_notas.get("variacion_nota", nota_act - nota_ant)),
            "accesos_lms_semana": float(historial_notas.get("accesos_lms_semana", 15.0))
        }
        
        df = pd.DataFrame([vector])
        return df[self.features_anomalia]

    def limpiar_texto_plagio(self, texto: str) -> str:
        """
        Remueve caracteres extraños, espacios adicionales y normaliza el texto.
        """
        if not texto:
            return ""
            
        # Normalizar a minúsculas y quitar espacios extra
        texto_limpio = texto.lower().strip()
        # Reemplazar múltiples espacios por uno
        texto_limpio = " ".join(texto_limpio.split())
        return texto_limpio
