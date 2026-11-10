
import sqlite3
from functools import wraps

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)

from app.models.user import (
    User,
    get_user_by_username,
    check_user_password,
    create_user
)

from app.models.livro import Livro
from app.database import DatabaseConnection


auth_bp = Blueprint('auth', __name__)


def migrar_livros_admin():
    User.init_db()
    Livro.init_db()

    admin = User.get_by_username('admin')

    if admin:
        with DatabaseConnection() as conn:
            conn.execute("""
                UPDATE livros
                SET user_id = ?
                WHERE user_id IS NULL
            """, (admin.id,))


def login_obrigatorio(func):
    @wraps(func)
    def verificar(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login para acessar sua biblioteca.', 'warning')
            return redirect(url_for('auth.login'))

        return func(*args, **kwargs)

    return verificar


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    User.init_db()
    migrar_livros_admin()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_username(username)

        if user and check_user_password(user, password):
            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('auth.welcome'))

        flash('Usuário ou senha inválidos!', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    User.init_db()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if len(username) < 3:
            flash('O usuário precisa ter pelo menos 3 caracteres.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('A senha precisa ter pelo menos 6 caracteres.', 'danger')
            return render_template('register.html')

        if get_user_by_username(username):
            flash('Este usuário já está cadastrado.', 'danger')
            return render_template('register.html')

        try:
            create_user(username, password)

            if username.lower() == 'admin':
                migrar_livros_admin()

            flash('Conta criada com sucesso! Faça seu login.', 'success')
            return redirect(url_for('auth.login'))

        except sqlite3.IntegrityError:
            flash('Este nome de usuário já está em uso.', 'danger')

    return render_template('register.html')


@auth_bp.route('/welcome')
@login_obrigatorio
def welcome():
    migrar_livros_admin()

    usuario = User.get_by_id(session['user_id'])

    if not usuario:
        session.clear()
        return redirect(url_for('auth.login'))

    livros = Livro.get_by_user(usuario.id)

    return render_template(
        'welcome.html',
        usuario=usuario,
        livros=livros
    )


@auth_bp.route('/livros/novo', methods=['GET', 'POST'])
@login_obrigatorio
def cadastrar_livro():
    usuario = User.get_by_id(session['user_id'])

    if not usuario:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        ano_texto = request.form.get('ano', '').strip()

        if not titulo or not autor or not ano_texto:
            flash('Preencha todos os campos.', 'danger')
            return render_template('cadastrar_livro.html')

        try:
            ano = int(ano_texto)

            if ano < 1 or ano > 9999:
                raise ValueError

        except ValueError:
            flash('Informe um ano válido.', 'danger')
            return render_template('cadastrar_livro.html')

        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            ano=ano,
            user_id=usuario.id
        )

        novo_livro.salvar()

        flash('Livro cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.welcome'))

    return render_template('cadastrar_livro.html')


@auth_bp.route('/livros/excluir/<int:livro_id>', methods=['POST'])
@login_obrigatorio
def excluir_livro(livro_id):
    usuario = User.get_by_id(session['user_id'])

    if not usuario:
        session.clear()
        return redirect(url_for('auth.login'))

    excluido = Livro.excluir(livro_id, usuario.id)

    if excluido:
        flash('Livro excluído com sucesso!', 'success')
    else:
        flash(
            'Livro não encontrado ou você não tem permissão para excluí-lo.',
            'danger'
        )

    return redirect(url_for('auth.welcome'))


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('auth.login'))
