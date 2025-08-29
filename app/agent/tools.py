from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

api_arxiv_wrapper = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
arxiv = ArxivQueryRun(api_wrapper=api_arxiv_wrapper, description="Query arxiv papers")

# Initialize Wikipedia
api_wikipedia_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wiki = WikipediaQueryRun(api_wrapper=api_wikipedia_wrapper)

# Initialize Tavily
tavily = TavilySearch(max_results=2)

tools = [arxiv, wiki, tavily]
