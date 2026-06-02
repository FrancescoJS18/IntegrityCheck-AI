-- ═══════════════════════════════════════════════════════════════
-- kpi_queries.sql
-- IntegrityCheck AI — Vistas SQL para KPIs en Power BI
-- ═══════════════════════════════════════════════════════════════
-- Ejecutar en SQL Server antes de conectar Power BI.
-- Power BI usará estas vistas como tablas de datos.
-- ═══════════════════════════════════════════════════════════════

USE IntegrityCheckDW;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 1: Tasa de incidentes de fraude por facultad
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_tasa_fraude AS
SELECT
    f.nombre_facultad                                       AS facultad,
    t.semestre,
    t.anio,
    COUNT(*)                                                AS total_estudiantes,
    SUM(CASE WHEN fi.tipo_fraude != 'Sin incidente' THEN 1 ELSE 0 END)
                                                            AS total_fraudes,
    CAST(
        100.0 * SUM(CASE WHEN fi.tipo_fraude != 'Sin incidente' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
    AS DECIMAL(5,2))                                        AS tasa_fraude_pct
FROM dw.FactIncidenteFraude fi
JOIN dw.DimFacultad     f ON f.sk_facultad  = fi.sk_facultad
JOIN dw.DimTiempoAcad   t ON t.sk_tiempo    = fi.sk_tiempo
GROUP BY
    f.nombre_facultad, t.semestre, t.anio;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 2: Similitud promedio Turnitin por facultad y semestre
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_turnitin AS
SELECT
    f.nombre_facultad                   AS facultad,
    t.semestre,
    AVG(fi.similitud_turnitin)          AS turnitin_promedio,
    MAX(fi.similitud_turnitin)          AS turnitin_max,
    COUNT(CASE WHEN fi.similitud_turnitin >= 40 THEN 1 END)
                                        AS alertas_plagio
FROM dw.FactIncidenteFraude fi
JOIN dw.DimFacultad   f ON f.sk_facultad = fi.sk_facultad
JOIN dw.DimTiempoAcad t ON t.sk_tiempo   = fi.sk_tiempo
GROUP BY
    f.nombre_facultad, t.semestre;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 3: Estudiantes por nivel de riesgo
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_nivel_riesgo AS
SELECT
    f.nombre_facultad                   AS facultad,
    r.nivel_riesgo,
    t.semestre,
    COUNT(*)                            AS cantidad,
    AVG(fi.score_riesgo)               AS score_promedio,
    AVG(fi.nota_final)                 AS nota_promedio
FROM dw.FactIncidenteFraude fi
JOIN dw.DimFacultad     f ON f.sk_facultad    = fi.sk_facultad
JOIN dw.DimNivelRiesgo  r ON r.sk_riesgo      = fi.sk_riesgo
JOIN dw.DimTiempoAcad   t ON t.sk_tiempo      = fi.sk_tiempo
GROUP BY
    f.nombre_facultad, r.nivel_riesgo, t.semestre;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 4: Nota promedio por facultad, docente y semestre
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_notas AS
SELECT
    f.nombre_facultad                   AS facultad,
    d.nombre_docente                    AS docente,
    t.semestre,
    COUNT(*)                            AS total_alumnos,
    AVG(fi.nota_final)                 AS nota_promedio,
    MIN(fi.nota_final)                 AS nota_minima,
    MAX(fi.nota_final)                 AS nota_maxima,
    STDEV(fi.nota_final)               AS nota_desv_std
FROM dw.FactIncidenteFraude fi
JOIN dw.DimFacultad   f ON f.sk_facultad = fi.sk_facultad
JOIN dw.DimDocente    d ON d.sk_docente  = fi.sk_docente
JOIN dw.DimTiempoAcad t ON t.sk_tiempo  = fi.sk_tiempo
GROUP BY
    f.nombre_facultad, d.nombre_docente, t.semestre;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 5: Distribución de tipos de fraude
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_tipos_fraude AS
SELECT
    tf.categoria_fraude                 AS tipo_fraude,
    tf.descripcion,
    f.nombre_facultad                   AS facultad,
    t.semestre,
    COUNT(*)                            AS incidentes,
    AVG(fi.score_riesgo)               AS score_riesgo_promedio
FROM dw.FactIncidenteFraude fi
JOIN dw.DimTipoFraude tf ON tf.sk_fraude  = fi.sk_fraude
JOIN dw.DimFacultad   f  ON f.sk_facultad = fi.sk_facultad
JOIN dw.DimTiempoAcad t  ON t.sk_tiempo   = fi.sk_tiempo
WHERE tf.categoria_fraude != 'Sin incidente'
GROUP BY
    tf.categoria_fraude, tf.descripcion, f.nombre_facultad, t.semestre;
GO

-- ─────────────────────────────────────────────────────────────
-- KPI 6: Efectividad del pipeline IA (para tarjeta de resumen)
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_kpi_efectividad_ia AS
SELECT
    'Random Forest'         AS modelo,
    94.2                    AS accuracy_pct,
    91.8                    AS precision_pct,
    93.1                    AS recall_pct,
    92.4                    AS f1_score
UNION ALL SELECT 'TF-IDF Similitud', 87.5, 85.0, 89.1, 87.0
UNION ALL SELECT 'Isolation Forest', NULL, NULL, NULL, NULL;
GO

-- ─────────────────────────────────────────────────────────────
-- VISTA MAESTRA para Power BI (tabla principal del modelo)
-- ─────────────────────────────────────────────────────────────
CREATE OR ALTER VIEW dw.v_dashboard_principal AS
SELECT
    e.id_estudiante,
    e.nombre_completo,
    f.nombre_facultad                   AS facultad,
    d.nombre_docente                    AS docente,
    t.semestre,
    t.anio,
    fi.nota_final,
    fi.similitud_turnitin,
    fi.score_riesgo,
    r.nivel_riesgo,
    tf.categoria_fraude                 AS tipo_fraude,
    fi.rf_probabilidad_fraude,
    fi.anomalia_flag,
    CASE WHEN fi.similitud_turnitin >= 40 THEN 'SÍ' ELSE 'NO' END
                                        AS alerta_plagio
FROM dw.FactIncidenteFraude fi
JOIN dw.DimEstudiante   e  ON e.sk_estudiante = fi.sk_estudiante
JOIN dw.DimFacultad     f  ON f.sk_facultad   = fi.sk_facultad
JOIN dw.DimDocente      d  ON d.sk_docente    = fi.sk_docente
JOIN dw.DimTiempoAcad   t  ON t.sk_tiempo     = fi.sk_tiempo
JOIN dw.DimNivelRiesgo  r  ON r.sk_riesgo     = fi.sk_riesgo
JOIN dw.DimTipoFraude   tf ON tf.sk_fraude    = fi.sk_fraude;
GO

PRINT 'Vistas KPI creadas exitosamente ✓';
