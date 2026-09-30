from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Verifica se o processo da API está de pé (não checa o banco)."""
    return {"status": "ok"}
