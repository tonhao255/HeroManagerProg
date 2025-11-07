#}>===-------===<:/%@@%/:>===-------===<{#
#|              IMPORTAÇÃO              |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

# endregion



#}>===-------===<:/%@@%/:>===-------===<{#
#|             CONFIGURAÇÃO             |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

app = Flask(__name__)
app.secret_key = 'chave-muito-secreta'

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
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'ADMIN':
            flash('Acesso restrito a administradores.', 'erro')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para acessar o painel.', 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

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
            h.nivel,
            h.forca,
            h.defesa,
            h.velocidade,
            c.nome_classe AS classe,
            t.nome_time AS time
        FROM herois h
        JOIN classes c ON h.id_classe = c.id_classe
        JOIN times t ON h.id_time = t.id_time
        ORDER BY c.nome_classe, h.id_heroi;
    """)
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
            session['usuario_id'] = user['id_usuario']
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
#|             ROTAS EDITAR             |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region



#endregion


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
#             session['usuario_id'] = user['id_usuario']
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
#     usuario_id = session.get('usuario_id')
#     tipo = session.get('tipo_usuario')

#     # Evita que o admin acesse esta rota
#     if tipo == 'ADMIN':
#         flash("Acesse o painel administrativo.", "info")
#         return redirect(url_for('admin.dashboard_admin'))

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM times WHERE id_usuario = %s", (usuario_id,))
#     time = cursor.fetchone()
#     cursor.execute("SELECT * FROM herois WHERE id_time = %s ORDER BY id_heroi", (time['id_time'],))
#     herois = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     return render_template('dashboard_time.html', time=time, herois=herois)


#}>===-------===<:/%@@%/:>===-------===<{#
#|               EXECUÇÃO               |#
#}>===-------===<:/%@@%/:>===-------===<{#
# region

if __name__ == '__main__':
    app.run(debug=True)

# endregion
