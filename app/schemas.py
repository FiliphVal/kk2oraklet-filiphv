from pydantic import BaseModel
from typing import Dict, Any

class QuestionInput(BaseModel):
    question: str


class PromptInput(BaseModel):
    question: str
    stats: Dict[str, Any]

class PromptOutput(BaseModel):
    prompt: str

class LLMOutput(BaseModel):
    raw_text: str

class FinalResponse(BaseModel):
    question: str
    answer: str
    model: str = "HuggingFaceTB/SmolLM2-135M-Instruct"