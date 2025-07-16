# 📚 Sistema de Biblioteca com Flask e Neo4j

Este projeto é um sistema web para gerenciamento e recomendação de livros, com backend em Flask e banco de dados gráfico Neo4j. A interface web permite cadastrar livros, buscar por gênero/autor, executar comandos Cypher e visualizar estatísticas.

---

## ⚙️ Requisitos

Antes de iniciar, você precisa ter instalado:

- [Python 3.8+](https://www.python.org/downloads/windows/)
- [Neo4j Desktop](https://neo4j.com/download/) 
- [pip](https://pip.pypa.io/en/stable/installation/)

---

## 📦 Instalação

1. **Baixe ou clone o repositório:**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

2. **Instale as dependências:**

```bash
pip install Flask neo4j python-dotenv Flask-Cors
```

3. **Crie (ou edite) o arquivo `.env` com as credenciais do seu banco Neo4j:**

> ⚠️ O arquivo `.env` já está incluso, mas troque os dados para o do seu bd.

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sua_senha
```

---

## 🚀 Executando o Backend

No terminal (dentro da pasta do projeto), execute:

```bash
python app.py
```

O servidor Flask estará disponível em [http://localhost:5000](http://localhost:5000).

---

## 🌐 Executando o Frontend

Abra o arquivo `index.html` diretamente no navegador (clique duas vezes ou abra com Chrome/Edge).

> 💡 O frontend está configurado para se comunicar com o backend em `http://localhost:5000/api`.

---

## 🔁 Endpoints Disponíveis

| Rota | Método | Descrição |
|------|--------|-----------|
| `/api/recommendations` | `GET` | Recomendação de livros por gênero e autor |
| `/api/add_book` | `POST` | Cadastrar novo livro |
| `/api/cypher` | `POST` | Executa consulta Cypher personalizada |
| `/api/stats/*` | `GET` | Retorna estatísticas (livros, autores, gêneros, etc.) |
| `/api/clear_database` | `POST` | Remove todos os dados do banco |
| `/api/test_connection` | `GET` | Verifica a conexão com o Neo4j |

---

## 💡 Exemplo de Uso

1. Cadastre um novo livro na aba **"Cadastrar"**.
2. Faça uma busca por gênero e/ou autor na aba **"Buscar"**.
3. Execute comandos Cypher na aba **"Cypher"**, como:

```cypher
MATCH (a:Autor)-[:ESCRITO_POR]->(l:Livro)
RETURN a.nome, l.titulo
LIMIT 10
```

---

## 🧠 Observações

- O backend precisa estar rodando para que a interface web funcione corretamente.
- Certifique-se de que o Neo4j está ativo e escutando na porta 7687 (padrão).

---

