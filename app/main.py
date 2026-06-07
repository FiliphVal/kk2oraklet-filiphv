from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import io
import os
from dotenv import load_dotenv
from app.chain.pipeline import oracle_chain
import logging
from app.schemas import QuestionInput, PromptInput, FinalResponse
from app.chain.steps import PromptBuilder, LLMRunner, ResponseParser

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="KK2 - Oraklet")
current_dataset = None

HF_API_KEY = os.getenv("HF_API_KEY")
MAX_FILE_SIZE = 10 * 1024 * 1024 ## spärr på 10mb max 

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/data/upload")
async def upload_file(file: UploadFile = File(...)):
    global current_dataset
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Du måste ladda upp en CSV fil")
    
    if file.size and file.size > MAX_FILE_SIZE:
        logger.warning(f"Filen {file.filename} var för stor.")
        raise HTTPException(status_code=400, detail="Filen är för stor. Max 10 MB tillåtet.")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        current_dataset = df
        dtypes_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
        logger.info("En ny CSV fil laddades upp framgångsrikt.")
        return {
            "message": "Uppladdning genomförd",
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": dtypes_dict
        }

    except Exception as e:
        logger.error(f"Krasch vid inläsning av CSV filen: {str(e)}")
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
        logger.info("AI genererade ett svar utan problem.")
        return resultat
    except Exception as e:
        logger.error(f"AI kraschade: {str(e)}")
        raise HTTPException(status_code=500, detail="AI kraschade")