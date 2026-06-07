from app.chain.steps import PromptBuilder
from app.schemas import PromptInput

def test_prompt_builder():
    builder = PromptBuilder()
    fejk_data = PromptInput(question="What sport is this?", stats={"Player": 10})
    resultat = builder.invoke(fejk_data)
    assert "[START] What sport is this? [END]" in resultat.prompt
    assert "Player" in resultat.prompt