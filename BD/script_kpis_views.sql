-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 6: Capa Semántica (Vistas de KPIs)
-- Autor: Grupo 4 - Universidad Peruana
-- ==========================================

USE IntegrityCheckAI;
GO

-- Limpiar vistas si existen
IF OBJECT_ID('dbo.vw_kpi_tasa_incidentes_facultad', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_tasa_incidentes_facultad;
IF OBJECT_ID('dbo.vw_kpi_indice_integridad', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_indice_integridad;
IF OBJECT_ID('dbo.vw_kpi_casos_por_estado', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_casos_por_estado;
IF OBJECT_ID('dbo.vw_kpi_similitud_promedio_curso', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_similitud_promedio_curso;
IF OBJECT_ID('dbo.vw_kpi_ranking_riesgo_docente', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_ranking_riesgo_docente;
IF OBJECT_ID('dbo.vw_kpi_evolucion_mensual', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_evolucion_mensual;
IF OBJECT_ID('dbo.vw_kpi_tipo_fraude_distribucion', 'V') IS NOT NULL DROP VIEW dbo.vw_kpi_tipo_fraude_distribucion;
GO

-- 1. Tasa de Incidentes por Facultad (incidentes / total_estudiantes por facultad)
CREATE VIEW dbo.vw_kpi_tasa_incidentes_facultad AS
SELECT 
    f.id_facultad,
    f.nombre AS facultad,
    COUNT(fact.id_incidente) AS total_incidentes,
    ISNULL(
        (SELECT COUNT(*) FROM dbo.DimEstudiante e 
         WHERE (f.nombre = 'Facultad de Ingeniería' AND e.carrera LIKE '%Ingeniería%')
            OR (f.nombre = 'Facultad de Derecho' AND e.carrera LIKE '%Derecho%')
            OR (f.nombre = 'Facultad de Medicina' AND e.carrera LIKE '%Medicina%')
            OR (f.nombre = 'Facultad de Administración' AND e.carrera LIKE '%Administración%')
        ), 50
    ) AS total_estudiantes,
    CAST(COUNT(fact.id_incidente) AS DECIMAL(5,2)) / NULLIF(
        CAST(
            ISNULL(
                (SELECT COUNT(*) FROM dbo.DimEstudiante e 
                 WHERE (f.nombre = 'Facultad de Ingeniería' AND e.carrera LIKE '%Ingeniería%')
                    OR (f.nombre = 'Facultad de Derecho' AND e.carrera LIKE '%Derecho%')
                    OR (f.nombre = 'Facultad de Medicina' AND e.carrera LIKE '%Medicina%')
                    OR (f.nombre = 'Facultad de Administración' AND e.carrera LIKE '%Administración%')
                ), 50
            ) AS DECIMAL(5,2)
        ), 0
    ) * 100 AS tasa_incidentes
FROM dbo.DimFacultad f
LEFT JOIN dbo.FactIncidenteFraude fact ON f.id_facultad = fact.id_facultad
GROUP BY f.id_facultad, f.nombre;
GO

-- 2. Índice de Integridad (100 - (incidentes_graves / total * 100))
CREATE VIEW dbo.vw_kpi_indice_integridad AS
SELECT 
    ISNULL(
        100.0 - (CAST(SUM(CASE WHEN tf.nivel_gravedad = 'GRAVE' THEN 1 ELSE 0 END) AS DECIMAL(5,2)) / NULLIF(CAST(COUNT(fact.id_incidente) AS DECIMAL(5,2)), 0) * 100.0),
        100.0
    ) AS indice_integridad,
    COUNT(fact.id_incidente) AS total_incidentes,
    SUM(CASE WHEN tf.nivel_gravedad = 'GRAVE' THEN 1 ELSE 0 END) AS total_graves
FROM dbo.FactIncidenteFraude fact
INNER JOIN dbo.DimTipoFraude tf ON fact.id_tipo_fraude = tf.id_tipo_fraude;
GO

-- 3. Casos por Estado (COUNT por PENDIENTE/EN_REVISION/CERRADO)
CREATE VIEW dbo.vw_kpi_casos_por_estado AS
SELECT 
    estado_caso,
    COUNT(*) AS total_casos
FROM dbo.FactIncidenteFraude
GROUP BY estado_caso;
GO

-- 4. Similitud Promedio por Curso (AVG(porcentaje_similitud) por curso)
CREATE VIEW dbo.vw_kpi_similitud_promedio_curso AS
SELECT 
    c.codigo AS curso_codigo,
    c.nombre AS curso_nombre,
    AVG(fact.porcentaje_similitud) AS similitud_promedio
FROM dbo.DimCurso c
INNER JOIN dbo.FactIncidenteFraude fact ON c.id_curso = fact.id_curso
GROUP BY c.codigo, c.nombre;
GO

-- 5. Ranking de Riesgo por Docente (ranking docentes por avg(puntaje_riesgo) alumnos)
CREATE VIEW dbo.vw_kpi_ranking_riesgo_docente AS
SELECT 
    d.codigo AS docente_codigo,
    d.nombre AS docente_nombre,
    d.facultad AS docente_facultad,
    AVG(fact.puntaje_riesgo) AS promedio_puntaje_riesgo,
    RANK() OVER (ORDER BY AVG(fact.puntaje_riesgo) DESC) AS ranking
FROM dbo.DimDocente d
INNER JOIN dbo.FactIncidenteFraude fact ON d.id_docente = fact.id_docente
GROUP BY d.codigo, d.nombre, d.facultad;
GO

-- 6. Evolución Mensual (incidentes por mes/semestre)
CREATE VIEW dbo.vw_kpi_evolucion_mensual AS
SELECT 
    t.anio,
    t.mes,
    t.semestre,
    COUNT(fact.id_incidente) AS total_incidentes
FROM dbo.DimTiempo t
INNER JOIN dbo.FactIncidenteFraude fact ON t.id_tiempo = fact.id_tiempo
GROUP BY t.anio, t.mes, t.semestre;
GO

-- 7. Distribución por Tipo de Fraude (% por tipo de fraude)
CREATE VIEW dbo.vw_kpi_tipo_fraude_distribucion AS
SELECT 
    tf.nombre AS tipo_fraude,
    COUNT(fact.id_incidente) AS total_casos,
    CAST(COUNT(fact.id_incidente) AS DECIMAL(5,2)) / NULLIF(
        CAST((SELECT COUNT(*) FROM dbo.FactIncidenteFraude) AS DECIMAL(5,2)), 0
    ) * 100 AS porcentaje_distribucion
FROM dbo.DimTipoFraude tf
INNER JOIN dbo.FactIncidenteFraude fact ON tf.id_tipo_fraude = fact.id_tipo_fraude
GROUP BY tf.nombre;
GO

PRINT 'Vistas de KPIs creadas con éxito.';
GO
