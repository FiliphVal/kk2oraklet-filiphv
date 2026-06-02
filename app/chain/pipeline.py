from transformers import pipeline
from app.chain.steps import PromptBuilder, LLMRunner, ResponseParser

generator = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",
    trust_remote_code=True
)

def oracle_chain(question:str):
    builder = PromptBuilder()
    runner = LLMRunner(generator=generator)
    parser = ResponseParser(question=question)

    return builder | runner | parser