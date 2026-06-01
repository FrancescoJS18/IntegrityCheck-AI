-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 4: Data Warehouse (Modelo Estrella / Copo de Nieve)
-- Autor: Grupo 4 - Universidad Peruana
-- ==========================================

USE IntegrityCheckAI;
GO

-- Limpiar Fact y Dimensiones si existen
IF OBJECT_ID('dbo.FactIncidenteFraude', 'F') IS NOT NULL DROP TABLE dbo.FactIncidenteFraude;
IF OBJECT_ID('dbo.DimEstudiante', 'U') IS NOT NULL DROP TABLE dbo.DimEstudiante;
IF OBJECT_ID('dbo.DimDocente', 'U') IS NOT NULL DROP TABLE dbo.DimDocente;
IF OBJECT_ID('dbo.DimCurso', 'U') IS NOT NULL DROP TABLE dbo.DimCurso;
IF OBJECT_ID('dbo.DimFacultad', 'U') IS NOT NULL DROP TABLE dbo.DimFacultad;
IF OBJECT_ID('dbo.DimTipoFraude', 'U') IS NOT NULL DROP TABLE dbo.DimTipoFraude;
IF OBJECT_ID('dbo.DimTiempo', 'U') IS NOT NULL DROP TABLE dbo.DimTiempo;
IF OBJECT_ID('dbo.DimSede', 'U') IS NOT NULL DROP TABLE dbo.DimSede;
IF OBJECT_ID('dbo.DimTipoPrueba', 'U') IS NOT NULL DROP TABLE dbo.DimTipoPrueba;
GO

-- 1. Dimensión Sede
CREATE TABLE dbo.DimSede (
    id_sede INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL
);

-- 2. Dimensión Facultad
CREATE TABLE dbo.DimFacultad (
    id_facultad INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    decano VARCHAR(150) NOT NULL,
    sede VARCHAR(100) NOT NULL
);

-- 3. Dimensión Estudiante
CREATE TABLE dbo.DimEstudiante (
    id_estudiante INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    ciclo INT NOT NULL,
    carrera VARCHAR(100) NOT NULL,
    fecha_ingreso DATE NOT NULL
);

-- 4. Dimensión Docente
CREATE TABLE dbo.DimDocente (
    id_docente INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    facultad VARCHAR(100) NOT NULL
);

-- 5. Dimensión Curso
CREATE TABLE dbo.DimCurso (
    id_curso INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    creditos INT NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('OBLIGATORIO', 'ELECTIVO'))
);

-- 6. Dimensión Tipo de Fraude
CREATE TABLE dbo.DimTipoFraude (
    id_tipo_fraude INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500) NULL,
    nivel_gravedad VARCHAR(50) NOT NULL CHECK (nivel_gravedad IN ('LEVE', 'MODERADO', 'GRAVE'))
);

-- 7. Dimensión Tiempo
CREATE TABLE dbo.DimTiempo (
    id_tiempo INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    dia INT NOT NULL,
    semana INT NOT NULL,
    mes INT NOT NULL,
    semestre VARCHAR(20) NOT NULL,
    anio INT NOT NULL,
    es_periodo_examenes BIT NOT NULL DEFAULT 0
);

-- 8. Dimensión Tipo de Prueba
CREATE TABLE dbo.DimTipoPrueba (
    id_tipo_prueba INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL CHECK (nombre IN ('EXAMEN_PARCIAL', 'EXAMEN_FINAL', 'PRACTICA', 'TRABAJO', 'TESIS', 'PROYECTO'))
);

-- 9. Tabla de Hechos: FactIncidenteFraude
CREATE TABLE dbo.FactIncidenteFraude (
    id_incidente INT IDENTITY(1,1) PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_docente INT NOT NULL,
    id_curso INT NOT NULL,
    id_facultad INT NOT NULL,
    id_tipo_fraude INT NOT NULL,
    id_tiempo INT NOT NULL,
    id_sede INT NOT NULL,
    id_tipo_prueba INT NOT NULL,
    puntaje_riesgo DECIMAL(5,2) NOT NULL CHECK (puntaje_riesgo BETWEEN 0.00 AND 100.00),
    porcentaje_similitud DECIMAL(5,2) NOT NULL CHECK (porcentaje_similitud BETWEEN 0.00 AND 100.00),
    estado_caso VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado_caso IN ('PENDIENTE', 'EN_REVISION', 'CERRADO')),
    fecha_deteccion DATETIME NOT NULL DEFAULT GETDATE(),
    fecha_resolucion DATETIME NULL,
    
    -- Claves foráneas
    CONSTRAINT FK_FactIncidente_Estudiante FOREIGN KEY (id_estudiante) REFERENCES dbo.DimEstudiante(id_estudiante),
    CONSTRAINT FK_FactIncidente_Docente FOREIGN KEY (id_docente) REFERENCES dbo.DimDocente(id_docente),
    CONSTRAINT FK_FactIncidente_Curso FOREIGN KEY (id_curso) REFERENCES dbo.DimCurso(id_curso),
    CONSTRAINT FK_FactIncidente_Facultad FOREIGN KEY (id_facultad) REFERENCES dbo.DimFacultad(id_facultad),
    CONSTRAINT FK_FactIncidente_TipoFraude FOREIGN KEY (id_tipo_fraude) REFERENCES dbo.DimTipoFraude(id_tipo_fraude),
    CONSTRAINT FK_FactIncidente_Tiempo FOREIGN KEY (id_tiempo) REFERENCES dbo.DimTiempo(id_tiempo),
    CONSTRAINT FK_FactIncidente_Sede FOREIGN KEY (id_sede) REFERENCES dbo.DimSede(id_sede),
    CONSTRAINT FK_FactIncidente_TipoPrueba FOREIGN KEY (id_tipo_prueba) REFERENCES dbo.DimTipoPrueba(id_tipo_prueba)
);
GO

PRINT 'Data Warehouse y dimensiones creados con éxito.';
GO
