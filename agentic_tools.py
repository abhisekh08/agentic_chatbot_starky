from dotenv import load_dotenv
from langchain.tools import tool
import yfinance as yf
from langchain_groq import ChatGroq
import requests
from bs4 import BeautifulSoup
from langchain_core.messages import SystemMessage
from tavily import TavilyClient
from config import credentials


load_dotenv()

# setup groq
GROQ_API_KEY = credentials["GROQ_API_KEY"]
APP_NAME = credentials["APP_NAME"]
tavily_api_key = credentials["TAVILY_API_KEY"]

# create llm
llm_base = ChatGroq(model_name=credentials["MODEL_NAME"],
                    temperature=0.1,
                    groq_api_key=GROQ_API_KEY,
                    reasoning_format="parsed")

def summarize_chunk(input_text):
    msgs = [SystemMessage(f"""summarize the INPUT text to the most accurate and meaningful form under 5 bullet points, focus on key events, exclude trivia.stick point to point.
                            INPUT: {input_text}""")]

    return llm_base.invoke(msgs).content

def chunk_text(text, max_words=1024):
    """Split large text into chunks by word count (Groq handles text, not tokens)."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i+max_words]))
    return chunks

def summarize_large_text(input_text):
    chunks = chunk_text(input_text)

    partial_summaries = []
    for i, chunk in enumerate(chunks):
        summary = summarize_chunk(chunk)
        print(summary)
        partial_summaries.append(summary)

    combined_summary_input = " ".join(partial_summaries)
    final_summary = summarize_chunk(combined_summary_input)
    return final_summary

def extract_text_from_website(url: str) -> str:
    """
    Fetch and extract readable text content from a webpage.

    Args:
        url (str): The webpage URL.

    Returns:
        str: Cleaned text content from the page.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # helps avoid blocking
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return f"Error fetching {url}: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove scripts, styles, metadata
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.extract()

    text = soup.get_text(separator='\n')
    # Normalize whitespace
    text = " ".join(text.split())

    return text

@tool
def search_query_from_web(query: str) -> str:
    """
    return the search-engine content about the query in JSON from websites.
    Args:
        query (str): search string to search in the web for results

    Returns:
        str: Cleaned text content from web about the query.
    """
    try:
        client = TavilyClient(api_key=tavily_api_key)
        output_body = ""
        resp = client.search(query,search_depth="advanced",include_answer = True,include_images=False, max_results=2)
        for src_content_ind in resp["results"]:
            src_url = src_content_ind["url"]
            if 'wikipedia' in src_url: # skipping wiki content to avoid token limit in process
                continue
            src_content = extract_text_from_website(src_url)

            output_body = output_body + f"""
            CONTENT: {src_content}
            SOURCE: {src_url} 
            
            \n\n
            """

        # summarized output content
        return summarize_large_text(output_body)

    except Exception as e:
        return f"Error caused in fetching data due to : {e}"

@tool
def get_stock_info(ticker: str) -> dict:
    """Fetch basic stock information for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {"symbol": info.get("symbol", ticker),
                "shortName": info.get("shortName", "N/A"),
                "currentPrice": info.get("currentPrice", "N/A"),
                "marketCap": info.get("marketCap", "N/A"),
                "sector": info.get("sector", "N/A"),
                "Rating": info.get('averageAnalystRating', "N/A")
                }
    except Exception as e:
        return {"error": str(e)}
