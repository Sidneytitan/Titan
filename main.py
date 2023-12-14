from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# Configuração do MongoDB
app.config['MONGO_URI'] = "mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/supply"
mongo = PyMongo(app)

# Verificação de Conexão com o MongoDB
if mongo.db.command('ping')['ok'] != 1:
    raise ConnectionError("Erro de conexão com o MongoDB. Verifique suas credenciais e conexão.")

# Rota para a página Kanban
@app.route('/kanban')
def kanban():
    # Obtendo dados do MongoDB
    dados_kanban = mongo.db.cotacao.find()
    return render_template('kanban.html', dados_kanban=dados_kanban)

# Rota para obter todas as cotações
@app.route('/dados_kanban', methods=['GET'])
def get_dados_kanban():
    # Obtendo dados do MongoDB
    dados_kanban = mongo.db.cotacao.find()

    # Converter ObjectId para str para torná-lo serializável em JSON
    dados_kanban_serializable = [
        {
            "_id": str(dado["_id"]),
            "titulo": dado["titulo"],
            "descricao": dado["descricao"],
            "status": dado["status"]
        }
        for dado in dados_kanban
    ]

    return jsonify({'dados_kanban': dados_kanban_serializable})

# Rota para adicionar um novo item ao Kanban
@app.route('/criar_cotacao', methods=['POST'])
def criar_cotacao():
    data = request.form

    if 'new-task-title' in data and 'new-task-description' in data:
        mongo.db.cotacao.insert_one({
            'titulo': data['new-task-title'],
            'descricao': data['new-task-description'],
            'status': data['new-task-status']
        })
        return jsonify({'message': 'Cotação criada com sucesso!'})

    return jsonify({'error': 'Campos título e descrição são obrigatórios!'}), 400

# Rota para mover um item para uma nova coluna
@app.route('/mover_item_coluna/<item_id>/<nova_coluna>', methods=['PUT'])
def mover_item_coluna(item_id, nova_coluna):
    # Atualizar o status do item no MongoDB
    mongo.db.cotacao.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {'status': nova_coluna}}
    )
    return jsonify({'message': 'Item movido com sucesso!'})

# Rota para excluir uma cotação
@app.route('/excluir_cotacao/<item_id>', methods=['DELETE'])
def excluir_cotacao(item_id):
    try:
        # Excluir o item do MongoDB
        result = mongo.db.cotacao.delete_one({'_id': ObjectId(item_id)})

        if result.deleted_count == 1:
            return jsonify({'message': 'Cotação excluída com sucesso!'})
        else:
            return jsonify({'error': 'Cotação não encontrada'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para exibir a lista de fornecedores
@app.route('/listafornecedor')
def lista_fornecedor():
    # Obtendo dados do MongoDB
    data_list = mongo.db.lista_fornecedor.find()
    return render_template('index.html', data_list=data_list)

# Rota para exibir a página inicial
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Rota para exibir o formulário de adição
@app.route('/adicionar', methods=['GET'])
def exibir_formulario_adicao():
    return render_template('adicionar.html')

# Rota para lidar com a adição de fornecedores (POST)
@app.route('/adicionar_fornecedor', methods=['POST'])
def adicionar_fornecedor():
    if request.method == 'POST':
        novo_fornecedor = {
            'fornecedor': request.form['fornecedor'],
            'cnpj': request.form['cnpj'],
            'telefone': request.form['telefone'],
            'responsavel': request.form['responsavel'],
            'local': request.form['local'],
            'cep': request.form['cep']
        }

        # Insere o fornecedor no MongoDB
        mongo.db.lista_fornecedor.insert_one(novo_fornecedor)

    return redirect(url_for('listafornecedor'))

# Rota para exibir o formulário de exclusão
@app.route('/excluir', methods=['GET', 'POST'])
def exibir_formulario_exclusao():
    if request.method == 'POST':
        # Obtendo o nome do fornecedor a ser excluído do formulário
        excluir = request.form['Fornecedor']

        # Excluir o fornecedor pelo nome
        mongo.db.lista_fornecedor.delete_one({'fornecedor': excluir})

        return redirect(url_for('listafornecedor'))

    return render_template('excluir.html')

# Adicione uma rota para lidar com a pesquisa
@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    # Obter os parâmetros da pesquisa
    filtro = request.args.get('filtro')
    termo = request.args.get('termo')

    # Construir a consulta MongoDB com base nos parâmetros de pesquisa
    query = {filtro: {'$regex': termo, '$options': 'i'}}
    data_list = mongo.db.lista_fornecedor.find(query)

    return render_template('index.html', data_list=data_list)

if __name__ == "__main__":
    app.run(debug=True)

#Anotação

#  <!-- Footer Section -->
    #<footer>Sidney Ribeiro</footer>