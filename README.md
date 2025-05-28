# Gestão de Frota Avançado

Sistema web desenvolvido com **FastAPI**, com foco em controle de frota, incluindo:

- Autenticação de gestores
- Cadastro de veículos
- Reserva e devolução de veículos
- Dashboard administrativo
- Visual moderno com Bootstrap

## 🔧 Requisitos

- Python 3.10+
- fastapi
- uvicorn
- jinja2
- starlette
- (opcional) SQLAlchemy para persistência

## ▶️ Como rodar localmente

```bash
# Instale os requisitos
pip install -r requirements.txt

# Rode o servidor
uvicorn main:app --reload
```

## 📁 Estrutura do Projeto

- `main.py` – arquivo principal com as rotas FastAPI
- `templates/` – HTMLs com Jinja2
- `static/` – arquivos CSS e JS
- `models/` – definição de dados e ORM
- `database/` – conexão com banco de dados

---

Desenvolvido por Latitude Genética – setor de Produção.
