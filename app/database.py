import sqlite3
import os

class DatabaseConnection:
    """
    Gestor de Contexto (Context Manager) para a conexão nativa com o SQLite.
    Utiliza __enter__ e __exit__ para garantir o fecho automático da conexão.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            # Aponta para o ficheiro biblioteca.db localizado na raiz do projeto
            basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.db_path = os.path.join(basedir, "biblioteca.db")
        else:
            self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        # Permite aceder aos campos da tabela pelo nome da coluna (ex: row["username"])
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                # Se ocorreu um erro, desfaz a transação
                self.conn.rollback()
            else:
                # Sucesso: guarda as alterações
                self.conn.commit()
            self.conn.close()
        return False