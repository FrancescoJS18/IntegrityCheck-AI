# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase CRUD Incidente (FactIncidenteFraude) y Control ETL
Autor: Grupo 4 - Universidad Peruana
"""

import logging
import datetime
from typing import List, Dict, Any, Optional
from ClaseBD.conexion import ConexionBD

class CRUDIncidente:
    """Clase para manejar las operaciones CRUD sobre la tabla FactIncidenteFraude y orquestar el ETL."""
    
    def __init__(self, conexion: ConexionBD) -> None:
        self.db = conexion
        self._mock_incidentes = []
        self._generar_mock_incidentes()

    def _generar_mock_incidentes(self) -> None:
        """Genera dinámicamente más de 50 incidentes realistas para simulación offline."""
        nombres_estudiantes = [
            "JUAN QUISPE VILLANUEVA", "MARIA FLORES ARIAS", "JOSE SANCHEZ ORTIZ", "ANA RODRIGUEZ SILVA",
            "LUIS GOMEZ BENITEZ", "CARLOS MENDOZA REYES", "JORGE HUAMAN MORALES", "ROSA MAMANI ROJAS",
            "PEDRO RAMOS GUTIERREZ", "GABRIELA VARGAS MEDINA", "DIEGO CASTRO ARIAS", "SOFIA RUIZ ORTIZ",
            "CAMILA CHAVEZ SILVA", "ALEJANDRO ALVAREZ BENITEZ", "LUZ TORRES REYES", "MANUEL QUISPE MORALES",
            "CARMEN FLORES ROJAS", "MIGUEL SANCHEZ GUTIERREZ", "LUCIA RODRIGUEZ MEDINA", "VICTOR GOMEZ TORRES"
        ]
        carreras = ["Ingeniería de Sistemas", "Derecho", "Medicina Humana", "Administración de Empresas"]
        facultades = ["Facultad de Ingeniería", "Facultad de Derecho", "Facultad de Medicina", "Facultad de Administración"]
        cursos = ["Introducción a la Algoritmia", "Derecho Penal General", "Anatomía Humana I", "Finanzas Corporativas"]
        docentes = ["Dr. Javier Huaman Sanchez", "Dra. Patricia Ramos Castro", "Dr. Guillermo Quispe Flores", "MSc. Fernando Sanchez Ramos"]
        tipos_fraude = [
            ("FR-01", "Plagio de Trabajo Académico", "Similitud elevada en Turnitin", "MODERADO"),
            ("FR-02", "Plagio de Tesis/Proyecto", "Copia sustancial de investigación de grado", "GRAVE"),
            ("FR-03", "Copia en Examen Virtual", "Uso de material no autorizado", "MODERADO"),
            ("FR-04", "Suplantación de Identidad", "Rendir examen en lugar de otro alumno", "GRAVE"),
            ("FR-05", "Uso de IA Generativa", "Redacción íntegra por bots en entregables", "LEVE"),
            ("FR-06", "Colusión en Exámenes", "Intercambio de IPs detectadas", "MODERADO")
        ]
        sedes = ["Sede Central - Lima", "Sede Arequipa", "Sede Trujillo", "Sede Cusco"]
        tipos_prueba = ["EXAMEN_PARCIAL", "EXAMEN_FINAL", "PRACTICA", "TRABAJO", "TESIS", "PROYECTO"]

        # Generar 65 incidentes variados
        for i in range(1, 66):
            est_idx = i % len(nombres_estudiantes)
            fac_idx = i % len(facultades)
            tf_idx = i % len(tipos_fraude)
            sede_idx = i % len(sedes)
            tp_idx = i % len(tipos_prueba)
            
            codigo_estudiante = f"2022{1000 + i}"
            estudiante_nombre = nombres_estudiantes[est_idx]
            carrera = carreras[fac_idx]
            facultad = facultades[fac_idx]
            curso = cursos[fac_idx]
            docente = docentes[fac_idx]
            tf_cod, tf_nom, tf_desc, tf_grav = tipos_fraude[tf_idx]
            sede = sedes[sede_idx]
            tipo_prueba = tipos_prueba[tp_idx]
            
            # Calcular riesgos realistas
            riesgo = float((i * 13) % 55 + 40) # 40 a 95
            similitud = float((i * 19) % 65 + 30) if tf_cod in ["FR-01", "FR-02"] else 0.0
            
            estado = "PENDIENTE"
            if i % 3 == 1:
                estado = "EN_REVISION"
            elif i % 3 == 2:
                estado = "CERRADO"
                
            fecha_det = (datetime.datetime.now() - datetime.timedelta(days=(i % 30) + 1, hours=i % 12)).strftime("%Y-%m-%d %H:%M:%S")
            fecha_res = (datetime.datetime.now() - datetime.timedelta(days=i % 10)).strftime("%Y-%m-%d %H:%M:%S") if estado == "CERRADO" else None

            self._mock_incidentes.append({
                "id_incidente": i,
                "estudiante_codigo": codigo_estudiante,
                "estudiante_nombre": estudiante_nombre,
                "estudiante_carrera": carrera,
                "docente_codigo": f"DOC-{200+i}",
                "docente_nombre": docente,
                "curso_codigo": f"CUR-{300+i}",
                "curso_nombre": curso,
                "facultad_nombre": facultad,
                "tipo_fraude_codigo": tf_cod,
                "tipo_fraude_nombre": tf_nom,
                "nivel_gravedad": tf_grav,
                "sede_nombre": sede,
                "tipo_prueba": tipo_prueba,
                "puntaje_riesgo": riesgo,
                "porcentaje_similitud": similitud,
                "estado_caso": estado,
                "fecha_deteccion": fecha_det,
                "fecha_resolucion": fecha_res
            })

    def obtener_todos(self, facultad_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los incidentes del Data Warehouse.
        Si se pasa facultad_filter (por ejemplo, para el rol DECANO),
        aplica Row Level Security filtrando por facultad.
        """
        query = """
            SELECT 
                f.id_incidente,
                e.codigo AS estudiante_codigo,
                e.nombre AS estudiante_nombre,
                e.carrera AS estudiante_carrera,
                d.nombre AS docente_nombre,
                c.codigo AS curso_codigo,
                c.nombre AS curso_nombre,
                fac.nombre AS facultad_nombre,
                tf.codigo AS tipo_fraude_codigo,
                tf.nombre AS tipo_fraude_nombre,
                tf.nivel_gravedad,
                s.nombre AS sede_nombre,
                tp.nombre AS tipo_prueba,
                f.puntaje_riesgo,
                f.porcentaje_similitud,
                f.estado_caso,
                CONVERT(VARCHAR, f.fecha_deteccion, 120) AS fecha_deteccion,
                CONVERT(VARCHAR, f.fecha_resolucion, 120) AS fecha_resolucion
            FROM dbo.FactIncidenteFraude f
            INNER JOIN dbo.DimEstudiante e ON f.id_estudiante = e.id_estudiante
            INNER JOIN dbo.DimDocente d ON f.id_docente = d.id_docente
            INNER JOIN dbo.DimCurso c ON f.id_curso = c.id_curso
            INNER JOIN dbo.DimFacultad fac ON f.id_facultad = fac.id_facultad
            INNER JOIN dbo.DimTipoFraude tf ON f.id_tipo_fraude = tf.id_tipo_fraude
            INNER JOIN dbo.DimSede s ON f.id_sede = s.id_sede
            INNER JOIN dbo.DimTipoPrueba tp ON f.id_tipo_prueba = tp.id_tipo_prueba
        """
        
        params = []
        if facultad_filter:
            query += " WHERE fac.nombre = ?"
            params.append(facultad_filter)
            
        query += " ORDER BY f.fecha_deteccion DESC"
        
        resultados = self.db.ejecutar_consulta(query, tuple(params))
        
        if self.db.mock_mode or not resultados:
            if facultad_filter:
                return [inc for inc in self._mock_incidentes if inc["facultad_nombre"].lower() == facultad_filter.lower()]
            return self._mock_incidentes
            
        return resultados

    def obtener_por_id(self, id_incidente: int) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de un incidente de fraude."""
        query = """
            SELECT 
                f.id_incidente,
                e.codigo AS estudiante_codigo,
                e.nombre AS estudiante_nombre,
                e.carrera AS estudiante_carrera,
                d.codigo AS docente_codigo,
                d.nombre AS docente_nombre,
                c.codigo AS curso_codigo,
                c.nombre AS curso_nombre,
                fac.nombre AS facultad_nombre,
                tf.codigo AS tipo_fraude_codigo,
                tf.nombre AS tipo_fraude_nombre,
                tf.descripcion AS tipo_fraude_descripcion,
                tf.nivel_gravedad,
                s.nombre AS sede_nombre,
                tp.nombre AS tipo_prueba,
                f.puntaje_riesgo,
                f.porcentaje_similitud,
                f.estado_caso,
                CONVERT(VARCHAR, f.fecha_deteccion, 120) AS fecha_deteccion,
                CONVERT(VARCHAR, f.fecha_resolucion, 120) AS fecha_resolucion
            FROM dbo.FactIncidenteFraude f
            INNER JOIN dbo.DimEstudiante e ON f.id_estudiante = e.id_estudiante
            INNER JOIN dbo.DimDocente d ON f.id_docente = d.id_docente
            INNER JOIN dbo.DimCurso c ON f.id_curso = c.id_curso
            INNER JOIN dbo.DimFacultad fac ON f.id_facultad = fac.id_facultad
            INNER JOIN dbo.DimTipoFraude tf ON f.id_tipo_fraude = tf.id_tipo_fraude
            INNER JOIN dbo.DimSede s ON f.id_sede = s.id_sede
            INNER JOIN dbo.DimTipoPrueba tp ON f.id_tipo_prueba = tp.id_tipo_prueba
            WHERE f.id_incidente = ?
        """
        resultados = self.db.ejecutar_consulta(query, (id_incidente,))
        
        if self.db.mock_mode or not resultados:
            for inc in self._mock_incidentes:
                if inc["id_incidente"] == id_incidente:
                    return inc
            return None
            
        return resultados[0]

    def actualizar_estado(self, id_incidente: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de un caso en la base de datos."""
        fecha_resolucion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if nuevo_estado == "CERRADO" else None
        
        query = "UPDATE dbo.FactIncidenteFraude SET estado_caso = ?, fecha_resolucion = ? WHERE id_incidente = ?"
        exito = self.db.ejecutar_comando(query, (nuevo_estado, fecha_resolucion, id_incidente))
        
        if self.db.mock_mode:
            for inc in self._mock_incidentes:
                if inc["id_incidente"] == id_incidente:
                    inc["estado_caso"] = nuevo_estado
                    inc["fecha_resolucion"] = fecha_resolucion
                    return True
            return False
            
        return exito

    def ejecutar_etl(self, id_carga: str) -> bool:
        """
        Ejecuta secuencialmente los tres stored procedures del proceso ETL:
        1. Extract (validaciones)
        2. Transform (limpieza)
        3. Load (fusión a DW y hechos)
        """
        logging.info(f"Triggering ETL for Load ID: {id_carga}")
        
        if self.db.mock_mode:
            logging.info("[MOCK] Simulando ejecución de Stored Procedures de ETL...")
            logging.info("[MOCK] sp_etl_extract ejecutado con éxito.")
            logging.info("[MOCK] sp_etl_transform ejecutado con éxito.")
            logging.info("[MOCK] sp_etl_load ejecutado con éxito.")
            return True
            
        try:
            # Ejecutar Extract
            logging.info("Ejecutando sp_etl_extract...")
            exito_extract = self.db.ejecutar_comando("EXEC dbo.sp_etl_extract ?", (id_carga,))
            if not exito_extract:
                raise Exception("Falla en sp_etl_extract")
                
            # Ejecutar Transform
            logging.info("Ejecutando sp_etl_transform...")
            exito_transform = self.db.ejecutar_comando("EXEC dbo.sp_etl_transform ?", (id_carga,))
            if not exito_transform:
                raise Exception("Falla en sp_etl_transform")
                
            # Ejecutar Load
            logging.info("Ejecutando sp_etl_load...")
            exito_load = self.db.ejecutar_comando("EXEC dbo.sp_etl_load ?", (id_carga,))
            if not exito_load:
                raise Exception("Falla en sp_etl_load")
                
            logging.info(f"ETL finalizado correctamente para Carga: {id_carga}")
            return True
        except Exception as e:
            logging.error(f"Error durante la ejecución del proceso ETL: {e}")
            return False
