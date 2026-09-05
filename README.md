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
shared/normalization.py                 normalize_name(raw) -> str  (pura; usada
                                         por subject/ e topic/)

subject/entity/subject.py               modelo SQLAlchemy Subject (tabela "subject")
subject/dtos/subject_dto.py             DTO de saída
subject/repository/                     porta + SubjectRepository

topic/entity/topic.py                   modelo Topic (tabela "topic", FK -> subject)
topic/dtos/topic_dto.py                 DTO de saída
topic/repository/                       porta + TopicRepository

question/entity/question.py             modelo Question (tabela "question")
question/dtos/question_scraped_dto.py   DTO de entrada (o que o scraper produz)
question/dtos/question_dto.py           DTO de saída (subject_id + subject_name)
question/repository/                    porta + QuestionRepository
```

Os repositórios estendem o *service layer* do `advanced-alchemy` (o mais próximo
de Spring Data / Hibernate em Python): herdam CRUD e consultas prontos e recebem
a `Session` de quem chama. Nenhum repositório resolve entidade de outro
repositório (ex.: `QuestionRepository` não cria `Subject`/`Topic`) — essa
orquestração é feita por `main.persist_questions`, preparação para um futuro
Service.

`main.persist_questions` resolve a matéria de cada questão (normaliza o nome,
`"Matemática"` → `MATEMATICA`, busca/cria via `SubjectRepository`), resolve os
tópicos de cada questão (`dto.topics`) via `TopicRepository` — vinculados ao
`subject_id` já resolvido, únicos **por matéria** e não globalmente — e só então
chama `QuestionRepository.upsert_many` com o `subject_id` de cada questão já
pronto, gravando a FK `question.subject_id`. Questão sem matéria → `ValueError`.
As migrations ficam em `alembic/versions/`.

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

### Tabelas `subject`, `topic` e `question`

`subject`: `id` (uuid, PK, `gen_random_uuid()`), `name` (varchar **único** — só a
forma normalizada, ex.: `MATEMATICA`), `active` (boolean, default `true`),
`deleted` (boolean, default `false`, soft delete), `created_at` / `updated_at`.

`topic`: `id` (uuid, PK), `subject_id` (uuid, **FK NOT NULL** → `subject.id`),
`name` (varchar, forma normalizada; **único por subject** — `UNIQUE(subject_id,
name)`, não globalmente, então o mesmo nome pode existir em matérias diferentes),
`active` (boolean, default `true`), `deleted` (boolean, default `false`, soft
delete), `created_at` / `updated_at`.

`question`: `id` (uuid, PK), `question_id` (único, ex.: `Q3761251`),
`subject_id` (uuid, **FK NOT NULL** → `subject.id`), `topics` (array — nomes
crus do scraper, sem FK para `topic`), `year`, `exam_board`, `organization`,
`exam_title`, `exam_url`, `associated_text`, `enunciation`, `alternatives`
(jsonb), `correct_answer` (letra do gabarito, ex. `A`; `None` se a página não
trouxer gabarito, ou `X` para questão anulada), `deleted` (boolean, default
`false`, soft delete), `created_at` / `updated_at`.

O gabarito vem do bloco "Respostas" no rodapé da própria página de listagem
(`numero: letra`). `main.extract_answers_from_html` extrai esse bloco e
`main.correlate_answers_by_order` associa cada questão à sua letra **pela
ordem relativa** em que aparecem na página (não pelo valor numérico — o
gabarito de uma página não necessariamente começa em 1). A letra não é
restrita a A-E: questão anulada aparece como `X`, e descartá-la desalinharia
a correlação das questões seguintes na mesma página.

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
