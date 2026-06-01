import requests
from app.chain.runnable import Runnable
from app.schemas import PromptInput, PromptOutput, LLMOutput, FinalResponse

class PromptBuilder(Runnable[PromptInput, PromptOutput]):
    def invoke(self, data: PromptInput) -> PromptOutput:

        ## slår ihop statistiken och frågan till en textsträng
        prompt_text = f"""Du är en dataexpert. Här är statistik från vårt dataset:
            {data.stats}
            Användarfråga: {data.question}
            Svara snyggt och kortfattat på svenska."""
    
        ## skicka vidare texten i rätt mall
        return PromptOutput(prompt=prompt_text)
    
class LLMRunner(Runnable[PromptOutput, LLMOutput]):
    api_key: str ## hämtar vi från env sen
    api_link: str = "https://api-inference.huggingface.co/models/HuggingFaceTB/SmolLM2-135M-Instruct"
    
    def invoke(self, data: PromptOutput) -> LLMOutput:
        headers = {"Authorization": f"Bearer {self.api_key}"}

        ## paketet med inställningar vi skickar vidare till ai modellen
        payload = {
            "inputs": data.prompt,
            "parameters": {"max_new_tokens": 300, "temperature": 0.2}
        }

        ## skickar paketet, länken och vår nyckel
        response = requests.post(self.api_link, headers=headers, json=payload)

        ## avbryter om vi inte får koden 200 (att det lyckas)
        if response.status_code != 200:
            raise Exception(f"API Felkod {response.status_code}")
        
        result = response.json()
        ## plocka ut råa texten som ain genererade
        raw_text = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
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
