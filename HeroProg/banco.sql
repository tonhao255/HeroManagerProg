--#}>===-------===<:/%@@%/:>===-------===<{#--
--#|             CRIAÇÃO DO DB            |#--
--#}>===-------===<:/%@@%/:>===-------===<{#--
CREATE DATABASE sistema_herois;
USE sistema_herois;

--#}>===-------===<:/%@@%/:>===-------===<{#--
--#|       USUÁRIOS (ADMINS E TIMES)      |#--
--#}>===-------===<:/%@@%/:>===-------===<{#--
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo ENUM('ADMIN', 'TIME') NOT NULL DEFAULT 'TIME',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--#}>===-------===<:/%@@%/:>===-------===<{#--
--#|                 TIMES                |#--
--#}>===-------===<:/%@@%/:>===-------===<{#--
CREATE TABLE times (
    id_time INT AUTO_INCREMENT PRIMARY KEY,
    nome_time VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    id_usuario INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
);

--#}>===-------===<:/%@@%/:>===-------===<{#--
--#|           CLASSES DE HERÓIS          |#--
--#}>===-------===<:/%@@%/:>===-------===<{#--
CREATE TABLE classes (
    id_classe INT AUTO_INCREMENT PRIMARY KEY,
    nome_classe VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT
);

--#}>===-------===<:/%@@%/:>===-------===<{#--
--#|                HERÓIS                |#--
--#}>===-------===<:/%@@%/:>===-------===<{#--
CREATE TABLE herois (
    id_heroi INT AUTO_INCREMENT PRIMARY KEY,
    nome_heroi VARCHAR(100) NOT NULL,
    id_classe INT NOT NULL,
    imagem_url VARCHAR(255),
    habilidades TEXT,
    forca INT NOT NULL DEFAULT 10,
    defesa INT NOT NULL DEFAULT 10,
    velocidade INT NOT NULL DEFAULT 10,
    id_time INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    classe_ranking ENUM('S', 'A', 'B', 'C', 'D') DEFAULT 'C',
    posicao_ranking INT DEFAULT NULL,
    
    FOREIGN KEY (id_classe) REFERENCES classes(id_classe)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_time) REFERENCES times(id_time)
        ON DELETE CASCADE
);