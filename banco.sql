--}>===-------===<:/%@@%/:>===-------===<{--
--|             CRIAÇÃO DO DB            |--
--}>===-------===<:/%@@%/:>===-------===<{--
CREATE DATABASE sistema_herois;
USE sistema_herois;

--}>===-------===<:/%@@%/:>===-------===<{--
--|       USUÁRIOS (ADMINS E TIMES)      |--
--}>===-------===<:/%@@%/:>===-------===<{--
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo ENUM('ADMIN', 'TIME') NOT NULL DEFAULT 'TIME',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--}>===-------===<:/%@@%/:>===-------===<{--
--|                 TIMES                |--
--}>===-------===<:/%@@%/:>===-------===<{--
CREATE TABLE times (
    id_time INT AUTO_INCREMENT PRIMARY KEY,
    nome_time VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    id_usuario INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
);

--}>===-------===<:/%@@%/:>===-------===<{--
--|           CLASSES DE HERÓIS          |--
--}>===-------===<:/%@@%/:>===-------===<{--
CREATE TABLE classes (
    id_classe INT AUTO_INCREMENT PRIMARY KEY,
    nome_classe VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT
);

--}>===-------===<:/%@@%/:>===-------===<{--
--|                HERÓIS                |--
--}>===-------===<:/%@@%/:>===-------===<{--
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
    rank ENUM('S', 'A', 'B', 'C', 'D') DEFAULT 'D',
    posicao INT DEFAULT NULL,
    
    FOREIGN KEY (id_classe) REFERENCES classes(id_classe)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_time) REFERENCES times(id_time)
        ON DELETE CASCADE
);

USE sistema_herois;

-- ============================================================
-- USUÁRIOS
-- ============================================================
INSERT INTO usuarios (nome_usuario, email, senha_hash, tipo) VALUES
('Admin Master', 'admin@sistema.com', 'hash_admin_123', 'ADMIN'),
('Time Alpha Líder', 'alpha@sistema.com', 'hash_alpha_123', 'TIME'),
('Time Omega Líder', 'omega@sistema.com', 'hash_omega_123', 'TIME'),
('Time Phantom Líder', 'phantom@sistema.com', 'hash_phantom_123', 'TIME');


-- ============================================================
-- TIMES
-- ============================================================
INSERT INTO times (nome_time, descricao, id_usuario) VALUES
('Alpha Squad', 'Time focado em operações de elite', 2),
('Omega Force', 'Especialistas em combate de larga escala', 3),
('Phantom Unit', 'Equipe furtiva voltada para infiltração', 4);


-- ============================================================
-- CLASSES DE HERÓIS
-- ============================================================
INSERT INTO classes (nome_classe, descricao) VALUES
('Guerreiro', 'Especialista em combate corpo a corpo'),
('Arqueiro', 'Ataques à distância com alta precisão'),
('Mago', 'Usuário de magia arcana poderosa'),
('Tanque', 'Alta resistência e defesa'),
('Assassino', 'Alta velocidade e dano crítico');


-- ============================================================
-- HERÓIS
-- ============================================================
INSERT INTO herois 
(nome_heroi, id_classe, imagem_url, habilidades, forca, defesa, velocidade, id_time, rank, posicao)
VALUES
-- Alpha Squad
('Valorian', 1, 'https://imagens-herois.com/valorian.png',
 'Golpe Flamejante, Lâmina Sagrada', 18, 14, 12, 1, 'A', 1),

('Elyndra', 3, 'https://imagens-herois.com/elyndra.png',
 'Explosão Arcana, Teleporte', 12, 10, 14, 1, 'S', 2),

('Ravenlock', 5, 'https://imagens-herois.com/ravenlock.png',
 'Passo Sombrio, Golpe Crítico', 16, 8, 18, 1, 'A', 3),

-- Omega Force
('Brutalus', 4, 'https://imagens-herois.com/brutalus.png',
 'Muralha de Ferro, Golpe Terremoto', 20, 20, 8, 2, 'S', 1),

('Seraphine', 3, 'https://imagens-herois.com/seraphine.png',
 'Chama Celestial, Cura Arcana', 14, 12, 12, 2, 'A', 2),

('Falconis', 2, 'https://imagens-herois.com/falconis.png',
 'Flecha Perfurante, Visão de Águia', 13, 9, 17, 2, 'B', 3),

-- Phantom Unit
('Nightshade', 5, 'https://imagens-herois.com/nightshade.png',
 'Lâmina Sombria, Invisibilidade', 15, 10, 19, 3, 'S', 1),

('Thalos', 1, 'https://imagens-herois.com/thalos.png',
 'Golpe Fúria, Defesa Bruta', 17, 16, 11, 3, 'A', 2),

('Arcwyn', 3, 'https://imagens-herois.com/arcwyn.png',
 'Raios Arcanos, Barreira Mística', 14, 13, 14, 3, 'A', 3);
