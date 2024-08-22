-- Eliminar la base de datos si ya existe
DROP DATABASE IF EXISTS textDataEntryForm;

-- Crear la base de datos
CREATE DATABASE textDataEntryForm;

-- Usar la base de datos recién creada
USE textDataEntryForm;

-- Eliminar la tabla personal_data si ya existe
DROP TABLE IF EXISTS personal_data;

-- Crear la tabla personal_data
CREATE TABLE personal_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
