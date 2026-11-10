from app.database import DatabaseConnection


class Livro:
    def __init__(self, titulo=None, autor=None, ano=None,
                 livro_id=None, user_id=None):
        self.id = livro_id
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.user_id = user_id

    @classmethod
    def init_db(cls):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS livros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    ano INTEGER NOT NULL,
                    user_id INTEGER
                )
            """)

            cursor.execute("PRAGMA table_info(livros)")
            colunas = [coluna["name"] for coluna in cursor.fetchall()]

            if "user_id" not in colunas:
                cursor.execute(
                    "ALTER TABLE livros ADD COLUMN user_id INTEGER"
                )

    def salvar(self):
        self.init_db()

        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO livros (titulo, autor, ano, user_id)
                VALUES (?, ?, ?, ?)
            """, (self.titulo, self.autor, self.ano, self.user_id))

            self.id = cursor.lastrowid

        return self

    @classmethod
    def get_by_user(cls, user_id):
        cls.init_db()

        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, titulo, autor, ano, user_id
                FROM livros
                WHERE user_id = ?
                ORDER BY titulo
            """, (user_id,))

            return cursor.fetchall()

    @classmethod
    def get_all(cls):
        cls.init_db()

        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, titulo, autor, ano, user_id
                FROM livros
                ORDER BY titulo
            """)

            return cursor.fetchall()

    @classmethod
    def excluir(cls, livro_id, user_id):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM livros
                WHERE id = ? AND user_id = ?
            """, (livro_id, user_id))

            return cursor.rowcount > 0