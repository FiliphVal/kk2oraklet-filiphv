import requests
from app.chain.runnable import Runnable
from app.schemas import PromptInput, PromptOutput, LLMOutput, FinalResponse
from transformers import pipeline

class PromptBuilder(Runnable[PromptInput, PromptOutput]):
    def invoke(self, data: PromptInput) -> PromptOutput:

        ## slår ihop statistiken och frågan till en textsträng
        prompt_text = f"""You are a data expert. Here is the statistics from our dataset:
        {data.stats}
        User question: {data.question}
        Answer the question briefly and concisely in English:"""
    
        ## skicka vidare texten i rätt mall
        return PromptOutput(prompt=prompt_text)
    
generator = pipeline(
        "text-generation",
        model="Qwen/Qwen2.5-0.5B-Instruct",
        trust_remote_code=True
    )
class LLMRunner(Runnable[PromptOutput, LLMOutput]):

    def invoke(self, data: PromptOutput) -> LLMOutput:

        message = [
            {"role": "user", "content": data.prompt}
        ]

        result = generator(
            message,
            max_new_tokens=50,
            temperature=0.1,
            do_sample=True
        )


        ## -1 tar bort prompten från ai svaret
        raw_text = result[0]["generated_text"][-1]["content"]

        return LLMOutput(raw_text=raw_text)
    
class ResponseParser(Runnable[LLMOutput, FinalResponse]):
    ## kommer ihåg vad användaren frågade i början
    question: str 


    def invoke(self, data: LLMOutput) -> FinalResponse:
        ## paketerar ihop slutresultat till användaren
        return FinalResponse(
            question=self.question,
            answer=data.raw_text.strip()
        )
