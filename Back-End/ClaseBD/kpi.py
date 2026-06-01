# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase de Consultas KPI (Capa Semántica)
Autor: Grupo 4 - Universidad Peruana
"""

import logging
from typing import Dict, List, Any, Optional
from ClaseBD.conexion import ConexionBD
from ClaseBD.incidente import CRUDIncidente

class KPIConsultas:
    """Clase para interactuar con las vistas KPI en SQL Server o simular estadísticas."""
    
    def __init__(self, conexion: ConexionBD, crud_incidente: CRUDIncidente) -> None:
        self.db = conexion
        self.crud_inc = crud_incidente

    def obtener_kpis_dashboard(self, facultad_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna los KPIs principales para el dashboard central.
        Aplica filtro de facultad para RLS si es proporcionado.
        """
        kpis = {}
        
        if self.db.mock_mode:
            # Obtener incidentes simulados
            incidentes = self.crud_inc.obtener_todos(facultad_filter)
            total = len(incidentes)
            pendientes = sum(1 for x in incidentes if x["estado_caso"] == "PENDIENTE")
            revision = sum(1 for x in incidentes if x["estado_caso"] == "EN_REVISION")
            cerrados = sum(1 for x in incidentes if x["estado_caso"] == "CERRADO")
            
            graves = sum(1 for x in incidentes if x["nivel_gravedad"] == "GRAVE")
            promedio_riesgo = sum(x["puntaje_riesgo"] for x in incidentes) / total if total > 0 else 0.0
            
            # Indice integridad: 100 - (graves / total * 100)
            indice_int = 100.0 - ((graves / total * 100.0) if total > 0 else 0.0)
            
            # Promedio de similitud en plagios
            plagios = [x["porcentaje_similitud"] for x in incidentes if x["porcentaje_similitud"] > 0]
            similitud_prom = sum(plagios) / len(plagios) if plagios else 0.0
            
            kpis = {
                "total_casos": total,
                "casos_pendientes": pendientes,
                "casos_revision": revision,
                "casos_cerrados": cerrados,
                "promedio_riesgo": round(promedio_riesgo, 2),
                "indice_integridad": round(indice_int, 2),
                "similitud_promedio": round(similitud_prom, 2)
            }
        else:
            # Consulta real en base de datos utilizando vistas
            # Total de casos y estados
            query_estados = "SELECT estado_caso, COUNT(*) as total FROM dbo.FactIncidenteFraude"
            # Filtro por facultad si se aplica RLS
            if facultad_filter:
                query_estados = """
                    SELECT f.estado_caso, COUNT(*) as total 
                    FROM dbo.FactIncidenteFraude f
                    INNER JOIN dbo.DimFacultad fac ON f.id_facultad = fac.id_facultad
                    WHERE fac.nombre = ?
                    GROUP BY f.estado_caso
                """
                res_estados = self.db.ejecutar_consulta(query_estados, (facultad_filter,))
            else:
                query_estados += " GROUP BY estado_caso"
                res_estados = self.db.ejecutar_consulta(query_estados)
                
            total = 0
            pendientes = 0
            revision = 0
            cerrados = 0
            for r in res_estados:
                tot = r["total"]
                total += tot
                if r["estado_caso"] == "PENDIENTE":
                    pendientes = tot
                elif r["estado_caso"] == "EN_REVISION":
                    revision = tot
                elif r["estado_caso"] == "CERRADO":
                    cerrados = tot

            # Índice de integridad de la vista
            query_integridad = "SELECT TOP 1 indice_integridad FROM dbo.vw_kpi_indice_integridad"
            if facultad_filter:
                # Si hay RLS recalculamos en base a los incidentes de la facultad
                query_integridad = """
                    SELECT 100.0 - (CAST(SUM(CASE WHEN tf.nivel_gravedad = 'GRAVE' THEN 1 ELSE 0 END) AS DECIMAL(5,2)) / NULLIF(CAST(COUNT(f.id_incidente) AS DECIMAL(5,2)), 0) * 100.0) AS indice_integridad
                    FROM dbo.FactIncidenteFraude f
                    INNER JOIN dbo.DimTipoFraude tf ON f.id_tipo_fraude = tf.id_tipo_fraude
                    INNER JOIN dbo.DimFacultad fac ON f.id_facultad = fac.id_facultad
                    WHERE fac.nombre = ?
                """
                res_int = self.db.ejecutar_consulta(query_integridad, (facultad_filter,))
            else:
                res_int = self.db.ejecutar_consulta(query_integridad)
                
            indice_int = res_int[0]["indice_integridad"] if res_int and res_int[0]["indice_integridad"] is not None else 100.0
            
            # Promedio de riesgo
            query_riesgo = "SELECT AVG(puntaje_riesgo) as avg_riesgo, AVG(porcentaje_similitud) as avg_sim FROM dbo.FactIncidenteFraude f"
            if facultad_filter:
                query_riesgo += " INNER JOIN dbo.DimFacultad fac ON f.id_facultad = fac.id_facultad WHERE fac.nombre = ?"
                res_riesgo = self.db.ejecutar_consulta(query_riesgo, (facultad_filter,))
            else:
                res_riesgo = self.db.ejecutar_consulta(query_riesgo)
                
            avg_riesgo = res_riesgo[0]["avg_riesgo"] if res_riesgo and res_riesgo[0]["avg_riesgo"] is not None else 0.0
            avg_sim = res_riesgo[0]["avg_sim"] if res_riesgo and res_riesgo[0]["avg_sim"] is not None else 0.0

            kpis = {
                "total_casos": total,
                "casos_pendientes": pendientes,
                "casos_revision": revision,
                "casos_cerrados": cerrados,
                "promedio_riesgo": round(float(avg_riesgo), 2),
                "indice_integridad": round(float(indice_int), 2),
                "similitud_promedio": round(float(avg_sim), 2)
            }
            
        return kpis

    def obtener_ranking_facultades(self) -> List[Dict[str, Any]]:
        """Devuelve el listado de facultades ordenado por su tasa de incidentes."""
        query = "SELECT facultad, total_incidentes, total_estudiantes, tasa_incidentes FROM dbo.vw_kpi_tasa_incidentes_facultad ORDER BY tasa_incidentes DESC"
        resultados = self.db.ejecutar_consulta(query)
        
        if self.db.mock_mode or not resultados:
            # Simular ranking
            return [
                {"facultad": "Facultad de Ingeniería", "total_incidentes": 28, "total_estudiantes": 52, "tasa_incidentes": 53.8},
                {"facultad": "Facultad de Derecho", "total_incidentes": 15, "total_estudiantes": 53, "tasa_incidentes": 28.3},
                {"facultad": "Facultad de Medicina", "total_incidentes": 12, "total_estudiantes": 52, "tasa_incidentes": 23.1},
                {"facultad": "Facultad de Administración", "total_incidentes": 10, "total_estudiantes": 53, "tasa_incidentes": 18.9}
            ]
        return resultados

    def obtener_alertas_activas(self, umbral: float = 70.0, facultad_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna incidentes de fraude activos (riesgo > umbral)."""
        incidentes = self.crud_inc.obtener_todos(facultad_filter)
        alertas = [inc for inc in incidentes if inc["puntaje_riesgo"] >= umbral and inc["estado_caso"] != "CERRADO"]
        # Ordenar por puntaje_riesgo de forma descendente
        alertas.sort(key=lambda x: x["puntaje_riesgo"], reverse=True)
        return alertas
