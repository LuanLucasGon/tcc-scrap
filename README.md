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

A infraestrutura de acesso fica em `infra/` (`infra/database.py` monta a URL a
partir das env vars e expõe `engine` / `SessionLocal` / `Base`). Cada entidade
do domínio tem seu próprio pacote (singular, com o nome da tabela) seguindo
Clean Architecture:

```
infra/database.py                       engine, SessionLocal, Base

subject/normalization.py                normalize_subject_name(raw) -> str  (pura)
subject/entity/subject.py               modelo SQLAlchemy Subject (tabela "subject")
subject/dtos/subject_dto.py             DTO de saída
subject/repository/                     porta + SubjectRepository

question/entity/question.py             modelo Question (tabela "question")
question/dtos/question_scraped_dto.py   DTO de entrada (o que o scraper produz)
question/dtos/question_dto.py           DTO de saída (subject_id + subject_name)
question/repository/                    porta + QuestionRepository
```

Os repositórios estendem o *service layer* do `advanced-alchemy` (o mais próximo
de Spring Data / Hibernate em Python): herdam CRUD e consultas prontos e recebem
a `Session` de quem chama.

`QuestionRepository.upsert_many` resolve a matéria de cada questão: normaliza o
nome (`"Matemática"` → `MATEMATICA`), busca/cria a linha em `subject` via
`SubjectRepository` e grava a FK `question.subject_id`. Questão sem matéria →
`ValueError`. As migrations ficam em `alembic/versions/`.

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

### Tabelas `subject` e `question`

`subject`: `id` (uuid, PK, `gen_random_uuid()`), `name` (varchar **único** — só a
forma normalizada, ex.: `MATEMATICA`), `active` (boolean, default `true`),
`deleted` (boolean, default `false`, soft delete), `created_at` / `updated_at`.

`question`: `id` (uuid, PK), `question_id` (único, ex.: `Q3761251`),
`subject_id` (uuid, **FK NOT NULL** → `subject.id`), `topics` (array), `year`,
`exam_board`, `organization`, `exam_title`, `exam_url`, `associated_text`,
`enunciation`, `alternatives` (jsonb), `deleted` (boolean, default `false`,
soft delete), `created_at` / `updated_at`.

## Execução do scraper

```bash
alembic upgrade head   # garante a tabela criada
python main.py
```

O `main.py` grava os resultados em **`questions.json`** (para comparação) e faz
**upsert** na tabela `question`, com deduplicação por `question_id` (e cria/reusa
as `subject` conforme necessário):

- questão nova → inserida;
- `question_id` já existente → os campos são atualizados e `updated_at` avança
  (`created_at` e `deleted` são preservados — reprocessar não "ressuscita" uma
  questão marcada como `deleted = true`).

Rodar o script quantas vezes quiser não cria linhas duplicadas.

## Testes

```bash
pytest
```

Os testes de unidade (normalização de matéria, DTOs, contagem de upsert) rodam
sem banco. Os testes de integração dos repositórios precisam do Postgres no ar
(`docker compose up -d db`) — sem ele, são automaticamente pulados (`skip`).
