from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import io

app = FastAPI(title="KK2 - Oraklet")

current_dataset = None


@app.get("/health")
def health_check():
    """Verifierar att API:et är vid liv."""
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
    
    stats_df = current_dataset.describe()
    stats_df = stats_df.fillna(None)
    return stats_df.to_dict()