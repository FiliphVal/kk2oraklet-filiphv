from fastapi import FastAPI

app = FastAPI(title="KK2 - Oraklet")


@app.get("/health")
def health_check():
    """Verifierar att API:et är vid liv."""
    return {"status": "ok"}