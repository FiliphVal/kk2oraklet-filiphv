from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import io
import os
from dotenv import load_dotenv
from app.chain.pipeline import oracle_chain

from app.schemas import QuestionInput, PromptInput, FinalResponse
from app.chain.steps import PromptBuilder, LLMRunner, ResponseParser

load_dotenv()

app = FastAPI(title="KK2 - Oraklet")
current_dataset = None

HF_API_KEY = os.getenv("HF_API_KEY")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/data/upload")
async def upload_file(file: UploadFile = File(...)):
    global current_dataset
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Du måste ladda upp en CSV fil")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        current_dataset = df
        dtypes_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
        return {
            "message": "Uppladdning genomförd",
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": dtypes_dict
        }

    except:
        raise HTTPException(status_code=400, detail=f"Krasch vid inläsning av CSV filen")
    

@app.get("/data/stats")
def get_stats():
    global current_dataset
    if current_dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Finns inget dataset uppladdat"
        )
    
    return current_dataset.describe().fillna(None).to_dict()


@app.post("/ai/ask", response_model=FinalResponse)
def ask_oracle(payload: QuestionInput):
    global current_dataset

    if current_dataset is None:
        raise HTTPException(status_code=400, detail="Ladda upp ett dataset först")
    
    stats_dict = current_dataset.describe(include="all").fillna(None).to_dict()

    
    chain = oracle_chain(question=payload.question)

    try:
        input_data = PromptInput(question=payload.question, stats=stats_dict)
        resultat = chain.invoke(input_data)
        return resultat
    except Exception as e:
        print(f"!!! DETTA ÄR DET RIKTIGA FELET: {str(e)}")
        raise HTTPException(status_code=500, detail="AI kraschade")