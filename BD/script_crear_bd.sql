-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 1: Creación de Base de Datos y Esquemas
-- Autor: Grupo 4 - Universidad Peruana
-- Collation: Latin1_General_CI_AS
-- ==========================================

USE master;
GO

-- Eliminar BD si ya existe (para reinstalación limpia)
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'IntegrityCheckAI')
BEGIN
    ALTER DATABASE IntegrityCheckAI SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE IntegrityCheckAI;
END
GO

-- Crear la base de datos con la collation solicitada
CREATE DATABASE IntegrityCheckAI
COLLATE Latin1_General_CI_AS;
GO

USE IntegrityCheckAI;
GO

-- ==========================================
-- CONFIGURACIÓN DE ESQUEMAS
-- ==========================================

-- El esquema dbo ya existe por defecto en SQL Server
-- Confirmamos que está activo
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dbo')
BEGIN
    EXEC('CREATE SCHEMA dbo');
END
GO

-- ==========================================
-- CONFIGURACIÓN GENERAL DE LA BASE DE DATOS
-- ==========================================

-- Habilitar snapshot isolation para lecturas concurrentes
ALTER DATABASE IntegrityCheckAI
SET READ_COMMITTED_SNAPSHOT ON;
GO

-- Habilitar ALLOW_SNAPSHOT_ISOLATION para transacciones largas
ALTER DATABASE IntegrityCheckAI
SET ALLOW_SNAPSHOT_ISOLATION ON;
GO

-- Configurar recovery model
ALTER DATABASE IntegrityCheckAI
SET RECOVERY SIMPLE;
GO

-- ==========================================
-- ROLES DE APLICACIÓN (para seguridad RLS)
-- ==========================================

-- Crear logins de aplicación si no existen
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'app_integrity_user')
BEGIN
    CREATE USER app_integrity_user WITHOUT LOGIN;
END
GO

-- ==========================================
-- PERMISOS BASE
-- ==========================================
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO app_integrity_user;
GO

PRINT '================================================';
PRINT ' Base de datos IntegrityCheckAI creada con exito';
PRINT ' Collation : Latin1_General_CI_AS';
PRINT ' Esquema   : dbo configurado';
PRINT ' Isolation : READ_COMMITTED_SNAPSHOT ON';
PRINT ' Siguiente : Ejecutar script_tablas_staging.sql';
PRINT '================================================';
GO