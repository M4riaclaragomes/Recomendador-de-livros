# app.py - Servidor de backend com Flask e Neo4j para o Sistema de Biblioteca
# Para executar:
# 1. Instale as dependências: pip install Flask neo4j python-dotenv Flask-Cors
# 2. Crie um arquivo .env na mesma pasta com suas credenciais do Neo4j:
#    NEO4J_URI=bolt://localhost:7687
#    NEO4J_USERNAME=neo4j
#    NEO4J_PASSWORD=your_neo4j_password
# 3. Execute: python app.py

from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from flask_cors import CORS # Importa a extensão CORS

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas da aplicação

# Configurações do Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Inicializa o driver do Neo4j
driver = None # Inicializa como None para garantir que esteja definido
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    # Testa a conexão imediatamente
    with driver.session() as session:
        session.run("RETURN 1")
    print("Conexão com Neo4j estabelecida com sucesso.")
except Exception as e:
    print(f"Erro ao conectar ao Neo4j: {e}")
    # driver permanece None se a conexão falhar

# Função para fechar a conexão com o banco de dados ao desligar o aplicativo
@app.teardown_appcontext
def close_db(error):
    if driver:
        driver.close()
        print("Conexão com Neo4j fechada.")

# Endpoint de recomendação de livros (existente)
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if not driver:
        return jsonify({"error": "Banco de dados não conectado."}), 500

    genre = request.args.get('genre')
    author = request.args.get('author')

    if not genre:
        return jsonify({"error": "O parâmetro 'genre' é obrigatório."}), 400

    query = """
        MATCH (l:Livro)-[:TEM_GENERO]->(g:Genero)
        WHERE toLower(g.nome) CONTAINS toLower($genre)
    """
    params = {"genre": genre}

    query += """
        OPTIONAL MATCH (l)-[:ESCRITO_POR]->(a:Autor)
    """

    if author and author.lower() != 'qualquer':
        query += """
            WHERE toLower(a.nome) CONTAINS toLower($author)
        """
        params["author"] = author

    query += """
        RETURN l.titulo AS title, a.nome AS author, g.nome AS genre
        LIMIT 3
    """

    try:
        with driver.session() as session:
            result = session.run(query, params)
            recommendations = []
            for record in result:
                recommendations.append({
                    "title": record["title"],
                    "author": record["author"] if record["author"] is not None else "Desconhecido",
                    "genre": record["genre"]
                })
            return jsonify(recommendations), 200
    except Exception as e:
        print(f"Erro ao executar consulta Cypher: {e}")
        return jsonify({"error": "Erro interno do servidor ao buscar recomendações."}), 500

# NOVO ENDPOINT: Executar consulta Cypher arbitrária
@app.route('/api/cypher', methods=['POST'])
def execute_cypher_query():
    if not driver:
        return jsonify({"error": "Banco de dados não conectado."}), 500
    
    data = request.get_json()
    query = data.get('query')
    params = data.get('params', {}) # Permite passar parâmetros para a consulta

    if not query:
        return jsonify({"error": "A consulta Cypher é obrigatória."}), 400

    try:
        with driver.session() as session:
            result = session.run(query, params)
            # Para consultas de leitura (MATCH/RETURN), retorna os dados
            # Para consultas de escrita (CREATE/SET/DELETE), retorna metadados
            records = []
            try:
                for record in result:
                    records.append(record.data())
            except Exception:
                # Se não for uma consulta que retorna dados (ex: CREATE, DELETE),
                # result.data() pode falhar. Capturamos metadados da transação.
                summary = result.consume()
                records.append({
                    "nodes_created": summary.counters.nodes_created,
                    "relationships_created": summary.counters.relationships_created,
                    "nodes_deleted": summary.counters.nodes_deleted,
                    "relationships_deleted": summary.counters.relationships_deleted,
                    "properties_set": summary.counters.properties_set,
                    "labels_added": summary.counters.labels_added,
                    "labels_removed": summary.counters.labels_removed,
                    "message": "Consulta executada com sucesso. Verifique os contadores."
                })
            return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao executar consulta Cypher: {str(e)}"}), 500

# Funções auxiliares para contagem de nós
def get_node_count(label):
    if not driver: return 0
    try:
        with driver.session() as session:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
            return result.single()["count"]
    except Exception as e:
        print(f"Erro ao contar nós {label}: {e}")
        return 0

# NOVO ENDPOINT: Total de Autores
@app.route('/api/stats/total_authors', methods=['GET'])
def total_authors():
    return jsonify({"count": get_node_count("Autor")})

# NOVO ENDPOINT: Total de Livros
@app.route('/api/stats/total_books', methods=['GET'])
def total_books():
    return jsonify({"count": get_node_count("Livro")})

# NOVO ENDPOINT: Total de Gêneros
@app.route('/api/stats/total_genres', methods=['GET'])
def total_genres():
    return jsonify({"count": get_node_count("Genero")})

# NOVO ENDPOINT: Total de Editoras (assumindo que Editora pode não existir)
@app.route('/api/stats/total_publishers', methods=['GET'])
def total_publishers():
    return jsonify({"count": get_node_count("Editora")})

# NOVO ENDPOINT: Autores Mais Produtivos
@app.route('/api/stats/most_productive_authors', methods=['GET'])
def most_productive_authors():
    if not driver: return jsonify([])
    try:
        with driver.session() as session:
            query = """
            MATCH (a:Autor)-[:ESCRITO_POR]->(l:Livro)
            RETURN a.nome AS author, count(l) AS bookCount
            ORDER BY bookCount DESC
            LIMIT 3
            """
            result = session.run(query)
            return jsonify([record.data() for record in result]), 200
    except Exception as e:
        print(f"Erro ao buscar autores mais produtivos: {e}")
        return jsonify({"error": f"Erro ao buscar autores mais produtivos: {str(e)}"}), 500

# NOVO ENDPOINT: Gêneros Mais Populares
@app.route('/api/stats/most_popular_genres', methods=['GET'])
def most_popular_genres():
    if not driver: return jsonify([])
    try:
        with driver.session() as session:
            query = """
            MATCH (g:Genero)<-[:TEM_GENERO]-(l:Livro)
            RETURN g.nome AS genre, count(l) AS bookCount
            ORDER BY bookCount DESC
            LIMIT 3
            """
            result = session.run(query)
            return jsonify([record.data() for record in result]), 200
    except Exception as e:
        print(f"Erro ao buscar gêneros mais populares: {e}")
        return jsonify({"error": f"Erro ao buscar gêneros mais populares: {str(e)}"}), 500

# NOVO ENDPOINT: Limpar Banco de Dados
@app.route('/api/clear_database', methods=['POST'])
def clear_database_endpoint():
    if not driver:
        return jsonify({"error": "Banco de dados não conectado."}), 500
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        return jsonify({"message": "Banco de dados limpo com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao limpar o banco de dados: {e}")
        return jsonify({"error": f"Erro ao limpar o banco de dados: {str(e)}"}), 500

# NOVO ENDPOINT: Testar Conexão
@app.route('/api/test_connection', methods=['GET'])
def test_connection_endpoint():
    if driver:
        try:
            with driver.session() as session:
                session.run("RETURN 1") # Consulta simples para verificar a conectividade
            return jsonify({"status": "connected", "message": "Conexão com Neo4j estabelecida."}), 200
        except Exception as e:
            return jsonify({"status": "disconnected", "message": f"Erro na conexão com Neo4j: {str(e)}"}), 500
    else:
        return jsonify({"status": "disconnected", "message": "Driver Neo4j não inicializado."}), 500

if __name__ == '__main__':
    # Para desenvolvimento, use debug=True. Em produção, desative.
    app.run(debug=True, port=5000)
