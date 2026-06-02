from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():

    ## Teestar så att det funkar att köra health checken
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ask_ai_without_dataset():

    ## Testar om det går att fråga AIn en fråga utan att ladda upp ett dataset och förväntar oss 400 status koden.
    payload = {"question": "What is this dataset about?"}
    response = client.post("/ai/ask", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Ladda upp ett dataset först"

def test_get_stats_without_dataset():

    ## Testar om det går att få stats (df.describe()) utan att ha laddat upp ett dataset
    response = client.get("/data/stats")
    assert response.status_code == 404
    assert response.json()["detail"] == "Finns inget dataset uppladdat"

def test_upload_file_with_wrong_format():
    
    ## Testar om det går att ladda upp ett annat filformat än CSV, i detta fall en txt fil
    payload = {
        "file": "notes.txt"
    }
    response = client.post("/data/upload", files=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Du måste ladda upp en CSV fil"