from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from libs.pandascore.pandascore_libs import get_active_match_dict
from libs.prompt_template import active_games_template

active_games = get_active_match_dict()
model = OllamaLLM(model="llama3.1")

active_games_prompt = ChatPromptTemplate.from_template(
    active_games_template
)

chain = active_games_prompt | model

response = chain.invoke({"games_dict": active_games})
print(response)
