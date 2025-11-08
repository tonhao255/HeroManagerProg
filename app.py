#\._
#)%#}>--==<:/%@@%/:>===-------===<{#
# region IMPORTAÇÃO

from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

# endregion
#)%#}>--==<:/%@@%/:>===-------===<{#
#\._

#}>===-------===<:/%@@%/:>===-------===<{#
#|             CONFIGURAÇÃO             |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

app = Flask(__name__)
app.secret_key = 'chave-secreta-muito-segura-para-seu-projeto'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sistema_herois'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# endregion



#}>===-------===<:/%@@%/:>===-------===<{#
#|              DECORATORS              |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

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



#}>===-------===<:/%@@%/:>===-------===<{#
#|            ROTAS LISTAGEM            |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

@app.route('/')
def index():
    return render_template('index.html')

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
    return render_template('herois.html', herois)

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

    return render_template('times.html', times)

@app.route('/heroi/<int:id_heroi>', methods=['GET'])
def ver_heroi(id_heroi):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.*, t.nome_time
        FROM herois h
        JOIN times t ON t.id_time = h.id_time
        WHERE h.id_heroi = %s
    """, (id_heroi,))
    heroi = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('ver_heroi.html', heroi=heroi)

@app.route('/time/<int:id_time>', methods=['GET'])
def ver_time(id_time):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
    time = cursor.fetchone()
    cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (id_time,))
    herois = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('ver_time.html', time=time, herois=herois)

# endregion



#}>===-------===<:/%@@%/:>===-------===<{#
#|              ROTAS LOGIN             |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

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

#endregion



#}>===-------===<:/%@@%/:>===-------===<{#
#|              ROTAS CRUD              |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

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
            form['id_time'] = session.get('id_time')

        cursor.execute("SELECT id_heroi FROM herois WHERE nome_heroi = %s", (form['nome_heroi'],))
        if cursor.fetchone():
            flash("Já existe um herói com esse nome!", "warning")
        else:
            cursor.execute("""SELECT MAX(posicao_ranking) AS ultima_pos
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
            return redirect(url_for('ver_heroi', id_heroi=novo_id))

    cursor.close()
    conn.close()
    return render_template('adicionar_heroi.html', form=form, classes=classes, times=times)

@app.route('/heroi/<int:id_heroi>/editar', methods=['GET', 'POST'])
@hero_required
def editar_heroi(id_heroi):
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

    form = dict(heroi_original)

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
            form['id_time'] = session.get('id_time')

        cursor.execute("""
            SELECT id_heroi FROM herois WHERE nome_heroi = %s AND id_heroi <> %s""",
            (form['nome_heroi'], id_heroi)
        )
        if cursor.fetchone():
            flash("Já existe um herói com esse nome!", "warning")
        else:
            cursor.execute("""
                UPDATE herois
                SET nome_heroi=%s, id_classe=%s, imagem_url=%s, habilidades=%s, forca=%s, defesa=%s, velocidade=%s, id_time=%s, rank=%s
                WHERE id_heroi = %s""", 
                (form['nome_heroi'], form['id_classe'], form['imagem_url'], form['habilidades'], form['forca'], form['defesa'], form['velocidade'], form['id_time'], form['classe_ranking'], id_heroi)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('ver_heroi', id_heroi=id_heroi))

    cursor.close()
    conn.close()
    return render_template('editar_heroi.html', form=form, classes=classes, times=times)

#endregion



# region Comentado
# # ==============================================================
# # LOGIN / CADASTRO / LOGOUT
# # ==============================================================

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         senha = request.form['senha']

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if user and check_password_hash(user['senha_hash'], senha):
#             session['id_usuario'] = user['id_usuario']
#             session['tipo_usuario'] = user['tipo']
#             session['nome_usuario'] = user['nome_usuario']
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Email ou senha incorretos.', 'erro')

#     return render_template('login.html')

# @app.route('/cadastro', methods=['GET', 'POST'])
# def cadastro():
#     if request.method == 'POST':
#         nome = request.form['nome']
#         email = request.form['email']
#         senha = generate_password_hash(request.form['senha'])
#         tipo = request.form.get('tipo', 'TIME')

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO usuarios (nome_usuario, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
#                        (nome, email, senha, tipo))
#         conn.commit()

#         if tipo == 'TIME':
#             cursor.execute("SELECT LAST_INSERT_ID()")
#             user_id = cursor.fetchone()[0]
#             cursor.execute("INSERT INTO times (nome_time, id_usuario) VALUES (%s, %s)", (f"Time de {nome}", user_id))
#             conn.commit()

#         cursor.close()
#         conn.close()
#         flash('Conta criada com sucesso!', 'sucesso')
#         return redirect(url_for('login'))

#     return render_template('cadastro.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Sessão encerrada.', 'info')
#     return redirect(url_for('index'))

# # ==============================================================
# # ROTAS PÚBLICAS
# # ==============================================================

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/ranking/herois')
# def ranking_herois():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT h.*, t.nome_time 
#         FROM herois h
#         JOIN times t ON t.id_time = h.id_time
#         ORDER BY h.rank_geral ASC
#     """)
#     herois = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('ranking_herois.html', herois=herois)

# @app.route('/ranking/times')
# def ranking_times():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT t.*, COUNT(h.id_heroi) AS qtd_herois
#         FROM times t
#         LEFT JOIN herois h ON h.id_time = t.id_time
#         GROUP BY t.id_time
#         ORDER BY t.rank_geral ASC
#     """)
#     times = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('ranking_times.html', times=times)

# @app.route('/time/<int:id_time>')
# def ver_time(id_time):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
#     time = cursor.fetchone()
#     cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (id_time,))
#     herois = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('ver_time.html', time=time, herois=herois)

# @app.route('/heroi/<int:id_heroi>')
# def ver_heroi(id_heroi):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT h.*, t.nome_time
#         FROM herois h
#         JOIN times t ON t.id_time = h.id_time
#         WHERE h.id_heroi = %s
#     """, (id_heroi,))
#     heroi = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return render_template('ver_heroi.html', heroi=heroi)

# # ==============================================================
# # ROTAS TIME
# # ==============================================================



# # ==============================================================
# # ROTAS ADMIN
# # ==============================================================

# @admin_bp.route('/')
# @admin_required
# def painel_admin():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT t.id_time, t.nome_time, u.nome_usuario
#         FROM times t
#         JOIN usuarios u ON t.id_usuario = u.id_usuario
#         ORDER BY t.nome_time
#     """)
#     times = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('dashboard_admin.html', times=times)

# @admin_bp.route('/time/<int:id_time>')
# @admin_required
# def admin_ver_time(id_time):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM times WHERE id_time = %s", (id_time,))
#     time = cursor.fetchone()
#     cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (id_time,))
#     herois = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('ver_time.html', time=time, herois=herois, modo_admin=True)

# @admin_bp.route('/dashboard')
# @admin_required
# def dashboard_admin():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT t.id_time, t.nome_time, u.nome_usuario, COUNT(h.id_heroi) AS qtd_herois
#         FROM times t
#         JOIN usuarios u ON t.id_usuario = u.id_usuario
#         LEFT JOIN herois h ON h.id_time = t.id_time
#         GROUP BY t.id_time
#         ORDER BY t.nome_time
#     """)
#     times = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('dashboard_admin.html', times=times)

# # ==============================================================
# # DASHBOARD (time)
# # ==============================================================

# @app.route('/dashboard')
# @login_required
# def dashboard_time():
#     id_usuario = session.get('id_usuario')
#     tipo = session.get('tipo_usuario')

#     # Evita que o admin acesse esta rota
#     if tipo == 'ADMIN':
#         flash("Acesse o painel administrativo.", "info")
#         return redirect(url_for('admin.dashboard_admin'))

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM times WHERE id_usuario = %s", (id_usuario,))
#     time = cursor.fetchone()
#     cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (time['id_time'],))
#     herois = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     return render_template('dashboard_time.html', time=time, herois=herois)
#endregion


#}>===-------===<:/%@@%/:>===-------===<{#
#|               EXECUÇÃO               |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

if __name__ == '__main__':
    app.run(debug=True)

# endregion
