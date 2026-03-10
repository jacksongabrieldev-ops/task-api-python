# ============================================================
#  routes.py  —  Rotas REST da API de Tarefas
#
#  POST   /tarefas          → criar tarefa
#  GET    /tarefas          → listar todas
#  GET    /tarefas/<id>     → buscar por ID
#  PUT    /tarefas/<id>     → atualizar
#  DELETE /tarefas/<id>     → deletar
# ============================================================

from flask import Blueprint, request, jsonify, g
from database import get_db, close_db
from models import (
    criar_tarefa,
    listar_tarefas,
    buscar_tarefa,
    atualizar_tarefa,
    deletar_tarefa,
)

# Blueprint agrupa rotas relacionadas; facilita organização e testes
tarefas_bp = Blueprint("tarefas", __name__, url_prefix="/tarefas")


# ------------------------------------------------------------------
# Hook: fecha a conexão com o banco ao final de cada requisição
# ------------------------------------------------------------------
@tarefas_bp.teardown_app_request
def fechar_db(e=None):
    close_db(e)


# ------------------------------------------------------------------
# Helper: retorna o banco de dados do contexto atual
# ------------------------------------------------------------------
def db():
    return get_db()


# ==================================================================
# POST /tarefas  —  Criar nova tarefa
# ==================================================================
@tarefas_bp.route("", methods=["POST"])
def criar():
    """
    Body esperado (JSON):
    {
        "titulo":    "string (obrigatório)",
        "descricao": "string (opcional)"
    }
    """
    dados = request.get_json(silent=True) or {}

    titulo = dados.get("titulo", "").strip()
    if not titulo:
        return jsonify({"erro": "O campo 'titulo' é obrigatório."}), 400

    descricao = dados.get("descricao", "").strip()

    tarefa = criar_tarefa(db(), titulo, descricao)
    return jsonify(tarefa), 201   # 201 Created


# ==================================================================
# GET /tarefas  —  Listar todas as tarefas
# ==================================================================
@tarefas_bp.route("", methods=["GET"])
def listar():
    """
    Suporta filtro opcional por status via query param:
    GET /tarefas?status=pendente
    GET /tarefas?status=concluido
    """
    filtro_status = request.args.get("status")
    tarefas = listar_tarefas(db())

    # Filtra em memória caso o cliente passe ?status=...
    if filtro_status:
        tarefas = [t for t in tarefas if t["status"] == filtro_status]

    return jsonify({"total": len(tarefas), "tarefas": tarefas}), 200


# ==================================================================
# GET /tarefas/<id>  —  Buscar tarefa por ID
# ==================================================================
@tarefas_bp.route("/<int:tarefa_id>", methods=["GET"])
def buscar(tarefa_id):
    tarefa = buscar_tarefa(db(), tarefa_id)
    if not tarefa:
        return jsonify({"erro": f"Tarefa {tarefa_id} não encontrada."}), 404
    return jsonify(tarefa), 200


# ==================================================================
# PUT /tarefas/<id>  —  Atualizar tarefa
# ==================================================================
@tarefas_bp.route("/<int:tarefa_id>", methods=["PUT"])
def atualizar(tarefa_id):
    """
    Body (JSON) — todos os campos são opcionais:
    {
        "titulo":    "novo título",
        "descricao": "nova descrição",
        "status":    "pendente" | "concluido"
    }
    """
    dados = request.get_json(silent=True) or {}

    # Valida o campo 'status' se foi enviado
    if "status" in dados and dados["status"] not in ("pendente", "concluido"):
        return jsonify({"erro": "Status inválido. Use 'pendente' ou 'concluido'."}), 400

    tarefa = atualizar_tarefa(db(), tarefa_id, dados)
    if not tarefa:
        return jsonify({"erro": f"Tarefa {tarefa_id} não encontrada."}), 404

    return jsonify(tarefa), 200


# ==================================================================
# DELETE /tarefas/<id>  —  Deletar tarefa
# ==================================================================
@tarefas_bp.route("/<int:tarefa_id>", methods=["DELETE"])
def deletar(tarefa_id):
    removido = deletar_tarefa(db(), tarefa_id)
    if not removido:
        return jsonify({"erro": f"Tarefa {tarefa_id} não encontrada."}), 404

    return jsonify({"mensagem": f"Tarefa {tarefa_id} deletada com sucesso."}), 200
