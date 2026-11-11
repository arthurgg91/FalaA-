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
    "Iluminação pública",
    "Lixo e coleta",
    "Buraco na rua",
    "Segurança",
    "Infraestrutura",
    "Água e saneamento",
    "Transito e vias",
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
    """Detalhe de uma manifestação específica."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Manifestação não encontrada.", "error")
        return redirect(url_for("suggestions"))
    return render_template("suggestion_detail.html", manifestacao=manifestacao)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    """Cadastro de morador e manifestação."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        bairro = request.form.get("bairro", "").strip()
        cep = request.form.get("cep", "").strip()
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "pendente").strip().lower()

        if not all([nome, bairro, cep, titulo, categoria, descricao]):
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        if categoria not in CATEGORIAS:
            flash("Categoria inválida.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        if status not in STATUSES:
            flash("Status inválido.", "error")
            return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)

        morador_id = criar_morador(nome, bairro, cep)
        criar_manifestacao(titulo, categoria, descricao, status, morador_id)
        flash("Manifestação cadastrada com sucesso!", "success")
        return redirect(url_for("suggestions"))

    return render_template("submit.html", categorias=CATEGORIAS, statuses=STATUSES)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """Edição de uma manifestação."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Manifestação não encontrada para edição.", "error")
        return redirect(url_for("suggestions"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "pendente").strip().lower()

        if not all([titulo, categoria, descricao]):
            flash("Todos os campos da manifestação devem ser preenchidos.", "error")
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
        flash("Manifestação atualizada com sucesso!", "success")
        return redirect(url_for("suggestion_detail", id=id))

    return render_template("edit.html", manifestacao=manifestacao, categorias=CATEGORIAS, statuses=STATUSES)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Exclusão de manifestação via POST para evitar GET insegura."""
    manifestacao = buscar_manifestacao_por_id(id)
    if manifestacao is None:
        flash("Não foi possível encontrar a manifestação para excluir.", "error")
        return redirect(url_for("suggestions"))

    excluir_manifestacao(id)
    flash("Manifestação removida com sucesso.", "success")
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
                "morador": {
                    "nome": item["nome_morador"],
                    "bairro": item["bairro"],
                    "cep": item["cep"],
                },
            }
        )
    return jsonify({"count": len(dados), "manifestacoes": dados})


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
