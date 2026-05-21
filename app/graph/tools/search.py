from langchain_tavily import TavilySearch

_tavily = TavilySearch(max_results=4)

async def search_web(query: str) -> list[dict]:
    """Search web for the given query."""
    result = await _tavily.ainvoke({"query": query})
    return result["results"]
