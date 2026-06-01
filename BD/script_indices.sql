-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 6: Índices de Rendimiento
-- Autor: Grupo 4 - Universidad Peruana
-- ==========================================

USE IntegrityCheckAI;
GO

-- 1. Índices sobre Claves Foráneas en la Tabla de Hechos (FactIncidenteFraude)
-- Ayuda a optimizar las consultas de agregación y los JOINs del Data Warehouse

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_estudiante' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_estudiante ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_estudiante ON dbo.FactIncidenteFraude(id_estudiante);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_docente' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_docente ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_docente ON dbo.FactIncidenteFraude(id_docente);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_curso' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_curso ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_curso ON dbo.FactIncidenteFraude(id_curso);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_facultad' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_facultad ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_facultad ON dbo.FactIncidenteFraude(id_facultad);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_tipo_fraude' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_tipo_fraude ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_tipo_fraude ON dbo.FactIncidenteFraude(id_tipo_fraude);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_tiempo' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_tiempo ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_tiempo ON dbo.FactIncidenteFraude(id_tiempo);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_sede' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_sede ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_sede ON dbo.FactIncidenteFraude(id_sede);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_tipo_prueba' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_tipo_prueba ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_tipo_prueba ON dbo.FactIncidenteFraude(id_tipo_prueba);
GO

-- 2. Índices para Optimizar Búsquedas y Filtros Frecuentes
-- Optimiza filtros por estado de caso y ordenamiento por nivel de riesgo
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_fact_estado_riesgo' AND object_id = OBJECT_ID('dbo.FactIncidenteFraude'))
    DROP INDEX idx_fact_estado_riesgo ON dbo.FactIncidenteFraude;
CREATE NONCLUSTERED INDEX idx_fact_estado_riesgo 
ON dbo.FactIncidenteFraude(estado_caso, puntaje_riesgo)
INCLUDE (porcentaje_similitud, fecha_deteccion);
GO

-- 3. Índices en Tablas Staging para Acelerar la Fase ETL (Transformación/Carga)
-- Ayuda a buscar rápidamente registros pendientes de validar o correspondientes a una carga en particular
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_stg_estudiantes_carga' AND object_id = OBJECT_ID('dbo.stg_estudiantes'))
    DROP INDEX idx_stg_estudiantes_carga ON dbo.stg_estudiantes;
CREATE NONCLUSTERED INDEX idx_stg_estudiantes_carga ON dbo.stg_estudiantes(id_carga, estado_validacion);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_stg_notas_carga' AND object_id = OBJECT_ID('dbo.stg_notas'))
    DROP INDEX idx_stg_notas_carga ON dbo.stg_notas;
CREATE NONCLUSTERED INDEX idx_stg_notas_carga ON dbo.stg_notas(id_carga, estado_validacion);

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_stg_incidentes_carga' AND object_id = OBJECT_ID('dbo.stg_incidentes'))
    DROP INDEX idx_stg_incidentes_carga ON dbo.stg_incidentes;
CREATE NONCLUSTERED INDEX idx_stg_incidentes_carga ON dbo.stg_incidentes(id_carga, estado_validacion);
GO

PRINT 'Índices de rendimiento creados con éxito.';
GO
