# tcc-scrap — Development Guidelines

Este documento contém as regras de trabalho neste repositório. Siga-as com precisão.

## Sobre o projeto

Scraper do site QConcursos para coletar questões públicas de vestibular e montar
uma base de dados aberta. Segue Clean Architecture: cada entidade de domínio tem
seu próprio pacote (singular, nome da tabela), com `infra/database.py` centralizando
`engine` / `SessionLocal` / `Base`.

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

Os repositórios estendem o *service layer* do `advanced-alchemy` (equivalente a
Spring Data/Hibernate em Python): herdam CRUD e consultas prontas e recebem a
`Session` de quem chama.

## Core Development Rules

### Package Management

- Dependências gerenciadas via `requirements.txt` (`pip install -r requirements.txt`)
- Stack: `requests`, `beautifulsoup4`, `lxml`, `playwright`, `sqlalchemy`,
  `advanced-alchemy`, `alembic`, `psycopg[binary]`, `python-dotenv`, `pytest`
- Ao adicionar dependência nova, atualize `requirements.txt` e explique o motivo no PR

### Code Quality

- Type hints obrigatórios em todo código novo
- APIs públicas (funções/classes expostas fora do pacote) precisam de docstring
- Funções pequenas e focadas — uma responsabilidade cada
- Seguir os padrões já existentes no repo (DTOs, portas de repositório, normalização) exatamente
- Line length: 88 caracteres

### Testing Requirements

- Framework: `pytest`
- Testes de unidade (normalização de matéria, DTOs, contagem de upsert) devem rodar
  **sem banco**
- Testes de integração dos repositórios precisam do Postgres no ar
  (`docker compose up -d db`); sem ele, devem ser `skip` automaticamente — nunca falhar
- Toda feature nova exige teste; todo bugfix exige teste de regressão
- Rodar `pytest` antes de abrir PR

### Code Style

- PEP 8 naming (snake_case for functions/variables)
- Class names in PascalCase
- Constants in UPPER_SNAKE_CASE
- Document with docstrings
- Use f-strings for formatting

## Development Philosophy

- Simplicity: Write simple, straightforward code
- Readability: Make code easy to understand
- Performance: Consider performance without sacrificing readability
- Maintainability: Write code that's easy to update
- Testability: Ensure code is testable
- Reusability: Create reusable components and functions
- Less Code = Less Debt: Minimize code footprint

## Coding Best Practices

- Early Returns: Use to avoid nested conditions
- Descriptive Names: Use clear variable/function names (prefix handlers with "handle")
- Constants Over Functions: Use constants where possible
- DRY Code: Don't repeat yourself
- Functional Style: Prefer functional, immutable approaches when not verbose
- Minimal Changes: Only modify code related to the task at hand
- Function Ordering: Define composing functions before their components
- TODO Comments: Mark issues in existing code with "TODO:" prefix
- Simplicity: Prioritize simplicity and readability over clever solutions
- Build Iteratively: Start with minimal functionality and verify it works before adding complexity
- Run Tests: Test your code frequently with realistic inputs and validate outputs
- Build Test Environments: Create testing environments for components that are difficult to validate directly
- Functional Code: Use functional and stateless approaches where they improve clarity
- Clean logic: Keep core logic clean and push implementation details to the edges
- File Organisation: Balance file organization with simplicity - use an appropriate number of files for the project scale

## Banco de dados (PostgreSQL via Docker)

```bash
cp .env.example .env          # ajustar variáveis se necessário
docker compose up -d          # sobe o Postgres em background
docker compose ps             # status/health do container
docker compose logs -f db     # acompanhar logs
docker compose exec db pg_isready -U tcc -d projectTCC
docker compose exec db psql -U tcc -d projectTCC
docker compose down           # para (dados persistem no volume)
docker compose down -v        # para e apaga os dados
```

Conexão: `postgresql://tcc:tcc@localhost:5432/projectTCC`
(se a porta 5432 estiver ocupada, ajustar `POSTGRES_PORT` no `.env`)

## Migrations (Alembic)

```bash
alembic upgrade head                              # aplica migrations pendentes
alembic downgrade -1                               # reverte a última
alembic downgrade base                             # reverte tudo
alembic current                                     # revisão atual
alembic history                                     # histórico
alembic revision --autogenerate -m "descricao"      # gera nova migration
```

### Tabelas

- `subject`: `id` (uuid, PK), `name` (varchar único, forma normalizada, ex. `MATEMATICA`),
  `active`, `deleted` (soft delete), `created_at` / `updated_at`
- `question`: `id` (uuid, PK), `question_id` (único, ex. `Q3761251`),
  `subject_id` (FK NOT NULL → `subject.id`), `topics` (array), `year`, `exam_board`,
  `organization`, `exam_title`, `exam_url`, `associated_text`, `enunciation`,
  `alternatives` (jsonb), `deleted` (soft delete), `created_at` / `updated_at`

`QuestionRepository.upsert_many` normaliza a matéria, busca/cria em `subject` via
`SubjectRepository` e grava a FK. Questão sem matéria → `ValueError`.

## Execução do scraper

```bash
alembic upgrade head
python main.py
```

Grava em `questions.json` (para comparação) e faz upsert em `question`, deduplicando
por `question_id`. Reexecutar não duplica nem "ressuscita" questão `deleted = true`
(`created_at` e `deleted` são preservados; só `updated_at` avança).

## Git

**Claude nunca executa comandos git neste projeto** — nenhum `git add`, `commit`,
`push`, `checkout`, `branch`, etc. Toda a parte de git (branches, commits, PRs) é
de responsabilidade exclusiva do usuário. Claude só edita arquivos de código.

## Resolução de erros

Ordem de correção: formatação → erros de tipo → lint → testes.

## Boas práticas gerais

- Seguir padrões existentes do repositório (portas/repositórios/DTOs) em vez de inventar novos
- Documentar APIs públicas
- Testar minuciosamente, incluindo casos de borda (HTML do QConcursos mudando de estrutura,
  questão sem matéria, questão já existente no banco)