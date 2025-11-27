import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

def setup_database():
    try:
        # ===============================
        # 1. Conectar ao MySQL sem banco
        # ===============================
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""     # senha padrão do XAMPP
        )
        cursor = conn.cursor()

        print("\n→ Criando banco de dados...")
        cursor.execute("DROP DATABASE IF EXISTS sistema_herois;")
        cursor.execute("CREATE DATABASE sistema_herois;")
        cursor.execute("USE sistema_herois;")

        # ===============================
        # 2. Criação das tabelas
        # ===============================
        print("→ Criando tabelas...")

        cursor.execute("""
        CREATE TABLE usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nome_usuario VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            tipo ENUM('ADMIN', 'TIME') NOT NULL DEFAULT 'TIME',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE times (
            id_time INT AUTO_INCREMENT PRIMARY KEY,
            nome_time VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT,
            id_usuario INT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE classes (
            id_classe INT AUTO_INCREMENT PRIMARY KEY,
            nome_classe VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT
        );
        """)

        cursor.execute("""
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
        """)

        # ===============================
        # 3. Inserção dos usuários
        # ===============================
        print("→ Inserindo usuários...")

        usuarios = [
            ("Admin Master", "admin@sistema.com", generate_password_hash("admin123"), "ADMIN"),
            ("Time Sigma Líder", "alpha@sistema.com", generate_password_hash("alpha123"), "TIME"),
            ("Time Omega Líder", "omega@sistema.com", generate_password_hash("omega123"), "TIME"),
            ("Time Phantom Líder", "phantom@sistema.com", generate_password_hash("phantom123"), "TIME")
        ]

        cursor.executemany("""
            INSERT INTO usuarios (nome_usuario, email, senha_hash, tipo)
            VALUES (%s, %s, %s, %s)
        """, usuarios)

        # ===============================
        # 4. Inserção dos times
        # ===============================
        print("→ Inserindo times...")

        cursor.execute("SELECT id_usuario FROM usuarios WHERE email='alpha@sistema.com';")
        sigma_user = cursor.fetchone()[0]

        cursor.execute("SELECT id_usuario FROM usuarios WHERE email='omega@sistema.com';")
        omega_user = cursor.fetchone()[0]

        cursor.execute("SELECT id_usuario FROM usuarios WHERE email='phantom@sistema.com';")
        phantom_user = cursor.fetchone()[0]

        times = [
            ("Sigma Squad", "Time focado em operações de elite", sigma_user),
            ("Omega Force", "Especialistas em combate de larga escala", omega_user),
            ("Phantom Unit", "Equipe furtiva voltada para infiltração", phantom_user)
        ]

        cursor.executemany("""
            INSERT INTO times (nome_time, descricao, id_usuario)
            VALUES (%s, %s, %s)
        """, times)

        # ===============================
        # 5. Inserção das classes
        # ===============================
        print("→ Inserindo classes...")

        classes = [
            ("Guerreiro", "Especialista em combate corpo a corpo"),
            ("Arqueiro", "Ataques à distância com alta precisão"),
            ("Mago", "Usuário de magia arcana poderosa"),
            ("Tanque", "Alta resistência e defesa"),
            ("Assassino", "Alta velocidade e dano crítico"),
            ("Esotérico", "Criatura mutante ou mista com humanos")
        ]

        cursor.executemany("""
            INSERT INTO classes (nome_classe, descricao)
            VALUES (%s, %s)
        """, classes)

        # ===============================
        # 6. Inserção dos heróis
        # ===============================
        print("→ Inserindo heróis...")

        cursor.execute("SELECT id_time FROM times WHERE nome_time='Sigma Squad'")
        sigma = cursor.fetchone()[0]

        cursor.execute("SELECT id_time FROM times WHERE nome_time='Omega Force'")
        omega = cursor.fetchone()[0]

        cursor.execute("SELECT id_time FROM times WHERE nome_time='Phantom Unit'")
        phantom = cursor.fetchone()[0]

        # pegar classes
        def classe_id(nome):
            cursor.execute("SELECT id_classe FROM classes WHERE nome_classe=%s", (nome,))
            return cursor.fetchone()[0]

        herois = [
            # Sigma Squad
            ('Valorian', classe_id("Guerreiro"), 'https://imagens-herois.com/valorian.png',
             'Golpe Flamejante, Lâmina Sagrada', 18, 14, 12, sigma, 'A', 1),

            ('Elyndra', classe_id("Mago"), 'https://imagens-herois.com/elyndra.png',
             'Explosão Arcana, Teleporte', 12, 10, 14, sigma, 'S', 2),

            ('Ravenlock', classe_id("Assassino"), 'https://imagens-herois.com/ravenlock.png',
             'Passo Sombrio, Golpe Crítico', 16, 8, 18, sigma, 'A', 3),

            # Omega Force
            ('Brutalus', classe_id("Tanque"), 'https://imagens-herois.com/brutalus.png',
             'Muralha de Ferro, Golpe Terremoto', 20, 20, 8, omega, 'S', 1),

            ('Seraphine', classe_id("Mago"), 'https://imagens-herois.com/seraphine.png',
             'Chama Celestial, Cura Arcana', 14, 12, 12, omega, 'A', 2),

            ('Falconis', classe_id("Arqueiro"), 'https://imagens-herois.com/falconis.png',
             'Flecha Perfurante, Visão de Águia', 13, 9, 17, omega, 'B', 3),

            # Phantom Unit
            ('Nightshade', classe_id("Assassino"), 'https://imagens-herois.com/nightshade.png',
             'Lâmina Sombria, Invisibilidade', 15, 10, 19, phantom, 'S', 1),

            ('Thalos', classe_id("Guerreiro"), 'https://imagens-herois.com/thalos.png',
             'Golpe Fúria, Defesa Bruta', 17, 16, 11, phantom, 'A', 2),

            ('Arcwyn', classe_id("Mago"), 'https://imagens-herois.com/arcwyn.png',
             'Raios Arcanos, Barreira Mística', 14, 13, 14, phantom, 'A', 3),
        ]

        cursor.executemany("""
            INSERT INTO herois
            (nome_heroi, id_classe, imagem_url, habilidades, forca, defesa, velocidade, id_time, rank, posicao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, herois)


        # ===============================
        # FINALIZAR
        # ===============================
        conn.commit()
        cursor.close()
        conn.close()

        print("\n✔ Banco criado e populado com sucesso!")

    except Error as e:
        print("❌ Erro:", e)


if __name__ == "__main__":
    setup_database()