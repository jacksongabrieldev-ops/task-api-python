# ============================================================
#  models.py  —  Lógica de acesso a dados (CRUD)
#  Cada função recebe uma conexão db e retorna dados Python puros
# ============================================================

from datetime import datetime, timezone


def _row_to_dict(row):
    """Converte um sqlite3.Row em dicionário JSON-serializável."""
    return dict(row) if row else None


# ----------------------------------------------------------
# CREATE
# ----------------------------------------------------------
def criar_tarefa(db, titulo: str, descricao: str) -> dict:
    """
    Insere uma nova tarefa no banco.
    Status inicial é sempre 'pendente'.
    Retorna o registro completo recém-criado.
    """
    criado_em = datetime.now(timezone.utc).isoformat()

    cursor = db.execute(
        "INSERT INTO tarefas (titulo, descricao, status, criado_em) VALUES (?, ?, 'pendente', ?)",
        (titulo, descricao, criado_em),
    )
    db.commit()

    # Busca o registro pelo id gerado automaticamente
    return buscar_tarefa(db, cursor.lastrowid)


# ----------------------------------------------------------
# READ (lista)
# ----------------------------------------------------------
def listar_tarefas(db) -> list[dict]:
    """Retorna todas as tarefas ordenadas da mais recente para a mais antiga."""
    rows = db.execute(
        "SELECT * FROM tarefas ORDER BY id DESC"
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


# ----------------------------------------------------------
# READ (único)
# ----------------------------------------------------------
def buscar_tarefa(db, tarefa_id: int) -> dict | None:
    """Retorna uma tarefa pelo ID ou None se não encontrada."""
    row = db.execute(
        "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
    ).fetchone()
    return _row_to_dict(row)


# ----------------------------------------------------------
# UPDATE
# ----------------------------------------------------------
def atualizar_tarefa(db, tarefa_id: int, dados: dict) -> dict | None:
    """
    Atualiza os campos informados em 'dados'.
    Campos aceitos: titulo, descricao, status.
    Retorna o registro atualizado ou None se não existir.
    """
    # Verifica se a tarefa existe antes de tentar atualizar
    if not buscar_tarefa(db, tarefa_id):
        return None

    # Monta dinamicamente apenas as colunas enviadas pelo cliente
    campos_validos = {"titulo", "descricao", "status"}
    atualizacoes = {k: v for k, v in dados.items() if k in campos_validos}

    if not atualizacoes:
        # Nada para atualizar; retorna o registro sem modificar
        return buscar_tarefa(db, tarefa_id)

    # Constrói: "titulo = ?, descricao = ?" etc.
    set_clause = ", ".join(f"{col} = ?" for col in atualizacoes)
    valores = list(atualizacoes.values()) + [tarefa_id]

    db.execute(
        f"UPDATE tarefas SET {set_clause} WHERE id = ?", valores
    )
    db.commit()

    return buscar_tarefa(db, tarefa_id)


# ----------------------------------------------------------
# DELETE
# ----------------------------------------------------------
def deletar_tarefa(db, tarefa_id: int) -> bool:
    """
    Remove a tarefa pelo ID.
    Retorna True se deletado, False se não encontrado.
    """
    if not buscar_tarefa(db, tarefa_id):
        return False

    db.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    db.commit()
    return True
