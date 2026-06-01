# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase CRUD Estudiante (DimEstudiante)
Autor: Grupo 4 - Universidad Peruana
"""

import logging
from typing import List, Dict, Any, Optional
from ClaseBD.conexion import ConexionBD

class CRUDEstudiante:
    """Clase para manejar las operaciones CRUD sobre la dimensión DimEstudiante."""
    
    def __init__(self, conexion: ConexionBD) -> None:
        self.db = conexion
        
        # Datos mock en caso de estar en Mock Mode
        self._mock_estudiantes = [
            {"id_estudiante": 1, "codigo": "20220001", "nombre": "JUAN QUISPE VILLANUEVA", "ciclo": 6, "carrera": "Ingeniería de Sistemas", "fecha_ingreso": "2022-03-15"},
            {"id_estudiante": 2, "codigo": "20220002", "nombre": "MARIA FLORES ARIAS", "ciclo": 8, "carrera": "Derecho", "fecha_ingreso": "2022-03-15"},
            {"id_estudiante": 3, "codigo": "20220003", "nombre": "JOSE SANCHEZ ORTIZ", "ciclo": 4, "carrera": "Medicina Humana", "fecha_ingreso": "2023-08-15"},
            {"id_estudiante": 4, "codigo": "20220004", "nombre": "ANA RODRIGUEZ SILVA", "ciclo": 5, "carrera": "Administración de Empresas", "fecha_ingreso": "2023-03-15"},
            {"id_estudiante": 5, "codigo": "20220005", "nombre": "LUIS GOMEZ BENITEZ", "ciclo": 7, "carrera": "Ingeniería de Sistemas", "fecha_ingreso": "2022-08-15"},
            {"id_estudiante": 6, "codigo": "20220006", "nombre": "CARLOS MENDOZA REYES", "ciclo": 9, "carrera": "Derecho", "fecha_ingreso": "2021-08-15"},
            {"id_estudiante": 7, "codigo": "20220007", "nombre": "JORGE HUAMAN MORALES", "ciclo": 3, "carrera": "Medicina Humana", "fecha_ingreso": "2024-03-15"},
            {"id_estudiante": 8, "codigo": "20220008", "nombre": "ROSA MAMANI ROJAS", "ciclo": 2, "carrera": "Administración de Empresas", "fecha_ingreso": "2024-08-15"},
            {"id_estudiante": 9, "codigo": "20220009", "nombre": "PEDRO RAMOS GUTIERREZ", "ciclo": 10, "carrera": "Ingeniería de Sistemas", "fecha_ingreso": "2021-03-15"},
            {"id_estudiante": 10, "codigo": "20220010", "nombre": "GABRIELA VARGAS MEDINA", "ciclo": 1, "carrera": "Derecho", "fecha_ingreso": "2025-03-15"}
        ]

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de todos los estudiantes."""
        query = "SELECT id_estudiante, codigo, nombre, ciclo, carrera, CONVERT(VARCHAR, fecha_ingreso, 23) AS fecha_ingreso FROM dbo.DimEstudiante ORDER BY nombre"
        resultados = self.db.ejecutar_consulta(query)
        
        if self.db.mock_mode or not resultados:
            return self._mock_estudiantes
        return resultados

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca un estudiante por su código único."""
        query = "SELECT id_estudiante, codigo, nombre, ciclo, carrera, CONVERT(VARCHAR, fecha_ingreso, 23) AS fecha_ingreso FROM dbo.DimEstudiante WHERE codigo = ?"
        resultados = self.db.ejecutar_consulta(query, (codigo,))
        
        if self.db.mock_mode or not resultados:
            for est in self._mock_estudiantes:
                if est["codigo"] == codigo:
                    return est
            return None
        return resultados[0]

    def crear_estudiante(self, codigo: str, nombre: str, ciclo: int, carrera: str, fecha_ingreso: str) -> bool:
        """Crea un nuevo registro de estudiante en la base de datos."""
        query = "INSERT INTO dbo.DimEstudiante (codigo, nombre, ciclo, carrera, fecha_ingreso) VALUES (?, ?, ?, ?, ?)"
        exito = self.db.ejecutar_comando(query, (codigo, nombre, ciclo, carrera, fecha_ingreso))
        
        if self.db.mock_mode:
            # Simular en memoria
            nuevo = {
                "id_estudiante": len(self._mock_estudiantes) + 1,
                "codigo": codigo,
                "nombre": nombre.upper(),
                "ciclo": ciclo,
                "carrera": carrera,
                "fecha_ingreso": fecha_ingreso
            }
            self._mock_estudiantes.append(nuevo)
            return True
        return exito

    def actualizar_estudiante(self, codigo: str, ciclo: int, carrera: str) -> bool:
        """Actualiza el ciclo y carrera de un estudiante."""
        query = "UPDATE dbo.DimEstudiante SET ciclo = ?, carrera = ? WHERE codigo = ?"
        exito = self.db.ejecutar_comando(query, (ciclo, carrera, codigo))
        
        if self.db.mock_mode:
            for est in self._mock_estudiantes:
                if est["codigo"] == codigo:
                    est["ciclo"] = ciclo
                    est["carrera"] = carrera
                    return True
            return False
        return exito

    def eliminar_estudiante(self, codigo: str) -> bool:
        """Elimina un estudiante de la base de datos."""
        query = "DELETE FROM dbo.DimEstudiante WHERE codigo = ?"
        exito = self.db.ejecutar_comando(query, (codigo,))
        
        if self.db.mock_mode:
            for est in self._mock_estudiantes:
                if est["codigo"] == codigo:
                    self._mock_estudiantes.remove(est)
                    return True
            return False
        return exito
