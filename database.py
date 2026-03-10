# ============================================================
#  database.py  —  Configuração e conexão com o SQLite
# ============================================================

import sqlite3
from flask import g

# Caminho do arquivo de banco de dados gerado automaticamente
DATABASE = "tarefas.db"


def get_db():
    """
    Retorna a conexão ativa com o banco de dados.
    A conexão fica armazenada em 'g' (contexto de requisição do Flask)
    para ser reutilizada durante toda a requisição e fechada ao final.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        # row_factory permite acessar colunas pelo nome (dict-like)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Fecha a conexão com o banco ao final de cada requisição."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Cria a tabela 'tarefas' caso ela ainda não exista.
    Chamado uma única vez ao subir a aplicação.
    """
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT    NOT NULL,
            descricao   TEXT,
            status      TEXT    NOT NULL DEFAULT 'pendente',
            criado_em   TEXT    NOT NULL
        )
        """
    )
    db.commit()
    db.close()
