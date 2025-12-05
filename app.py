# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region TESTE

# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region IMPORTAÇÃO

from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region CONFIGURAÇÃO

app = Flask(__name__)
app.secret_key = 'chave-secreta-muito-segura-para-seu-projeto'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': '',
    'port': 3306
}

def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

@app.context_processor
def inject_now():
    return {'now': datetime.now}

def setup_database():
    # try:
        # ===============================
        # 1. Conectar ao MySQL sem banco
        # ===============================
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SHOW DATABASES LIKE 'sistema_herois'")
        if cursor.fetchone():
            cursor.close()
            conn.close()
            db_config['database'] = 'sistema_herois'
            return

        print("\n→ Criando banco de dados...")
        cursor.execute("DROP DATABASE IF EXISTS sistema_herois;")
        cursor.execute("CREATE DATABASE sistema_herois;")
        cursor.execute("USE sistema_herois;")
        
        db_config['database'] = 'sistema_herois'

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
            ("Time Sigma Líder", "sigma@sistema.com", generate_password_hash("sigma123"), "TIME"),
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

        cursor.execute("SELECT id_usuario FROM usuarios WHERE email='sigma@sistema.com';")
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
            ('Valorian', classe_id("Guerreiro"), 'https://ik.imagekit.io/x2dirkim6/images/avatars/characters/character_avatar_L7L_3ytXr.webp?tr=w-3840',
             'Golpe Flamejante, Lâmina Sagrada', 18, 14, 12, sigma, 'A', 1),

            ('Elyndra', classe_id("Mago"), 'https://i.pinimg.com/originals/3d/64/88/3d6488707233cced488505a7304e5a20.jpg',
             'Explosão Arcana, Teleporte', 12, 10, 14, sigma, 'S', 2),

            ('Ravenlock', classe_id("Assassino"), 'https://i0.wp.com/standsinthefire.com/wp-content/uploads/2015/06/rogue_by_sabin_boykinov-d486zda.jpg?resize=1400%2C1200&ssl=1',
             'Passo Sombrio, Golpe Crítico', 16, 8, 18, sigma, 'A', 3),

            # Omega Force
            ('Brutalus', classe_id("Tanque"), 'https://thumbs.dreamstime.com/b/old-viking-two-handed-hammer-rock-barbarian-steel-leather-armor-two-handed-war-hammer-old-viking-186295761.jpg',
             'Muralha de Ferro, Golpe Terremoto', 20, 20, 8, omega, 'S', 1),

            ('Seraphine', classe_id("Mago"), 'https://preview.redd.it/rqbk6bgdnbn91.jpg?width=640&crop=smart&auto=webp&s=cac4dbab4d97ec43abcc56809a67b3f7c74c4f55',
             'Chama Celestial, Cura Arcana', 14, 12, 12, omega, 'A', 2),

            ('Falconis', classe_id("Arqueiro"), 'https://www.giantbomb.com/a/uploads/square_small/0/1992/2911935-aloy.jpg',
             'Flecha Perfurante, Visão de Águia', 13, 9, 17, omega, 'B', 3),

            # Phantom Unit
            ('Nightshade', classe_id("Assassino"), 'https://i.redd.it/dzsuxajtcpr61.jpg',
             'Lâmina Sombria, Invisibilidade', 15, 10, 19, phantom, 'S', 1),

            ('Thalos', classe_id("Guerreiro"), 'https://thumbs.dreamstime.com/b/character-cartoon-illustration-male-fantasy-warrior-sword-shotgun-design-hunter-82031423.jpg',
             'Golpe Fúria, Defesa Bruta', 17, 16, 11, phantom, 'A', 2),

            ('Arcwyn', classe_id("Mago"), 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5mPBEOJrBesvpGqSrTggAmobVD7IsHhCiGA&s',
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

    # except Error as e:
    #     print("❌ Erro:", e)

# setup_database()



# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region DECORATORS

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'id_usuario' not in session or session.get('tipo_usuario') != 'ADMIN':
            flash('Acesso restrito a administradores.', 'erro')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'id_usuario' not in session:
            flash('Faça login para acessar o painel.', 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def team_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        tipo_usuario = session.get('tipo_usuario')
        id_usuario = session.get('id_usuario')
        id_time = kwargs.get('id_time')

        if tipo_usuario == 'ADMIN':
            return f(*args, **kwargs)

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario FROM times WHERE id_time = %s", (id_time,))
        dono_time = cursor.fetchone()
        cursor.close()
        conn.close()

        if not dono_time or dono_time['id_usuario'] != id_usuario:
            flash("Você não tem permissão para alterar este time.", "erro")
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

def hero_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        tipo_usuario = session.get('tipo_usuario')
        id_usuario = session.get('id_usuario')
        id_heroi = kwargs.get('id_heroi')

        if tipo_usuario == 'ADMIN':
            return f(*args, **kwargs)

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_time FROM herois WHERE id_heroi = %s", (id_heroi,))
        heroi = cursor.fetchone()

        cursor.execute("SELECT id_time FROM times WHERE id_usuario = %s", (id_usuario,))
        time_usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if not heroi or not time_usuario or heroi['id_time'] != time_usuario['id_time']:
            flash("Você não tem permissão para alterar este herói.", "erro")
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region ROTAS LISTAGEM

@app.route('/')
def index():
    return render_template('index.html')

# region HEROI

@app.route('/herois', methods=['GET'])
def listar_herois():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            h.id_heroi,
            h.nome_heroi,
            h.forca,
            h.defesa,
            h.velocidade,
            h.id_time,
            h.imagem_url,
            h.rank,
            h.posicao,
            c.nome_classe AS classe,
            t.nome_time AS time
        FROM herois h
        JOIN classes c ON h.id_classe = c.id_classe
        JOIN times t ON h.id_time = t.id_time
        ORDER BY c.nome_classe, h.rank DESC, h.posicao ASC, h.id_heroi;""")
    herois = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('herois.html', herois=herois, user=(session.get("tipo_usuario") or "USER"))

@app.route('/heroi/<int:id_heroi>', methods=['GET'])
def ver_heroi(id_heroi):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT h.*, 
               t.nome_time,
               c.nome_classe
        FROM herois h
        JOIN times t ON t.id_time = h.id_time
        JOIN classes c ON c.id_classe = h.id_classe
        WHERE h.id_heroi = %s
    """, (id_heroi,))

    heroi = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('ver_heroi.html', heroi=heroi, user=(session.get("tipo_usuario") or "USER"))


# endregion

# region TIME

@app.route('/times', methods=['GET'])
def listar_times():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            t.id_time,
            t.nome_time,
            t.descricao,
            u.nome_usuario AS dono,
            COUNT(h.id_heroi) AS total_herois
        FROM times t
        JOIN usuarios u ON t.id_usuario = u.id_usuario
        LEFT JOIN herois h ON t.id_time = h.id_time
        GROUP BY t.id_time
        ORDER BY t.nome_time;
    """)    
    times = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('times.html', times=times, user=(session.get("tipo_usuario") or "USER"))

@app.route('/time/<int:id_time>', methods=['GET'])
def ver_time(id_time):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
    time = cursor.fetchone()
    # cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (id_time,))
    cursor.execute("SELECT h.*, c.nome_classe FROM herois h JOIN classes c ON h.id_classe = c.id_classe WHERE h.id_time = %s ORDER BY h.id_heroi", (id_time,))
    herois = cursor.fetchall()
    cursor.execute("SELECT id_time FROM times WHERE id_usuario = %s", (session.get("id_usuario"),))
    c = cursor.fetchone()
    if c:
        mesmo_time = id_time == c["id_time"]
    else:
        mesmo_time = False
    cursor.close()
    conn.close()
    return render_template('ver_time.html', time=time, herois=herois, user=(session.get("tipo_usuario") or "USER"), mesmo_time=mesmo_time)

# endregion

# region CLASSE

@app.route('/classes', methods=['GET'])
def listar_classes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM classes
    """)
    classes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('classes.html', classes=classes, tipo = session.get('tipo_usuario'))

# endregion

# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region ROTAS LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['senha_hash'], senha):
            session['id_usuario'] = user['id_usuario']
            session['tipo_usuario'] = user['tipo']
            session['nome_usuario'] = user['nome_usuario']
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'erro')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario'].strip()
        email = request.form['email'].strip()
        senha = generate_password_hash(request.form['senha'])
        nome_time = request.form['nome_time'].strip()
        descricao_time = request.form['descricao_time'].strip()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Já existe um usuário com este e-mail.", "erro")
                return render_template('cadastro.html', nome_usuario=nome_usuario, nome_time=nome_time, descricao_time=descricao_time)

            cursor.execute("SELECT id_usuario FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
            if cursor.fetchone():
                flash("Já existe um usuário com este nome.", "erro")
                return render_template('cadastro.html', email=email, nome_time=nome_time, descricao_time=descricao_time)

            cursor.execute("SELECT id_time FROM times WHERE nome_time = %s", (nome_time,))
            if cursor.fetchone():
                flash("Já existe um time com este nome.", "erro")
                return render_template('cadastro.html', nome_usuario=nome_usuario, email=email, descricao_time=descricao_time)

            cursor.execute("""
                INSERT INTO usuarios (nome_usuario, email, senha_hash, tipo)
                VALUES (%s, %s, %s, 'TIME')
            """, (nome_usuario, email, senha))
            conn.commit()

            id_usuario = cursor.lastrowid

            cursor.execute("""
                INSERT INTO times (nome_time, descricao, id_usuario)
                VALUES (%s, %s, %s)
            """, (nome_time, descricao_time, id_usuario))
            conn.commit()

            flash("Time cadastrado com sucesso! Faça login.", "sucesso")
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print("Erro ao cadastrar:", err)
            flash("Erro inesperado ao cadastrar. Tente novamente.", "erro")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('cadastro.html')

@app.route('/admin/cadastro', methods=['GET', 'POST'])
@admin_required
def cadastro_admin():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario'].strip()
        email = request.form['email'].strip()
        senha = generate_password_hash(request.form['senha'])

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Já existe um usuário com esse email.", "erro")
                return render_template('cadastro_admin.html', nome_usuario=nome_usuario)
            
            cursor.execute("SELECT id_usuario FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
            if cursor.fetchone():
                flash("Já existe um usuário com este nome.", "erro")
                return render_template('cadastro_admin.html', email=email)

            cursor.execute("""
                INSERT INTO usuarios (nome_usuario, email, senha_hash, tipo)
                VALUES (%s, %s, %s, 'ADMIN')
            """, (nome_usuario, email, senha))
            conn.commit()

            flash("Administrador criado com sucesso!", "sucesso")
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print("Erro ao criar administrador:", err)
            conn.rollback()
            flash("Erro ao criar administrador.", "erro")
        finally:
            cursor.close()
            conn.close()

    return render_template('cadastro_admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('index'))

# endregion
# ._____ ____._______
#(  .       (
# '-'        '



# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region ROTAS CRUD

# region HEROI

@app.route('/heroi/novo', methods=['GET', 'POST'])
@login_required
def adicionar_heroi():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_classe, nome_classe FROM classes ORDER BY nome_classe")
    classes = cursor.fetchall()

    tipo_usuario = session.get('tipo_usuario')
    
    times = []
    if tipo_usuario == 'ADMIN':
        cursor.execute("SELECT id_time, nome_time FROM times ORDER BY nome_time")
        times = cursor.fetchall()

    form = {}
    
    if request.method == 'POST':
        form['nome_heroi'] = request.form['nome_heroi'].strip()
        form['id_classe'] = request.form['id_classe']
        form['imagem_url'] = request.form['imagem_url'].strip()
        form['habilidades'] = request.form['habilidades'].strip()
        form['forca'] = request.form['forca']
        form['defesa'] = request.form['defesa']
        form['velocidade'] = request.form['velocidade']

        if tipo_usuario == 'ADMIN':
            form['id_time'] = request.form['id_time']
        else:
            cursor.execute("SELECT id_time FROM times WHERE id_usuario = %s", (session.get("id_usuario"),))
            form['id_time'] = cursor.fetchone()["id_time"]

        cursor.execute("SELECT id_heroi FROM herois WHERE nome_heroi = %s", (form['nome_heroi'],))
        if cursor.fetchone():
            flash("Já existe um herói com esse nome!", "warning")
        else:
            cursor.execute("""SELECT MAX(posicao) AS ultima_pos
                FROM herois
                WHERE rank = 'D'""")
            ultima_pos = cursor.fetchone()['ultima_pos'] or 0
            nova_posicao = ultima_pos + 1

            cursor.execute("""
                INSERT INTO herois
                (nome_heroi, id_classe, imagem_url, habilidades, forca, defesa, velocidade, id_time, posicao)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (form['nome_heroi'], form['id_classe'], form['imagem_url'], form['habilidades'], form['forca'], form['defesa'], form['velocidade'], form['id_time'], nova_posicao)
            )
            conn.commit()

            novo_id = cursor.lastrowid

            cursor.close()
            conn.close()
            flash("Herói adicionado com sucesso!", "sucesso")
            return redirect(url_for('ver_heroi', id_heroi=novo_id))

    cursor.close()
    conn.close()
    return render_template('adicionar_heroi.html', form=form, classes=classes, times=times, admin=tipo_usuario=="ADMIN")

@app.route('/heroi/<int:id_heroi>/editar', methods=['GET', 'POST'])
@hero_required
def editar_heroi(id_heroi): ###### NÃO EXISTE ID_TIME NO SESSION
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT h.*, t.nome_time
        FROM herois h
        JOIN times t ON t.id_time = h.id_time
        WHERE h.id_heroi = %s
    """, (id_heroi,))
    heroi_original = cursor.fetchone()

    if not heroi_original:
        cursor.close()
        conn.close()
        flash("Herói não encontrado.", "erro")
        return redirect(url_for('index'))

    cursor.execute("SELECT id_classe, nome_classe FROM classes ORDER BY nome_classe")
    classes = cursor.fetchall()

    tipo_usuario = session.get('tipo_usuario')

    times = []
    if tipo_usuario == 'ADMIN':
        cursor.execute("SELECT id_time, nome_time FROM times ORDER BY nome_time")
        times = cursor.fetchall()

    # form começa com os valores originais
    form = dict(heroi_original)

    cursor.execute("SELECT id_time FROM times WHERE id_usuario = %s", (session.get("id_usuario"),))
    id_time = cursor.fetchone()["id_time"]

    if request.method == 'POST':
        form['nome_heroi'] = request.form.get('nome_heroi', '').strip()
        form['id_classe'] = request.form.get('id_classe')
        form['imagem_url'] = request.form.get('imagem_url', '').strip()
        form['habilidades'] = request.form.get('habilidades', '').strip()
        form['forca'] = request.form.get('forca')
        form['defesa'] = request.form.get('defesa')
        form['velocidade'] = request.form.get('velocidade')

        if tipo_usuario == 'ADMIN':
            form['id_time'] = request.form['id_time']
            form['rank'] = request.form.get('rank', 'D')
        else:
            form['id_time'] = id_time
            form['rank'] = heroi_original['rank']

        cursor.execute("""
            SELECT id_heroi FROM herois 
            WHERE nome_heroi = %s AND id_heroi <> %s
        """, (form['nome_heroi'], id_heroi))

        if cursor.fetchone():
            flash("Já existe um herói com esse nome!", "warning")
        else:
            cursor.execute("""
                UPDATE herois
                SET nome_heroi=%s, id_classe=%s, imagem_url=%s, habilidades=%s,
                    forca=%s, defesa=%s, velocidade=%s, id_time=%s, rank=%s
                WHERE id_heroi = %s
            """, 
                (form['nome_heroi'], form['id_classe'], form['imagem_url'],
                 form['habilidades'], form['forca'], form['defesa'],
                 form['velocidade'], form['id_time'], form['rank'], id_heroi)
            )

            conn.commit()
            cursor.close()
            conn.close()
            flash("Herói editado com sucesso!", "sucesso")
            return redirect(url_for('ver_heroi', id_heroi=id_heroi))

    cursor.close()
    conn.close()
    return render_template('editar_heroi.html', form=form, classes=classes, times=times, admin=tipo_usuario=="ADMIN", id_time=id_time)

@app.route('/heroi/<int:id_heroi>/excluir', methods=['GET', 'POST'])
@hero_required
def excluir_heroi(id_heroi):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT h.*, t.nome_time
        FROM herois h
        JOIN times t ON t.id_time = h.id_time
        WHERE h.id_heroi = %s
    """, (id_heroi,))
    heroi = cursor.fetchone()

    if not heroi:
        cursor.close()
        conn.close()
        flash("Herói não encontrado.", "erro")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        cursor.execute('DELETE FROM herois WHERE id_heroi = %s', (id_heroi,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Herói excluído com sucesso!", "sucesso")
        return redirect(url_for('ver_time', id_time=heroi['id_time']))
    
    cursor.close()
    conn.close()
    return render_template('excluir_heroi', id_heroi=id_heroi)

# endregion

# region TIME

@app.route('/time/<int:id_time>/editar', methods=['GET', 'POST'])
@team_required
def editar_time(id_time):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
    time_original = cursor.fetchone()

    if not time_original:
        cursor.close()
        conn.close()
        flash("Time não encontrado.", "erro")
        return redirect(url_for('index'))

    tipo_usuario = session.get('tipo_usuario')

    form = dict(time_original)

    if request.method == 'POST':
        form['nome_time'] = request.form.get('nome_time', '').strip()
        form['descricao'] = request.form.get('descricao', '').strip()

        cursor.execute("""
            SELECT id_time FROM times WHERE nome_time = %s AND id_time <> %s""",
            (form['nome_time'], id_time)
        )
        if cursor.fetchone():
            flash("Já existe um time com esse nome!", "warning")
        else:
            cursor.execute("""
                UPDATE times
                SET nome_time = %s, descricao = %s
                WHERE id_time = %s
            """, (form['nome_time'], form['descricao'], id_time))

            conn.commit()
            cursor.close()
            conn.close()
            flash("Time com sucesso!", "sucesso")
            return redirect(url_for('ver_time', id_time=id_time))

    cursor.close()
    conn.close()
    return render_template('editar_time.html', form=form, admin=tipo_usuario=="ADMIN")

@app.route('/time/<int:id_time>/excluir', methods=['POST'])
@team_required
def excluir_time(id_time):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
    time = cursor.fetchone()

    if not time:
        flash("Time não encontrado.", "erro")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        cursor.execute("DELETE FROM times WHERE id_time = %s", (id_time,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Time excluído com sucesso!", "sucesso")
        return redirect(url_for('index'))

    cursor.close()
    conn.close()

# endregion

# region USUÁRIO

@app.route('/usuario/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    id_usuario = session.get('id_usuario')

    cursor.execute("""
        SELECT *
        FROM usuarios
        WHERE id_usuario = %s
    """, (id_usuario,))
    usuario_original = cursor.fetchone()

    if not usuario_original:
        cursor.close()
        conn.close()
        flash("Usuário não encotrado.", "erro")
        return redirect(url_for('index'))
    
    form = dict(usuario_original)

    if request.method == 'POST':
        form['nome_usuario'] = request.form.get('nome_usuario').strip()
        form['email'] = request.form.get('email').strip()

        cursor.execute("""SELECT id_usuario FROM usuarios WHERE email = %s AND id_usuario != %s""", (form['email'], id_usuario))      
        if cursor.fetchone():
            flash("Já existe um usuário com este e-mail.", "erro")
        else:
            cursor.execute("""SELECT id_usuario FROM usuarios WHERE nome_usuario = %s AND id_usuario != %s""", (form['nome_usuario'], id_usuario))
            if cursor.fetchone():
               flash("Já existe um usuário com este nome.", "erro")
            else:
                cursor.execute("""
                    UPDATE usuarios
                    SET nome_usuario = %s, email = %s
                    WHERE id_usuario = %s
                """, (form['nome_usuario'], form['email'], id_usuario))

                conn.commit()
                cursor.close()
                conn.close()
                session['nome_usuario'] = form['nome_usuario']
                return redirect(url_for('index'))
                    
    cursor.close()
    conn.close()
    return render_template('editar_usuario.html', form=form)

@app.route('/usuario/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    id_usuario = session.get('id_usuario')

    cursor.execute("""
        SELECT senha_hash
        FROM usuarios
        WHERE id_usuario = %s
    """, (id_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conn.close()
        flash("Usuário não encotrado.", "erro")
        return redirect(url_for('index'))
    
    form = dict(usuario)

    if request.method == 'POST':
        form['senha'] = request.form.get('senha').strip()
        form['confirmar'] = request.form.get('confirmar').strip()

        if form['senha'] != form['confirmar']:
            flash("Senha e confirmação são diferentes", "erro")
        elif check_password_hash(usuario['senha_hash'], form['senha']):
            flash("Senha igual a anterior!", "erro")
        else:
            cursor.execute("""
                UPDATE usuarios
                SET senha_hash = %s
                WHERE id_usuario = %s
            """, (generate_password_hash(form['senha']), id_usuario))

            conn.commit()
            cursor.close()
            conn.close()
            flash("Senha alterada com sucesso!", "sucesso")
            return redirect(url_for('index'))
    
    cursor.close()
    conn.close()
    return render_template('editar_usuario.html', form=form)

@app.route('/usuario/excluir', methods=['POST'])
@login_required
def excluir_usuario():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    id_usuario = session.get('id_usuario')

    cursor.execute('DELETE FROM usuarios WHERE id_usuario = %s', (id_usuario,))
    conn.commit()

    cursor.close()
    conn.close()

    session.clear()
    flash("Usuário excluído com sucesso!", "sucesso")
    return redirect(url_for('index'))

# endregion

# region CLASSE

@app.route('/classe/novo', methods=['GET', 'POST'])
@admin_required
def adicionar_classe():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    form = {'nome_classe': '', 'descricao': ''}

    if request.method == "POST":
        form['nome_classe'] = request.form['nome_classe'].strip()
        form['descricao'] = request.form['descricao'].strip()

        cursor.execute("SELECT id_classe FROM classes WHERE nome_classe = %s", (form['nome_classe'],))
        if cursor.fetchone():
            flash("Já existe uma classe com esse nome!", "warning")
        else:
            cursor.execute("""
                INSERT INTO classes (nome_classe, descricao)
                VALUES (%s, %s)
            """, (form['nome_classe'], form['descricao']))
            conn.commit()

            cursor.close()
            conn.close()
            flash("Classe adicionada com sucesso!", "sucesso")
            return redirect(url_for('listar_classes'))

    cursor.close()
    conn.close()
    return render_template('adicionar_classe.html', form=form)

@app.route('/classe/<int:id_classe>/editar', methods=['GET', 'POST'])
@admin_required
def editar_classe(id_classe):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM classes WHERE id_classe = %s", (id_classe,))
    classe_original = cursor.fetchone()

    if not classe_original:
        cursor.close()
        conn.close()
        flash("Classe não encontrada.", "erro")
        return redirect(url_for('listar_classes'))

    form = dict(classe_original)

    if request.method == "POST":
        form['nome_classe'] = request.form.get('nome_classe', '').strip()
        form['descricao'] = request.form.get('descricao', '').strip()

        # Validar duplicado
        cursor.execute("""
            SELECT id_classe FROM classes
            WHERE nome_classe = %s AND id_classe <> %s
        """, (form['nome_classe'], id_classe))
        
        if cursor.fetchone():
            flash("Já existe uma classe com esse nome!", "warning")
        else:
            cursor.execute("""
                UPDATE classes
                SET nome_classe = %s, descricao = %s
                WHERE id_classe = %s
            """, (form['nome_classe'], form['descricao'], id_classe))
            
            conn.commit()
            cursor.close()
            conn.close()
            flash("Classe atualizada com sucesso!", "sucesso")
            return redirect(url_for('listar_classes'))

    cursor.close()
    conn.close()
    return render_template('editar_classe.html', form=form)

@app.route('/classe/<int:id_classe>/excluir', methods=['POST'])
@admin_required
def excluir_classe(id_classe):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar se a classe existe
        cursor.execute("SELECT * FROM classes WHERE id_classe = %s", (id_classe,))
        classe = cursor.fetchone()

        if not classe:
            flash("Classe não encontrada.", "erro")
            cursor.close()
            conn.close()
            return redirect(url_for('listar_classes'))

        # Excluir classe
        cursor.execute("DELETE FROM classes WHERE id_classe = %s", (id_classe,))
        conn.commit()

        flash("Classe excluída com sucesso!", "sucesso")

    except mysql.connector.Error as err:
        print("Erro ao excluir classe:", err)
        flash("Erro inesperado ao excluir a classe.", "erro")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('listar_classes'))


# endregion

# endregion
# ._____ ____._______
#(  .       (
# '-'        '

# \.
# .'¨¨¨'.
#/  __   \    `;
# .' .'  /,   ,¨'-
#/'.___.'__'__'._____('________ ____
#
# region EXECUÇÃO

if __name__ == '__main__':
    setup_database() 
    app.run(debug=True)
    

# endregion
# ._____ ____._______
#(  .       (
# '-'        '


