# FalaAí - UC35

O FalaAí é uma plataforma de participação comunitária para registrar reclamações, sugestões e problemas encontrados em bairros, como iluminação pública, lixo, buracos nas ruas, segurança e infraestrutura.

## Tecnologias

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2

## Estrutura do projeto

FalaAi_UC35/
- app.py
- database.py
- banco.db
- requirements.txt
- Procfile
- README.md
- templates/
  - base.html
  - index.html
  - about.html
  - submit.html
  - suggestions.html
  - suggestion_detail.html
  - edit.html
- static/
  - style.css
  - script.js

## Como executar

1. Abra o terminal no diretório do projeto.
2. Crie um ambiente virtual:
   python -m venv .venv
3. Ative o ambiente virtual:
   - Windows: .venv\Scripts\activate
   - Linux/Mac: source .venv/bin/activate
4. Instale as dependências:
   pip install -r requirements.txt
5. Inicie a aplicação:
   python app.py
6. Acesse no navegador:
   http://127.0.0.1:5000/

## Funcionalidades

- Página inicial
- Página sobre o projeto
- Cadastro de manifestações
- Listagem de manifestações
- Visualização individual
- Edição de manifestações
- Exclusão de manifestações
- Identificação do morador
- Categorias e status
- API JSON em /api/manifestacoes

## Banco de dados e persistência

O projeto usa SQLite. A base está em `banco.db` dentro da pasta do projeto.

No Render, o SQLite local não é preservado automaticamente. Para manter os dados, é necessário configurar um disco persistente ou usar um banco externo. Em geral, no Render, você deve:

1. Criar um disco persistente no serviço.
2. Montar esse volume em um diretório do app, como `/data`.
3. Ajustar a variável de ambiente ou o caminho do banco para esse diretório, por exemplo:
   `SQLITE_PATH=/data/banco.db`
4. Alterar a configuração do app para usar esse caminho em vez do banco local do projeto.

A aplicação atual usa o arquivo `banco.db` na pasta do projeto. Quando o serviço de hospedagem oferece armazenamento persistente, o caminho deve ser movido para esse volume para garantir que os dados continuem disponíveis após reinicializações.

## Observações de segurança

- Validação no servidor de todos os campos.
- Consultas SQL parametrizadas.
- Tratamento de registros inexistentes.
- Exclusão por POST, nunca por GET.

## Deploy no Render

Antes de publicar, verifique:

- Arquivo `requirements.txt` preenchido corretamente.
- Arquivo `Procfile` com o conteúdo esperado.
- O app tenha uma variável `app` exportada.
- O banco esteja em um local persistente se você usar SQLite no Render.

## Licença

Projeto acadêmico para a UC35 - Projeto Integrador Back-end.
