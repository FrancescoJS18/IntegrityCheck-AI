-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 2: Tablas de la Staging Area (Landing Zone)
-- Autor: Grupo 4 - Universidad Peruana
-- ==========================================

USE IntegrityCheckAI;
GO

-- Limpiar tablas si existen
IF OBJECT_ID('dbo.stg_incidentes', 'U') IS NOT NULL DROP TABLE dbo.stg_incidentes;
IF OBJECT_ID('dbo.stg_logs_examen', 'U') IS NOT NULL DROP TABLE dbo.stg_logs_examen;
IF OBJECT_ID('dbo.stg_similitud_turnitin', 'U') IS NOT NULL DROP TABLE dbo.stg_similitud_turnitin;
IF OBJECT_ID('dbo.stg_actividad_lms', 'U') IS NOT NULL DROP TABLE dbo.stg_actividad_lms;
IF OBJECT_ID('dbo.stg_notas', 'U') IS NOT NULL DROP TABLE dbo.stg_notas;
IF OBJECT_ID('dbo.stg_estudiantes', 'U') IS NOT NULL DROP TABLE dbo.stg_estudiantes;
GO

-- 1. Staging de Estudiantes
CREATE TABLE dbo.stg_estudiantes (
    codigo VARCHAR(50) NULL,
    nombre VARCHAR(150) NULL,
    ciclo VARCHAR(20) NULL,
    carrera VARCHAR(100) NULL,
    fecha_ingreso VARCHAR(50) NULL,
    sede_codigo VARCHAR(50) NULL,
    sede_nombre VARCHAR(100) NULL,
    sede_ciudad VARCHAR(100) NULL,
    sede_region VARCHAR(100) NULL,
    
    -- Campos obligatorios de Auditoría/Carga Staging
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE', -- VALIDO / INVALIDO / CUARENTENA
    error_detalle VARCHAR(MAX) NULL
);

-- 2. Staging de Notas y Matrículas (SGA)
CREATE TABLE dbo.stg_notas (
    estudiante_codigo VARCHAR(50) NULL,
    curso_codigo VARCHAR(50) NULL,
    curso_nombre VARCHAR(150) NULL,
    curso_creditos VARCHAR(10) NULL,
    curso_tipo VARCHAR(50) NULL, -- OBLIGATORIO / ELECTIVO
    docente_codigo VARCHAR(50) NULL,
    docente_nombre VARCHAR(150) NULL,
    docente_especialidad VARCHAR(100) NULL,
    docente_facultad VARCHAR(100) NULL,
    decano_nombre VARCHAR(150) NULL,
    nota_actual VARCHAR(10) NULL,
    nota_anterior VARCHAR(10) NULL,
    variacion_nota VARCHAR(10) NULL,
    ciclo_academico VARCHAR(20) NULL,
    
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    error_detalle VARCHAR(MAX) NULL
);

-- 3. Staging de Logs de Actividad LMS Moodle
CREATE TABLE dbo.stg_actividad_lms (
    estudiante_codigo VARCHAR(50) NULL,
    curso_codigo VARCHAR(50) NULL,
    accesos_lms_semana VARCHAR(20) NULL,
    foros_participaciones VARCHAR(20) NULL,
    descargas_recursos VARCHAR(20) NULL,
    promedio_tiempo_sesion_min VARCHAR(20) NULL,
    
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    error_detalle VARCHAR(MAX) NULL
);

-- 4. Staging de Similitud Turnitin
CREATE TABLE dbo.stg_similitud_turnitin (
    estudiante_codigo VARCHAR(50) NULL,
    curso_codigo VARCHAR(50) NULL,
    tipo_prueba VARCHAR(50) NULL, -- TRABAJO / TESIS / PROYECTO
    porcentaje_similitud VARCHAR(10) NULL,
    texto_trabajo VARCHAR(MAX) NULL,
    url_reporte VARCHAR(250) NULL,
    
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    error_detalle VARCHAR(MAX) NULL
);

-- 5. Staging de Logs de Examen (Plataforma de Evaluaciones)
CREATE TABLE dbo.stg_logs_examen (
    estudiante_codigo VARCHAR(50) NULL,
    curso_codigo VARCHAR(50) NULL,
    tipo_prueba VARCHAR(50) NULL, -- EXAMEN_PARCIAL / EXAMEN_FINAL / PRACTICA
    tiempo_respuesta_examen VARCHAR(20) NULL, -- en minutos
    cambios_ip_examen VARCHAR(20) NULL, -- cantidad de cambios de IP
    ip_registro VARCHAR(50) NULL,
    bloqueos_pantalla VARCHAR(10) NULL,
    fuera_de_tiempo VARCHAR(10) NULL, -- SI / NO
    
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    error_detalle VARCHAR(MAX) NULL
);

-- 6. Staging de Incidentes Reportados (Histórico o Externo)
CREATE TABLE dbo.stg_incidentes (
    estudiante_codigo VARCHAR(50) NULL,
    docente_codigo VARCHAR(50) NULL,
    curso_codigo VARCHAR(50) NULL,
    tipo_fraude_codigo VARCHAR(50) NULL,
    tipo_fraude_nombre VARCHAR(100) NULL,
    tipo_fraude_descripcion VARCHAR(500) NULL,
    nivel_gravedad VARCHAR(20) NULL, -- LEVE / MODERADO / GRAVE
    puntaje_riesgo VARCHAR(10) NULL,
    porcentaje_similitud VARCHAR(10) NULL,
    estado_caso VARCHAR(50) NULL, -- PENDIENTE / EN_REVISION / CERRADO
    fecha_deteccion VARCHAR(50) NULL,
    fecha_resolucion VARCHAR(50) NULL,
    
    id_carga VARCHAR(50) NOT NULL,
    fecha_ingesta DATETIME NOT NULL DEFAULT GETDATE(),
    estado_validacion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    error_detalle VARCHAR(MAX) NULL
);
GO

PRINT 'Tablas de la Staging Area creadas con éxito.';
GO
