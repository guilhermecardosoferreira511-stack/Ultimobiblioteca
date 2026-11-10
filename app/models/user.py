import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import DatabaseConnection

# Caminho para o ficheiro biblioteca.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../biblioteca.db'))

class User:
    """
    Classe de Modelo para Utilizadores (Padrão Active Record).
    """
    def __init__(self, username, password_hash=None, user_id=None):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash

    def __getitem__(self, key):
        """Permite aceder às propriedades como se fosse um dicionário (ex: user['password_hash'])"""
        return getattr(self, key)

    # ==========================================
    # MÉTODOS DE INSTÂNCIA
    # ==========================================

    def set_password(self, password):
        """Gera e guarda o hash seguro da palavra-passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Valida a palavra-passe em texto limpo contra o hash guardado."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def save(self):
        """
        Insere um novo utilizador no banco de dados (se id for None)
        ou atualiza o registo existente.
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                # INSERT (novo utilizador)
                sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                cursor.execute(sql, (self.username, self.password_hash))
                self.id = cursor.lastrowid
            else:
                # UPDATE (utilizador existente)
                sql = "UPDATE users SET username = ?, password_hash = ? WHERE id = ?"
                cursor.execute(sql, (self.username, self.password_hash, self.id))
        return self

    def delete(self):
        """Elimina este utilizador do banco de dados."""
        if self.id is not None:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                sql = "DELETE FROM users WHERE id = ?"
                cursor.execute(sql, (self.id,))
                self.id = None

    # ==========================================
    # MÉTODOS DE CLASSE (@classmethod)
    # ==========================================

    @classmethod
    def init_db(cls):
        """Cria a tabela 'users' no SQLite se ela ainda não existir."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                );
            """)

    @classmethod
    def get_by_username(cls, username):
        """Busca um utilizador pelo 'username' e retorna uma instância de User."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id, username, password_hash FROM users WHERE username = ?"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()

            if row:
                return cls(
                    user_id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"]
                )
            return None

    @classmethod
    def get_by_id(cls, user_id):
        """Busca um utilizador pelo 'id' e retorna uma instância de User."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id, username, password_hash FROM users WHERE id = ?"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

            if row:
                return cls(
                    user_id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"]
                )
            return None

    @classmethod
    def get_all(cls):
        """Retorna uma lista com todas as instâncias de User cadastradas."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id, username, password_hash FROM users"
            cursor.execute(sql)
            rows = cursor.fetchall()

            return [
                cls(
                    user_id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"]
                )
                for row in rows
            ]

# ==========================================
# FUNÇÕES DE LIVROS (AUTO-POPOVAÇÃO GARANTIDA)
# ==========================================

def criar_tabela_livros():
    for path in [DB_PATH, 'biblioteca.db']:
        try:
            con = sqlite3.connect(path)
            cur = con.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS livros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    autor TEXT,
                    ano INTEGER
                )
            ''')
            con.commit()
            con.close()
        except Exception:
            pass

def listar_livros():
    criar_tabela_livros()
    todos_livros = []
    
    # Procura na base de dados e povoa automaticamente se estiver vazia
    for path in [DB_PATH, 'biblioteca.db']:
        try:
            con = sqlite3.connect(path)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM livros")
            todos_livros = cur.fetchall()
            
            # Se a tabela estiver vazia, insere os 3 livros e lê novamente
            if not todos_livros:
                cur.execute("INSERT INTO livros (titulo, autor, ano) VALUES ('Dom Casmurro', 'Machado de Assis', 1899)")
                cur.execute("INSERT INTO livros (titulo, autor, ano) VALUES ('O Cortiço', 'Aluísio Azevedo', 1890)")
                cur.execute("INSERT INTO livros (titulo, autor, ano) VALUES ('A Hora da Estrela', 'Clarice Lispector', 1977)")
                con.commit()
                
                cur.execute("SELECT * FROM livros")
                todos_livros = cur.fetchall()
                
            con.close()
            if todos_livros:
                break
        except Exception:
            pass
            
    return todos_livros

# ==========================================
# FUNÇÕES DE COMPATIBILIDADE COM O AUTH
# ==========================================

def get_user_by_username(username):
    return User.get_by_username(username)

def check_user_password(p_hash_or_user, password):
    if isinstance(p_hash_or_user, User):
        return p_hash_or_user.check_password(password)
    if p_hash_or_user:
        return check_password_hash(p_hash_or_user, password)
    return False

def create_user(username, password):
    novo_usuario = User(username=username)
    novo_usuario.set_password(password)
    novo_usuario.save()
    return novo_usuario