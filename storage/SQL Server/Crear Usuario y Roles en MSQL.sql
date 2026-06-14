-- Crear el login a nivel de servidor con contraseña
CREATE LOGIN sql_pruebas 
WITH PASSWORD = 'pruebas123!';

-- Cambiar a la base de datos donde quieres darle acceso
USE AdventureWorksDW2022;

-- Crear el usuario dentro de la base de datos enlazado al login
CREATE USER sql_pruebas FOR LOGIN sql_pruebas;

-- Asignar el rol db_owner en esa base
ALTER ROLE db_owner ADD MEMBER sql_pruebas;