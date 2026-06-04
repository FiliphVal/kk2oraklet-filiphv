KK2 Oraklet En typad LLM kedja med FastAPI
Det här projektet är en REST tjänst byggd i FastAPI som kombinerar dataanalys i Pandas med en lokal AI språkmodell. Applikationen använder en egenbyggd Runnable kedja för att styra hela flödet från frågan och datan fram till det färdiga svaret.

Modellval
 Projektet körs med Qwen/Qwen2.5-0.5B-Instruct istället för SmolLLM. Detta val gjordes eftersom SmolLLM visade tydliga begränsningar när den skulle hantera rå Pandas statistik, vilket ledde till att den började loopa texten och klippa av sina svar mitt i meningar. Qwen modellen är väldigt kompakt och ligger på under 1 GB, vilket gör att den kan laddas ner snabbt och köras direkt på datorns vanliga CPU via transformers pipeline, samtidigt som den levererar mycket mer stabila och vettiga svar.

Projektstruktur
 I mappen app hittar man main.py som innehåller själva FastAPI applikationen med alla endpoints och felhanteringen. Filen schemas.py innehåller alla Pydantic modeller som sköter den starka typningen genom hela appen. Går man in i mappen chain så ligger steps.py där de isolerade stegen för promptbygget, AI exekveringen och parsern finns, och pipeline.py länkar ihop alla dessa steg med hjälp av vertical operatorn. Alla automatiska endpoints tester ligger samlade i mappen tests.

Installation och Setup
För att dra igång projektet behöver man se till att ha pakethanteraren uv installerad på sin dator.
Först klonar man repot från GitHub och hoppar in i projektmappen med terminalen. Därefter kör man kommandot uv sync för att automatiskt synka alla beroenden och skapa den virtuella miljön. När det är klart startar man upp servern genom att köra kommandot uv run uvicorn app.main:app --reload.
Så fort uvicorn har dragit igång och rullar så hittar manSwagger UI på den vanliga lokala adressen http://127.0.0.1:8000/docs där man kan testa alla funktioner live i webbläsaren.
Köra Tester 

Tesrena är byggd med pytest och verifierar att appen fungerar samt testar viktiga edge cases för robusthet, som till exempel att appen nekar en användare att ställa frågor om inget dataset har laddats upp än. Man kör enkelt igenom alla tester i terminalen med kommandot uv run pytest app/tests/ -v.

Exempel på hur man gör anrop 

Det går bra att köra appen direkt via terminalen med vanliga curl kommandon om man inte vill använda Swagger
För en healthcontrol kör man curl -X GET http://127.0.0.1:8000/health. Om man vill ladda upp sitt dataset skickar man med filen genom att skriva :
curl -X POST http://127.0.0.1:8000/data/upload -F file=@ditt_dataset.csv.
 När filen väl är uppladdad kan man ställa sin fråga till AI modellen genom att skicka en json payload med kommandot
 curl -X POST http://127.0.0.1:8000/ai/ask -H Content-Type: application/json -d {"question": "What does this dataset represent?"}.

