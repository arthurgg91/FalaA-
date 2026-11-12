import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "banco.db"


def get_connection():
    """Cria a conexão com o banco SQLite usando Row para facilitar o acesso."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas iniciais do sistema."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS moradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                bairro TEXT NOT NULL,
                cep TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS manifestacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                morador_id INTEGER NOT NULL,
                FOREIGN KEY (morador_id) REFERENCES moradores(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def criar_morador(nome, curso, unidade):
    """Cadastra um estudante e retorna o ID gerado."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO moradores (nome, bairro, cep) VALUES (?, ?, ?)",
            (nome, curso, unidade),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def criar_manifestacao(titulo, categoria, descricao, status, morador_id):
    """Cria uma manifestação vinculada a um morador."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO manifestacoes (titulo, categoria, descricao, status, morador_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (titulo, categoria, descricao, status, morador_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def listar_manifestacoes():
    """Retorna todas as manifestações com a informação do morador usando INNER JOIN."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT m.id, m.titulo, m.categoria, m.descricao, m.status,
                   mor.nome AS nome_estudante,
                   mor.bairro AS curso, mor.cep AS unidade
            FROM manifestacoes m
            INNER JOIN moradores mor ON m.morador_id = mor.id
            ORDER BY m.id DESC
            """
        ).fetchall()
    finally:
        conn.close()


def buscar_manifestacao_por_id(manifestacao_id):
    """Busca uma manifestação completa pelo ID."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT m.id, m.titulo, m.categoria, m.descricao, m.status,
                   m.morador_id, mor.nome AS nome_estudante,
                   mor.bairro AS curso, mor.cep AS unidade
            FROM manifestacoes m
            INNER JOIN moradores mor ON m.morador_id = mor.id
            WHERE m.id = ?
            """,
            (manifestacao_id,),
        ).fetchone()
    finally:
        conn.close()


def atualizar_manifestacao(manifestacao_id, titulo, categoria, descricao, status):
    """Atualiza os dados de uma manifestação."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE manifestacoes
            SET titulo = ?, categoria = ?, descricao = ?, status = ?
            WHERE id = ?
            """,
            (titulo, categoria, descricao, status, manifestacao_id),
        )
        conn.commit()
    finally:
        conn.close()


def excluir_manifestacao(manifestacao_id):
    """Remove a manifestação da base de dados."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM manifestacoes WHERE id = ?", (manifestacao_id,))
        conn.commit()
    finally:
        conn.close()


def buscar_manifestacoes_filtradas(categoria=None, status=None):
    """Consulta com filtros por categoria e status usando SQL parametrizado."""
    conn = get_connection()
    try:
        query = """
            SELECT m.id, m.titulo, m.categoria, m.descricao, m.status,
                   mor.nome AS nome_estudante,
                   mor.bairro AS curso, mor.cep AS unidade
            FROM manifestacoes m
            INNER JOIN moradores mor ON m.morador_id = mor.id
        """
        filtros = []
        parametros = []

        if categoria:
            filtros.append("m.categoria = ?")
            parametros.append(categoria)
        if status:
            filtros.append("m.status = ?")
            parametros.append(status)

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        query += " ORDER BY m.id DESC"
        return conn.execute(query, tuple(parametros)).fetchall()
    finally:
        conn.close()


def contar_manifestacoes_por_status():
    """Retorna contagem por status para a página inicial."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM manifestacoes
            GROUP BY status
            """
        ).fetchall()
    finally:
        conn.close()


def obter_morador_por_id(morador_id):
    """Busca um morador pelo seu ID."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id, nome, bairro AS curso, cep AS unidade FROM moradores WHERE id = ?",
            (morador_id,),
        ).fetchone()
    finally:
        conn.close()
