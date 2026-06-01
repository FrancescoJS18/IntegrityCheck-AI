-- ==========================================
-- IntegrityCheck AI - Plataforma BI
-- Capa 1: Creación de Base de Datos
-- Autor: Grupo 4 - Universidad Peruana
-- Collation: Latin1_General_CI_AS
-- ==========================================

USE master;
GO

-- Validar si existe la base de datos y eliminarla si es necesario
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

PRINT 'Base de datos IntegrityCheckAI creada con éxito con Collation Latin1_General_CI_AS.';
GO
