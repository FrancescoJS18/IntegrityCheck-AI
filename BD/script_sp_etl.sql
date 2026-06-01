-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 3: Proceso ETL (T-SQL Stored Procedures)
-- Autor: Grupo 4 - Universidad Peruana
-- ==========================================

USE IntegrityCheckAI;
GO

-- Limpiar Stored Procedures si existen
IF OBJECT_ID('dbo.sp_etl_extract', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_etl_extract;
IF OBJECT_ID('dbo.sp_etl_transform', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_etl_transform;
IF OBJECT_ID('dbo.sp_etl_load', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_etl_load;
GO

-- 1. Stored Procedure: EXTRACT
-- Valida las estructuras de la Staging Area, reportando campos corruptos e incorrectos
CREATE PROCEDURE dbo.sp_etl_extract
    @id_carga VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        PRINT 'Iniciando fase EXTRACT para Carga: ' + @id_carga;
        
        -- Validar stg_estudiantes
        UPDATE dbo.stg_estudiantes
        SET estado_validacion = CASE 
                WHEN codigo IS NULL OR LEN(RTRIM(codigo)) = 0 THEN 'INVALIDO'
                WHEN nombre IS NULL OR LEN(RTRIM(nombre)) = 0 THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN codigo IS NULL OR LEN(RTRIM(codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN nombre IS NULL OR LEN(RTRIM(nombre)) = 0 THEN 'Nombre de estudiante vacío'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        -- Validar stg_notas
        UPDATE dbo.stg_notas
        SET estado_validacion = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'INVALIDO'
                WHEN curso_codigo IS NULL OR LEN(RTRIM(curso_codigo)) = 0 THEN 'INVALIDO'
                WHEN TRY_CAST(nota_actual AS DECIMAL(5,2)) IS NULL THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN curso_codigo IS NULL OR LEN(RTRIM(curso_codigo)) = 0 THEN 'Código de curso vacío'
                WHEN TRY_CAST(nota_actual AS DECIMAL(5,2)) IS NULL THEN 'Nota actual no es numérica'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        -- Validar stg_actividad_lms
        UPDATE dbo.stg_actividad_lms
        SET estado_validacion = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'INVALIDO'
                WHEN TRY_CAST(accesos_lms_semana AS INT) IS NULL THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN TRY_CAST(accesos_lms_semana AS INT) IS NULL THEN 'Accesos LMS no es entero válido'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        -- Validar stg_similitud_turnitin
        UPDATE dbo.stg_similitud_turnitin
        SET estado_validacion = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'INVALIDO'
                WHEN TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) IS NULL THEN 'INVALIDO'
                WHEN TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) < 0 OR TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) > 100 THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) IS NULL THEN 'Similitud no numérica'
                WHEN TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) < 0 OR TRY_CAST(porcentaje_similitud AS DECIMAL(5,2)) > 100 THEN 'Similitud fuera de rango [0-100]'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        -- Validar stg_logs_examen
        UPDATE dbo.stg_logs_examen
        SET estado_validacion = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'INVALIDO'
                WHEN TRY_CAST(tiempo_respuesta_examen AS INT) IS NULL THEN 'INVALIDO'
                WHEN TRY_CAST(cambios_ip_examen AS INT) IS NULL THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN TRY_CAST(tiempo_respuesta_examen AS INT) IS NULL THEN 'Tiempo de respuesta no es numérico'
                WHEN TRY_CAST(cambios_ip_examen AS INT) IS NULL THEN 'Cambios de IP no es numérico'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        -- Validar stg_incidentes
        UPDATE dbo.stg_incidentes
        SET estado_validacion = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'INVALIDO'
                WHEN docente_codigo IS NULL OR LEN(RTRIM(docente_codigo)) = 0 THEN 'INVALIDO'
                WHEN curso_codigo IS NULL OR LEN(RTRIM(curso_codigo)) = 0 THEN 'INVALIDO'
                ELSE 'VALIDO'
            END,
            error_detalle = CASE 
                WHEN estudiante_codigo IS NULL OR LEN(RTRIM(estudiante_codigo)) = 0 THEN 'Código de estudiante vacío'
                WHEN docente_codigo IS NULL OR LEN(RTRIM(docente_codigo)) = 0 THEN 'Código de docente vacío'
                WHEN curso_codigo IS NULL OR LEN(RTRIM(curso_codigo)) = 0 THEN 'Código de curso vacío'
                ELSE NULL
            END
        WHERE id_carga = @id_carga;

        COMMIT TRANSACTION;
        PRINT 'Fase EXTRACT completada para Carga: ' + @id_carga;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        PRINT 'Error en fase EXTRACT: ' + @ErrorMessage;
        THROW;
    END CATCH
END;
GO

-- 2. Stored Procedure: TRANSFORM
-- Limpia, normaliza, realiza cálculos de IP y variaciones de notas, y mapea a códigos estándar
CREATE PROCEDURE dbo.sp_etl_transform
    @id_carga VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    PRINT 'Iniciando fase TRANSFORM para Carga: ' + @id_carga;
    
    -- La transformación en este caso prepara los registros para la carga.
    -- E.g., normalizar textos de sede, carrera, etc., eliminando espacios extras
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Limpieza de textos en Estudiantes
        UPDATE dbo.stg_estudiantes
        SET nombre = UPPER(RTRIM(LTRIM(nombre))),
            carrera = UPPER(RTRIM(LTRIM(carrera)))
        WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO';

        -- Limpieza en Notas y Docentes
        UPDATE dbo.stg_notas
        SET curso_nombre = UPPER(RTRIM(LTRIM(curso_nombre))),
            docente_nombre = UPPER(RTRIM(LTRIM(docente_nombre))),
            docente_facultad = UPPER(RTRIM(LTRIM(docente_facultad)))
        WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO';

        -- Normalizar nombres de Tipo Prueba
        UPDATE dbo.stg_similitud_turnitin
        SET tipo_prueba = UPPER(RTRIM(LTRIM(tipo_prueba)))
        WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO';

        UPDATE dbo.stg_logs_examen
        SET tipo_prueba = UPPER(RTRIM(LTRIM(tipo_prueba)))
        WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO';

        COMMIT TRANSACTION;
        PRINT 'Fase TRANSFORM completada para Carga: ' + @id_carga;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        PRINT 'Error en fase TRANSFORM: ' + @ErrorMessage;
        THROW;
    END CATCH
END;
GO

-- 3. Stored Procedure: LOAD
-- Inserta datos validados y transformados en el Data Warehouse utilizando control de duplicados (MERGE)
CREATE PROCEDURE dbo.sp_etl_load
    @id_carga VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        PRINT 'Iniciando fase LOAD para Carga: ' + @id_carga;

        -- 1. Cargar DimSede desde stg_estudiantes
        MERGE dbo.DimSede AS Target
        USING (
            SELECT DISTINCT sede_codigo, sede_nombre, sede_ciudad, sede_region
            FROM dbo.stg_estudiantes
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND sede_codigo IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.sede_codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, ciudad, region)
            VALUES (Source.sede_codigo, Source.sede_nombre, Source.sede_ciudad, Source.sede_region);

        -- 2. Cargar DimFacultad desde stg_notas / stg_estudiantes
        -- Mapeamos facultad utilizando la facultad del docente y decano de stg_notas
        MERGE dbo.DimFacultad AS Target
        USING (
            SELECT DISTINCT 
                UPPER(LEFT(docente_facultad, 3)) + '_FAC' AS codigo,
                docente_facultad AS nombre,
                ISNULL(decano_nombre, 'DECANO GENERAL') AS decano,
                'SEDE CENTRAL' AS sede
            FROM dbo.stg_notas
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND docente_facultad IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, decano, sede)
            VALUES (Source.codigo, Source.nombre, Source.decano, Source.sede);

        -- 3. Cargar DimEstudiante
        MERGE dbo.DimEstudiante AS Target
        USING (
            SELECT DISTINCT 
                codigo, nombre, 
                CAST(ISNULL(TRY_CAST(ciclo AS INT), 1) AS INT) AS ciclo,
                carrera,
                ISNULL(TRY_CAST(fecha_ingreso AS DATE), GETDATE()) AS fecha_ingreso
            FROM dbo.stg_estudiantes
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO'
        ) AS Source
        ON (Target.codigo = Source.codigo)
        WHEN MATCHED THEN
            UPDATE SET Target.ciclo = Source.ciclo, Target.carrera = Source.carrera
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, ciclo, carrera, fecha_ingreso)
            VALUES (Source.codigo, Source.nombre, Source.ciclo, Source.carrera, Source.fecha_ingreso);

        -- 4. Cargar DimDocente
        MERGE dbo.DimDocente AS Target
        USING (
            SELECT DISTINCT 
                docente_codigo, docente_nombre, 
                ISNULL(docente_especialidad, 'GENERAL') AS docente_especialidad,
                docente_facultad
            FROM dbo.stg_notas
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND docente_codigo IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.docente_codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, especialidad, facultad)
            VALUES (Source.docente_codigo, Source.docente_nombre, Source.docente_especialidad, Source.docente_facultad);

        -- 5. Cargar DimCurso
        MERGE dbo.DimCurso AS Target
        USING (
            SELECT DISTINCT 
                curso_codigo, curso_nombre, 
                CAST(ISNULL(TRY_CAST(curso_creditos AS INT), 4) AS INT) AS creditos,
                CASE WHEN curso_tipo IN ('OBLIGATORIO', 'ELECTIVO') THEN curso_tipo ELSE 'OBLIGATORIO' END AS tipo
            FROM dbo.stg_notas
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND curso_codigo IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.curso_codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, creditos, tipo)
            VALUES (Source.curso_codigo, Source.curso_nombre, Source.creditos, Source.tipo);

        -- 6. Cargar DimTipoFraude
        MERGE dbo.DimTipoFraude AS Target
        USING (
            SELECT DISTINCT 
                tipo_fraude_codigo, tipo_fraude_nombre, tipo_fraude_descripcion,
                CASE WHEN nivel_gravedad IN ('LEVE', 'MODERADO', 'GRAVE') THEN nivel_gravedad ELSE 'MODERADO' END AS nivel_gravedad
            FROM dbo.stg_incidentes
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND tipo_fraude_codigo IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.tipo_fraude_codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre, descripcion, nivel_gravedad)
            VALUES (Source.tipo_fraude_codigo, Source.tipo_fraude_nombre, Source.tipo_fraude_descripcion, Source.nivel_gravedad);

        -- 7. Cargar DimTipoPrueba
        MERGE dbo.DimTipoPrueba AS Target
        USING (
            SELECT DISTINCT tipo_prueba AS codigo, tipo_prueba AS nombre
            FROM dbo.stg_similitud_turnitin
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND tipo_prueba IS NOT NULL
            UNION
            SELECT DISTINCT tipo_prueba AS codigo, tipo_prueba AS nombre
            FROM dbo.stg_logs_examen
            WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO' AND tipo_prueba IS NOT NULL
        ) AS Source
        ON (Target.codigo = Source.codigo)
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (codigo, nombre)
            VALUES (Source.codigo, Source.nombre);

        -- 8. Generar DimTiempo para las fechas involucradas
        -- Extraemos fechas de deteccion
        DECLARE @fecha_min DATE, @fecha_max DATE;
        SELECT 
            @fecha_min = CAST(MIN(TRY_CAST(fecha_deteccion AS DATETIME)) AS DATE),
            @fecha_max = CAST(MAX(TRY_CAST(fecha_deteccion AS DATETIME)) AS DATE)
        FROM dbo.stg_incidentes
        WHERE id_carga = @id_carga AND estado_validacion = 'VALIDO';

        -- Si no hay fechas, usar fecha de hoy
        IF @fecha_min IS NULL
        BEGIN
            SET @fecha_min = CAST(GETDATE() AS DATE);
            SET @fecha_max = CAST(GETDATE() AS DATE);
        END

        -- Rellenar DimTiempo en bucle para el rango
        DECLARE @fecha_actual DATE = @fecha_min;
        WHILE @fecha_actual <= @fecha_max
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM dbo.DimTiempo WHERE fecha = @fecha_actual)
            BEGIN
                INSERT INTO dbo.DimTiempo (fecha, dia, semana, mes, semestre, anio, es_periodo_examenes)
                VALUES (
                    @fecha_actual,
                    DAY(@fecha_actual),
                    DATEPART(WEEK, @fecha_actual),
                    MONTH(@fecha_actual),
                    CAST(YEAR(@fecha_actual) AS VARCHAR(4)) + '-' + CASE WHEN MONTH(@fecha_actual) <= 6 THEN 'I' ELSE 'II' END,
                    YEAR(@fecha_actual),
                    CASE WHEN MONTH(@fecha_actual) IN (5, 7, 10, 12) THEN 1 ELSE 0 END -- meses comunes de examenes parciales/finales
                );
            END
            SET @fecha_actual = DATEADD(DAY, 1, @fecha_actual);
        END

        -- 9. Cargar FactIncidenteFraude
        -- Hacemos la inserción directa para incidentes procesados válidos
        -- Buscando sus correspondientes IDs en las dimensiones
        INSERT INTO dbo.FactIncidenteFraude (
            id_estudiante, id_docente, id_curso, id_facultad, id_tipo_fraude, 
            id_tiempo, id_sede, id_tipo_prueba, puntaje_riesgo, porcentaje_similitud, 
            estado_caso, fecha_deteccion, fecha_resolucion
        )
        SELECT 
            e.id_estudiante,
            d.id_docente,
            c.id_curso,
            f.id_facultad,
            tf.id_tipo_fraude,
            t.id_tiempo,
            s.id_sede,
            tp.id_tipo_prueba,
            CAST(ISNULL(TRY_CAST(stg.puntaje_riesgo AS DECIMAL(5,2)), 0.0) AS DECIMAL(5,2)) AS puntaje_riesgo,
            CAST(ISNULL(TRY_CAST(stg.porcentaje_similitud AS DECIMAL(5,2)), 0.0) AS DECIMAL(5,2)) AS porcentaje_similitud,
            stg.estado_caso,
            CAST(stg.fecha_deteccion AS DATETIME) AS fecha_deteccion,
            TRY_CAST(stg.fecha_resolucion AS DATETIME) AS fecha_resolucion
        FROM dbo.stg_incidentes stg
        INNER JOIN dbo.DimEstudiante e ON stg.estudiante_codigo = e.codigo
        INNER JOIN dbo.DimDocente d ON stg.docente_codigo = d.codigo
        INNER JOIN dbo.DimCurso c ON stg.curso_codigo = c.codigo
        INNER JOIN dbo.DimTipoFraude tf ON stg.tipo_fraude_codigo = tf.codigo
        INNER JOIN dbo.DimTiempo t ON CAST(stg.fecha_deteccion AS DATE) = t.fecha
        INNER JOIN dbo.DimFacultad f ON f.codigo = UPPER(LEFT(d.facultad, 3)) + '_FAC'
        -- Buscamos sede del estudiante
        INNER JOIN dbo.stg_estudiantes stg_e ON e.codigo = stg_e.codigo
        INNER JOIN dbo.DimSede s ON stg_e.sede_codigo = s.codigo
        -- Buscamos tipo de prueba
        LEFT JOIN (
            -- cruce de tipo prueba por si acaso, sino default EXAMEN_PARCIAL
            SELECT DISTINCT estudiante_codigo, curso_codigo, tipo_prueba FROM dbo.stg_logs_examen
            UNION
            SELECT DISTINCT estudiante_codigo, curso_codigo, tipo_prueba FROM dbo.stg_similitud_turnitin
        ) test_run ON stg.estudiante_codigo = test_run.estudiante_codigo AND stg.curso_codigo = test_run.curso_codigo
        INNER JOIN dbo.DimTipoPrueba tp ON tp.codigo = ISNULL(test_run.tipo_prueba, 'EXAMEN_PARCIAL')
        WHERE stg.id_carga = @id_carga AND stg.estado_validacion = 'VALIDO';

        COMMIT TRANSACTION;
        PRINT 'Fase LOAD completada para Carga: ' + @id_carga;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        PRINT 'Error en fase LOAD: ' + @ErrorMessage;
        THROW;
    END CATCH
END;
GO

PRINT 'Stored Procedures del ETL creados con éxito.';
GO
