# ============================================================
#  app.py  —  Ponto de entrada da aplicação
#  Inicializa o Flask, registra as rotas e cria o banco de dados
# ============================================================

from flask import Flask
from database import init_db
from routes import tarefas_bp

# Cria a instância principal do Flask
app = Flask(__name__)

# Registra o Blueprint com todas as rotas de /tarefas
app.register_blueprint(tarefas_bp)

# Inicializa o banco de dados (cria tabela se não existir)
with app.app_context():
    init_db()

if __name__ == "__main__":
    # debug=True recarrega automaticamente ao salvar o arquivo
    app.run(debug=True, port=5000)
