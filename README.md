# tcc-scrap

## Banco de dados (PostgreSQL via Docker)

O `docker-compose.yml` sobe um PostgreSQL 16 com o banco `projectTCC`.

### Configuração

Copie o arquivo de exemplo de variáveis de ambiente e ajuste se necessário:

```bash
cp .env.example .env
```

| Variável            | Default      | Descrição                          |
|---------------------|--------------|------------------------------------|
| `POSTGRES_USER`     | `tcc`        | Usuário do banco                   |
| `POSTGRES_PASSWORD` | `tcc`        | Senha do usuário                   |
| `POSTGRES_DB`       | `projectTCC` | Nome do banco criado no boot       |
| `POSTGRES_HOST`     | `localhost`  | Host usado pela aplicação/Alembic  |
| `POSTGRES_PORT`     | `5432`       | Porta exposta no host              |

### Comandos

```bash
# Subir o container em segundo plano
docker compose up -d

# Ver status e health do container
docker compose ps

# Acompanhar os logs
docker compose logs -f db

# Verificar se o banco está aceitando conexões
docker compose exec db pg_isready -U tcc -d projectTCC

# Abrir um shell psql no banco
docker compose exec db psql -U tcc -d projectTCC

# Parar o container (os dados persistem no volume)
docker compose down

# Parar e apagar os dados (remove o volume)
docker compose down -v
```

### Conexão

```
postgresql://tcc:tcc@localhost:5432/projectTCC
```

> Se a porta `5432` já estiver em uso no host, defina outra em `POSTGRES_PORT`
> no `.env` (ex.: `5434`) e ajuste a string de conexão de acordo.

## Migrations (Alembic)

Dependências: `pip install -r requirements.txt`.

A camada de acesso fica em `db/` (`db/database.py` monta a URL a partir das
env vars; `db/models.py` tem os modelos). As migrations ficam em
`alembic/versions/`.

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Reverter a última migration
alembic downgrade -1

# Reverter tudo
alembic downgrade base

# Ver a revisão atual do banco / histórico
alembic current
alembic history

# Gerar uma nova migration a partir das mudanças nos modelos
alembic revision --autogenerate -m "descricao da mudanca"
```

### Tabela `questao`

`id` (uuid, PK, `gen_random_uuid()`), `question_id` (único, ex.: `Q3761251`),
campos da questão (`subject`, `topics`, `year`, `exam_board`, `organization`,
`exam_title`, `exam_url`, `associated_text`, `enunciation`, `alternatives` jsonb),
`excluido` (boolean, default `false`, para soft delete) e `created_at` /
`updated_at`.

## Execução do scraper

```bash
alembic upgrade head   # garante a tabela criada
python main.py
```

O `main.py` grava os resultados em **`questions.json`** (para comparação) e faz
**upsert** na tabela `questao`, com deduplicação por `question_id`:

- questão nova → inserida;
- `question_id` já existente → os campos são atualizados e `updated_at` avança
  (`created_at` e `excluido` são preservados — reprocessar não "ressuscita" uma
  questão marcada como `excluido = true`).

Rodar o script quantas vezes quiser não cria linhas duplicadas.
