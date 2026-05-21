from langchain_ollama import ChatOllama
from app.config import get_settings

_settings = get_settings()


def get_llm():
    return ChatOllama(model=_settings.local_llm)  # type: ignore
