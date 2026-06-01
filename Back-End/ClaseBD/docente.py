# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Clase CRUD Docente (DimDocente)
Autor: Grupo 4 - Universidad Peruana
"""

import logging
from typing import List, Dict, Any, Optional
from ClaseBD.conexion import ConexionBD

class CRUDDocente:
    """Clase para manejar las operaciones CRUD sobre la dimensión DimDocente."""
    
    def __init__(self, conexion: ConexionBD) -> None:
        self.db = conexion
        
        # Datos mock en caso de estar en Mock Mode
        self._mock_docentes = [
            {"id_docente": 1, "codigo": "DOC-101", "nombre": "DR. JAVIER HUAMAN SANCHEZ", "especialidad": "Sistemas e Informática", "facultad": "Facultad de Ingeniería"},
            {"id_docente": 2, "codigo": "DOC-102", "nombre": "MSC. ELENA GOMEZ RUIZ", "especialidad": "Inteligencia Artificial", "facultad": "Facultad de Ingeniería"},
            {"id_docente": 3, "codigo": "DOC-201", "nombre": "DRA. PATRICIA RAMOS CASTRO", "especialidad": "Derecho Penal", "facultad": "Facultad de Derecho"},
            {"id_docente": 4, "codigo": "DOC-202", "nombre": "DR. RICARDO CHAVEZ DIAZ", "especialidad": "Derecho Constitucional", "facultad": "Facultad de Derecho"},
            {"id_docente": 5, "codigo": "DOC-301", "nombre": "DR. GUILLERMO QUISPE FLORES", "especialidad": "Anatomía y Cirugía", "facultad": "Facultad de Medicina"},
            {"id_docente": 6, "codigo": "DRA. SOFIA ALVAREZ MAMANI", "especialidad": "Farmacología Clínica", "facultad": "Facultad de Medicina"},
            {"id_docente": 7, "codigo": "DOC-401", "nombre": "MSC. FERNANDO SANCHEZ RAMOS", "especialidad": "Finanzas y Gestión", "facultad": "Facultad de Administración"},
            {"id_docente": 8, "codigo": "DOC-402", "nombre": "DR. LUIS TORRES GOMEZ", "especialidad": "Comportamiento Organizacional", "facultad": "Facultad de Administración"}
        ]

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de todos los docentes."""
        query = "SELECT id_docente, codigo, nombre, especialidad, facultad FROM dbo.DimDocente ORDER BY nombre"
        resultados = self.db.ejecutar_consulta(query)
        
        if self.db.mock_mode or not resultados:
            return self._mock_docentes
        return resultados

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca un docente por su código único."""
        query = "SELECT id_docente, codigo, nombre, especialidad, facultad FROM dbo.DimDocente WHERE codigo = ?"
        resultados = self.db.ejecutar_consulta(query, (codigo,))
        
        if self.db.mock_mode or not resultados:
            for doc in self._mock_docentes:
                if doc["codigo"] == codigo:
                    return doc
            return None
        return resultados[0]

    def crear_docente(self, codigo: str, nombre: str, especialidad: str, facultad: str) -> bool:
        """Crea un nuevo registro de docente."""
        query = "INSERT INTO dbo.DimDocente (codigo, nombre, especialidad, facultad) VALUES (?, ?, ?, ?)"
        exito = self.db.ejecutar_comando(query, (codigo, nombre, especialidad, facultad))
        
        if self.db.mock_mode:
            nuevo = {
                "id_docente": len(self._mock_docentes) + 1,
                "codigo": codigo,
                "nombre": nombre.upper(),
                "especialidad": especialidad,
                "facultad": facultad
            }
            self._mock_docentes.append(nuevo)
            return True
        return exito

    def actualizar_docente(self, codigo: str, especialidad: str, facultad: str) -> bool:
        """Actualiza la especialidad y facultad de un docente."""
        query = "UPDATE dbo.DimDocente SET especialidad = ?, facultad = ? WHERE codigo = ?"
        exito = self.db.ejecutar_comando(query, (especialidad, facultad, codigo))
        
        if self.db.mock_mode:
            for doc in self._mock_docentes:
                if doc["codigo"] == codigo:
                    doc["especialidad"] = especialidad
                    doc["facultad"] = facultad
                    return True
            return False
        return exito

    def eliminar_docente(self, codigo: str) -> bool:
        """Elimina un docente."""
        query = "DELETE FROM dbo.DimDocente WHERE codigo = ?"
        exito = self.db.ejecutar_comando(query, (codigo,))
        
        if self.db.mock_mode:
            for doc in self._mock_docentes:
                if doc["codigo"] == codigo:
                    self._mock_docentes.remove(doc)
                    return True
            return False
        return exito
