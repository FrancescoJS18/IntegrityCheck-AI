-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 1: Script de Datos de Prueba
-- Autor: Grupo 4 - Universidad Peruana
-- Genera: 4 Sedes, 4 Facultades, 10 Cursos, 8 Docentes,
--         8 Tipos de Fraude, 200+ Estudiantes Peruanos,
--         Fechas en DimTiempo y 60+ Incidentes de Fraude.
-- ==========================================

USE IntegrityCheckAI;
GO

-- Desactivar constraints temporalmente si fuera necesario para limpieza
-- Pero aquí limpiamos en orden inverso
TRUNCATE TABLE dbo.FactIncidenteFraude;
DELETE FROM dbo.DimEstudiante;
DELETE FROM dbo.DimDocente;
DELETE FROM dbo.DimCurso;
DELETE FROM dbo.DimFacultad;
DELETE FROM dbo.DimSede;
DELETE FROM dbo.DimTipoFraude;
DELETE FROM dbo.DimTipoPrueba;
DELETE FROM dbo.DimTiempo;
GO

-- 1. Insertar DimSede
INSERT INTO dbo.DimSede (codigo, nombre, ciudad, region) VALUES
('LIM_CEN', 'Sede Central - Lima', 'Lima', 'Lima'),
('AQP_SEDE', 'Sede Arequipa', 'Arequipa', 'Arequipa'),
('TRU_SEDE', 'Sede Trujillo', 'Trujillo', 'La Libertad'),
('CUS_SEDE', 'Sede Cusco', 'Cusco', 'Cusco');

-- 2. Insertar DimFacultad
INSERT INTO dbo.DimFacultad (codigo, nombre, decano, sede) VALUES
('ING_FAC', 'Facultad de Ingeniería', 'Dr. Alberto Quispe Torres', 'Sede Central - Lima'),
('DER_FAC', 'Facultad de Derecho', 'Dra. Beatriz Flores Ramos', 'Sede Central - Lima'),
('MED_FAC', 'Facultad de Medicina', 'Dr. Carlos Mendoza Chavez', 'Sede Central - Lima'),
('ADM_FAC', 'Facultad de Administración', 'Dra. Diana Vargas Diaz', 'Sede Central - Lima');

-- 3. Insertar DimCurso
INSERT INTO dbo.DimCurso (codigo, nombre, creditos, tipo) VALUES
('INF-101', 'Introducción a la Algoritmia', 4, 'OBLIGATORIO'),
('INF-302', 'Base de Datos I', 4, 'OBLIGATORIO'),
('DER-102', 'Derecho Constitucional Peruano', 3, 'OBLIGATORIO'),
('DER-205', 'Derecho Penal General', 4, 'OBLIGATORIO'),
('MED-103', 'Anatomía Humana I', 5, 'OBLIGATORIO'),
('MED-402', 'Farmacología General', 5, 'OBLIGATORIO'),
('ADM-104', 'Administración General', 3, 'OBLIGATORIO'),
('ADM-306', 'Finanzas Corporativas', 4, 'OBLIGATORIO'),
('INF-405', 'Inteligencia Artificial', 4, 'ELECTIVO'),
('DER-408', 'Derecho Internacional Público', 3, 'ELECTIVO');

-- 4. Insertar DimDocente
INSERT INTO dbo.DimDocente (codigo, nombre, especialidad, facultad) VALUES
('DOC-101', 'Dr. Javier Huaman Sanchez', 'Sistemas e Informática', 'Facultad de Ingeniería'),
('DOC-102', 'MSc. Elena Gomez Ruiz', 'Inteligencia Artificial', 'Facultad de Ingeniería'),
('DOC-201', 'Dra. Patricia Ramos Castro', 'Derecho Penal', 'Facultad de Derecho'),
('DOC-202', 'Dr. Ricardo Chavez Diaz', 'Derecho Constitucional', 'Facultad de Derecho'),
('DOC-301', 'Dr. Guillermo Quispe Flores', 'Anatomía y Cirugía', 'Facultad de Medicina'),
('DOC-302', 'Dra. Sofia Alvarez Mamani', 'Farmacología Clínica', 'Facultad de Medicina'),
('DOC-401', 'MSc. Fernando Sanchez Ramos', 'Finanzas y Gestión', 'Facultad de Administración'),
('DOC-402', 'Dr. Luis Torres Gomez', 'Comportamiento Organizacional', 'Facultad de Administración');

-- 5. Insertar DimTipoFraude
INSERT INTO dbo.DimTipoFraude (codigo, nombre, descripcion, nivel_gravedad) VALUES
('FR-01', 'Plagio de Trabajo Académico', 'Similitud elevada en Turnitin sin citar fuentes correctas', 'MODERADO'),
('FR-02', 'Plagio de Tesis/Proyecto', 'Copia sustancial de trabajos de investigación de grado', 'GRAVE'),
('FR-03', 'Copia en Examen Escrito/Virtual', 'Compartir respuestas o uso de material no autorizado', 'MODERADO'),
('FR-04', 'Suplantación de Identidad', 'Rendir examen en lugar de otro estudiante', 'GRAVE'),
('FR-05', 'Uso no autorizado de IA Generativa', 'Redacción íntegra por bots (ChatGPT, etc.) en entregables', 'LEVE'),
('FR-06', 'Colusión en Exámenes', 'Intercambio de IPs o patrones idénticos de respuesta entre alumnos', 'MODERADO'),
('FR-07', 'Alteración de Calificaciones', 'Acceso indebido al sistema SGA para cambiar notas', 'GRAVE'),
('FR-08', 'Fabricación de Datos de Campo', 'Inventar datos en reportes de laboratorio o tesis', 'LEVE');

-- 6. Insertar DimTipoPrueba
INSERT INTO dbo.DimTipoPrueba (codigo, nombre) VALUES
('EXAMEN_PARCIAL', 'EXAMEN_PARCIAL'),
('EXAMEN_FINAL', 'EXAMEN_FINAL'),
('PRACTICA', 'PRACTICA'),
('TRABAJO', 'TRABAJO'),
('TESIS', 'TESIS'),
('PROYECTO', 'PROYECTO');

-- 7. Insertar DimTiempo
-- Generar fechas del 2026-01-01 al 2026-06-30
DECLARE @StartDate DATE = '2026-01-01';
DECLARE @EndDate DATE = '2026-06-30';
WHILE @StartDate <= @EndDate
BEGIN
    INSERT INTO dbo.DimTiempo (fecha, dia, semana, mes, semestre, anio, es_periodo_examenes)
    VALUES (
        @StartDate,
        DAY(@StartDate),
        DATEPART(WEEK, @StartDate),
        MONTH(@StartDate),
        '2026-I',
        2026,
        CASE WHEN MONTH(@StartDate) IN (5, 7) THEN 1 ELSE 0 END
    );
    SET @StartDate = DATEADD(DAY, 1, @StartDate);
END;
GO

-- 8. Generar 200+ Estudiantes Peruanos usando combinación de nombres y apellidos
WITH PrimerosNombres AS (
    SELECT 'Juan' AS Nombre UNION SELECT 'Maria' UNION SELECT 'Jose' UNION SELECT 'Ana' UNION
    SELECT 'Luis' UNION SELECT 'Carlos' UNION SELECT 'Jorge' UNION SELECT 'Rosa' UNION
    SELECT 'Pedro' UNION SELECT 'Gabriela' UNION SELECT 'Diego' UNION SELECT 'Sofia' UNION
    SELECT 'Camila' UNION SELECT 'Alejandro' UNION SELECT 'Luz' UNION SELECT 'Manuel' UNION
    SELECT 'Carmen' UNION SELECT 'Miguel' UNION SELECT 'Lucia' UNION SELECT 'Victor'
),
ApellidosPaternos AS (
    SELECT 'Quispe' AS Apellido UNION SELECT 'Flores' UNION SELECT 'Sanchez' UNION SELECT 'Rodriguez' UNION
    SELECT 'Gomez' UNION SELECT 'Mendoza' UNION SELECT 'Huaman' UNION SELECT 'Mamani' UNION
    SELECT 'Ramos' UNION SELECT 'Vargas' UNION SELECT 'Diaz' UNION SELECT 'Castro' UNION
    SELECT 'Ruiz' UNION SELECT 'Chavez' UNION SELECT 'Alvarez' UNION SELECT 'Torres'
),
ApellidosMaternos AS (
    SELECT 'Villanueva' AS Apellido2 UNION SELECT 'Arias' UNION SELECT 'Ortiz' UNION SELECT 'Silva' UNION
    SELECT 'Benitez' UNION SELECT 'Reyes' UNION SELECT 'Morales' UNION SELECT 'Rojas' UNION
    SELECT 'Gutierrez' UNION SELECT 'Medina' UNION SELECT 'Guerrero' UNION SELECT 'Salazar' UNION
    SELECT 'Paredes' UNION SELECT 'Delgado' UNION SELECT 'Aguilar' UNION SELECT 'Espinoza'
),
EstudiantesCombinados AS (
    SELECT 
        ROW_NUMBER() OVER(ORDER BY n.Nombre, ap.Apellido, am.Apellido2) AS RowNum,
        n.Nombre + ' ' + ap.Apellido + ' ' + am.Apellido2 AS NombreCompleto
    FROM PrimerosNombres n
    CROSS JOIN ApellidosPaternos ap
    CROSS JOIN ApellidosMaternos am
)
INSERT INTO dbo.DimEstudiante (codigo, nombre, ciclo, carrera, fecha_ingreso)
SELECT 
    '2022' + RIGHT('0000' + CAST(RowNum AS VARCHAR), 4) AS codigo,
    NombreCompleto AS nombre,
    (RowNum % 10) + 1 AS ciclo,
    CASE 
        WHEN RowNum % 4 = 0 THEN 'Ingeniería de Sistemas'
        WHEN RowNum % 4 = 1 THEN 'Derecho'
        WHEN RowNum % 4 = 2 THEN 'Medicina Humana'
        ELSE 'Administración de Empresas'
    END AS carrera,
    DATEADD(DAY, -((RowNum % 1000) + 200), '2026-01-01') AS fecha_ingreso
FROM EstudiantesCombinados
WHERE RowNum <= 210; -- Nos aseguramos de tener al menos 200
GO

-- 9. Insertar 60+ Incidentes de prueba en FactIncidenteFraude
-- Combinamos estudiantes con cursos, docentes, facultades y tipos de fraude para armar casos variados.
-- Usaremos una lógica para mapear facultades de acuerdo a las carreras.
-- Asignamos puntajes de riesgo, similitudes y estados variados.

-- Creamos una tabla temporal de apoyo para mapear y generar
WITH CasosBase AS (
    SELECT 
        e.id_estudiante,
        e.codigo AS est_codigo,
        e.carrera,
        -- Mapeo de facultad
        CASE 
            WHEN e.carrera = 'Ingeniería de Sistemas' THEN 'ING_FAC'
            WHEN e.carrera = 'Derecho' THEN 'DER_FAC'
            WHEN e.carrera = 'Medicina Humana' THEN 'MED_FAC'
            ELSE 'ADM_FAC'
        END AS fac_codigo,
        -- Mapeo de curso idóneo para su facultad
        CASE 
            WHEN e.carrera = 'Ingeniería de Sistemas' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'INF-101' ELSE 'INF-302' END)
            WHEN e.carrera = 'Derecho' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'DER-102' ELSE 'DER-205' END)
            WHEN e.carrera = 'Medicina Humana' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'MED-103' ELSE 'MED-402' END)
            ELSE (CASE WHEN e.id_estudiante % 2 = 0 THEN 'ADM-104' ELSE 'ADM-306' END)
        END AS cur_codigo,
        -- Mapeo de docente
        CASE 
            WHEN e.carrera = 'Ingeniería de Sistemas' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'DOC-101' ELSE 'DOC-102' END)
            WHEN e.carrera = 'Derecho' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'DOC-201' ELSE 'DOC-202' END)
            WHEN e.carrera = 'Medicina Humana' THEN (CASE WHEN e.id_estudiante % 2 = 0 THEN 'DOC-301' ELSE 'DOC-302' END)
            ELSE (CASE WHEN e.id_estudiante % 2 = 0 THEN 'DOC-401' ELSE 'DOC-402' END)
        END AS doc_codigo
    FROM dbo.DimEstudiante e
)
INSERT INTO dbo.FactIncidenteFraude (
    id_estudiante, id_docente, id_curso, id_facultad, id_tipo_fraude, 
    id_tiempo, id_sede, id_tipo_prueba, puntaje_riesgo, porcentaje_similitud, 
    estado_caso, fecha_deteccion, fecha_resolucion
)
SELECT 
    cb.id_estudiante,
    d.id_docente,
    c.id_curso,
    f.id_facultad,
    tf.id_tipo_fraude,
    t.id_tiempo,
    s.id_sede,
    tp.id_tipo_prueba,
    -- Generar puntajes realistas de riesgo (0 - 100)
    CAST((cb.id_estudiante * 17) % 60 + 35 AS DECIMAL(5,2)) AS puntaje_riesgo,
    -- Similitud de Turnitin (0 - 100)
    CAST(CASE WHEN tf.codigo IN ('FR-01', 'FR-02') THEN (cb.id_estudiante * 13) % 45 + 50 ELSE 0 END AS DECIMAL(5,2)) AS porcentaje_similitud,
    -- Estado
    CASE 
        WHEN cb.id_estudiante % 3 = 0 THEN 'PENDIENTE'
        WHEN cb.id_estudiante % 3 = 1 THEN 'EN_REVISION'
        ELSE 'CERRADO'
    END AS estado_caso,
    -- Fechas de detección distribuidas
    DATEADD(HOUR, cb.id_estudiante % 24, CAST(t.fecha AS DATETIME)) AS fecha_deteccion,
    -- Fecha de resolución (solo si está cerrado)
    CASE 
        WHEN cb.id_estudiante % 3 = 2 THEN DATEADD(DAY, 4, CAST(t.fecha AS DATETIME))
        ELSE NULL
    END AS fecha_resolucion
FROM CasosBase cb
INNER JOIN dbo.DimDocente d ON cb.doc_codigo = d.codigo
INNER JOIN dbo.DimCurso c ON cb.cur_codigo = c.codigo
INNER JOIN dbo.DimFacultad f ON cb.fac_codigo = f.codigo
-- Cruzamos con un tipo de fraude basado en el ID del estudiante para variación
INNER JOIN dbo.DimTipoFraude tf ON tf.codigo = 'FR-0' + CAST(((cb.id_estudiante % 8) + 1) AS VARCHAR)
-- Sedes distribuidas
INNER JOIN dbo.DimSede s ON s.codigo = CASE 
    WHEN cb.id_estudiante % 4 = 0 THEN 'LIM_CEN'
    WHEN cb.id_estudiante % 4 = 1 THEN 'AQP_SEDE'
    WHEN cb.id_estudiante % 4 = 2 THEN 'TRU_SEDE'
    ELSE 'CUS_SEDE'
END
-- Pruebas distribuidas
INNER JOIN dbo.DimTipoPrueba tp ON tp.codigo = CASE 
    WHEN cb.id_estudiante % 6 = 0 THEN 'EXAMEN_PARCIAL'
    WHEN cb.id_estudiante % 6 = 1 THEN 'EXAMEN_FINAL'
    WHEN cb.id_estudiante % 6 = 2 THEN 'PRACTICA'
    WHEN cb.id_estudiante % 6 = 3 THEN 'TRABAJO'
    WHEN cb.id_estudiante % 6 = 4 THEN 'TESIS'
    ELSE 'PROYECTO'
END
-- Fechas asociadas a la detección en Mayo y Junio de 2026
INNER JOIN dbo.DimTiempo t ON t.fecha = DATEADD(DAY, (cb.id_estudiante % 40) + 120, '2026-01-01')
WHERE cb.id_estudiante <= 75; -- Esto genera exactamente 75 incidentes de fraude variados (>50)
GO

PRINT 'Datos de prueba insertados con éxito en dimensiones y tabla de hechos.';
GO
