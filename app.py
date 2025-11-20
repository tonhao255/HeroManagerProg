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
    'database': 'sistema_herois'
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
    return render_template('herois.html', herois=herois)

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

    return render_template('ver_heroi.html', heroi=heroi)


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

    return render_template('times.html', times=times)

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
    
    return render_template('classes.html', classes=classes, tipo=session["tipo_usuario"])

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
            form['id_time'] = session.get('id_time')

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

    # form começa com os valores originais
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
    return render_template('editar_heroi.html', form=form, classes=classes, times=times)

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
            (form['nome_heroi'], id_time)
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
    return render_template('editar_heroi.html', form=form)

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
    app.run(debug=True)

# endregion
# ._____ ____._______
#(  .       (
# '-'        '
