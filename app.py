from __future__ import annotations

from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, url_for

from database import (
    buscar_manifestacao_por_id,
    buscar_manifestacoes_filtradas,
    contar_manifestacoes_por_status,
    criar_manifestacao,
    criar_morador,
    excluir_manifestacao,
    init_db,
    listar_manifestacoes,
    obter_morador_por_id,
    atualizar_manifestacao,
)

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.config["SECRET_KEY"] = "falaai-uc35-projeto-integrador"

CATEGORIAS = [
    "Salas e infraestrutura",
    "Laboratórios e equipamentos",
    "Biblioteca e espaços de estudo",
    "Internet e tecnologia",
    "Acessibilidade",
    "Limpeza e conforto",
    "Convivência e segurança",
    "Eventos e atividades",
    "Sugestão acadêmica",
    "Outro",
]

STATUSES = ["pendente", "em análise", "resolvido"]


@app.before_request
def inicializar_banco():
    init_db()


@app.route("/")
def index():
    """Página inicial com resumo das ocorrências."""
    manifestacoes = listar_manifestacoes()
    totais = contar_manifestacoes_por_status()
    return render_template("index.html", manifestacoes=manifestacoes[:5], totais=totais)


@app.route("/sobre")
def sobre():
    """Página institucional do projeto."""
    return render_template("about.html")


@app.route("/manifestacoes")
def suggestions():
    """Listagem completa das manifestações registradas."""
    manifestacoes = listar_manifestacoes()
    return render_template(
        "suggestions.html",
        manifestacoes=manifestacoes,
        categorias=CATEGORIAS,
        statuses=STATUSES,
    )


@app.route("/manifestacao/<int:id>")
def suggestion_detail(id):
    """Detalhe de uma contribuição específica."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Contribuição não encontrada.", "error")
        return redirect(url_for("suggestions"))
    return render_template("suggestion_detail.html", manifestacao=manifestacao)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    """Cadastro de estudante e manifestação."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        curso = request.form.get("curso", "").strip()
        unidade = request.form.get("unidade", "").strip()
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "pendente").strip().lower()

        if not all([nome, curso, unidade, titulo, categoria, descricao]):
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        if categoria not in CATEGORIAS:
            flash("Categoria inválida.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        if status not in STATUSES:
            flash("Status inválido.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        morador_id = criar_morador(nome, curso, unidade)
        criar_manifestacao(titulo, categoria, descricao, status, morador_id)
        flash("Contribuição publicada com sucesso!", "success")
        return redirect(url_for("suggestions"))

    return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """Edição de uma contribuição."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Contribuição não encontrada para edição.", "error")
        return redirect(url_for("suggestions"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "pendente").strip().lower()

        if not all([titulo, categoria, descricao]):
            flash("Todos os campos da contribuição devem ser preenchidos.", "error")
            return render_template(
                "edit.html",
                manifestacao=manifestacao,
                categorias=CATEGORIAS,
                statuses=STATUSES,
            )

        if categoria not in CATEGORIAS:
            flash("Categoria inválida.", "error")
            return render_template(
                "edit.html",
                manifestacao=manifestacao,
                categorias=CATEGORIAS,
                statuses=STATUSES,
            )

        if status not in STATUSES:
            flash("Status inválido.", "error")
            return render_template(
                "edit.html",
                manifestacao=manifestacao,
                categorias=CATEGORIAS,
                statuses=STATUSES,
            )

        atualizar_manifestacao(id, titulo, categoria, descricao, status)
        flash("Contribuição atualizada com sucesso!", "success")
        return redirect(url_for("suggestion_detail", id=id))

    return render_template("edit.html", manifestacao=manifestacao, categorias=CATEGORIAS, statuses=STATUSES)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Exclusão de contribuição via POST para evitar GET insegura."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Não foi possível encontrar a contribuição para excluir.", "error")
        return redirect(url_for("suggestions"))

    excluir_manifestacao(id)
    flash("Contribuição removida com sucesso.", "success")
    return redirect(url_for("suggestions"))


@app.route("/consulta")
def consulta():
    """Consulta filtrada por categoria e status usando INNER JOIN."""
    categoria = request.args.get("categoria", "").strip()
    status = request.args.get("status", "").strip().lower()

    manifestacoes = buscar_manifestacoes_filtradas(categoria or None, status or None)
    return render_template(
        "suggestions.html",
        manifestacoes=manifestacoes,
        categoria_filtro=categoria,
        status_filtro=status,
        categorias=CATEGORIAS,
        statuses=STATUSES,
    )


@app.route("/api/manifestacoes")
def api_manifestacoes():
    """API em JSON com todas as manifestações."""
    manifestacoes = listar_manifestacoes()
    dados = []
    for item in manifestacoes:
        dados.append(
            {
                "id": item["id"],
                "titulo": item["titulo"],
                "categoria": item["categoria"],
                "descricao": item["descricao"],
                "status": item["status"],
                "estudante": {
                    "nome": item["nome_estudante"],
                    "curso": item["curso"],
                    "unidade": item["unidade"],
                },
            }
        )
    return jsonify({"count": len(dados), "manifestacoes": dados})


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
