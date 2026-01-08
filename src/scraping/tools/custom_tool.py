from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."



import requests
from bs4 import BeautifulSoup
import json
from crewai.tools import tool
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime

# -------------------------
# Helpers
# -------------------------

def fetch_data(
    base_url: str,
    params: Optional[Dict] = None,
    page_param: str = "page",
    per_page_key: Optional[str] = None,
    per_page_value: Optional[str] = None,
    stop_selector: Optional[str] = None,
    max_pages: int = 50,
) -> List[BeautifulSoup]:
    
    """
    Fetches and parses paginated web pages until no more data is available.
    
    Automatically iterates through pages by incrementing a page parameter,
    stopping when a specified CSS selector is no longer found on the page.
    
    Args:
        base_url: The target website URL
        params: Query parameters dict (default: {})
        page_param: URL parameter name for pagination (default: 'page')
        per_page_key: Parameter name for items per page (optional)
        per_page_value: Value for items per page (optional)
        stop_selector: CSS selector to check for content; stops when not found
        
    Returns:
        List of BeautifulSoup objects, one for each fetched page
        
    Example:
        soups = fetch_data(
            "https://example.com/data",
            params={'category': 'sports'},
            page_param='page',
            stop_selector='div.results'
        )
    """
    params = dict(params or {})  # copy to avoid mutating caller
    if per_page_key and per_page_value:
        params[per_page_key] = per_page_value

    soups: List[BeautifulSoup] = []
    page = 1

    while page <= max_pages:
        params[page_param] = page
        try:
            resp = requests.get(base_url, params=params, timeout=20)
        except Exception as e:
            # network error -> stop and return what we have
            print(f"[fetch_data] network error page={page}: {e}")
            break

        if resp.status_code != 200:
            print(f"[fetch_data] non-200 status ({resp.status_code}) for page={page}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        soups.append(soup)

        # If stop_selector provided, stop when it is NOT found (no more results)
        if stop_selector:
            # If the selector is not string, ignore it (defensive)
            if isinstance(stop_selector, str):
                if not soup.select_one(stop_selector):
                    # no content found → stop (we keep the page we just fetched only if you want, adjust behavior)
                    break
            else:
                # defensive: if stop_selector is not a str, stop to avoid unhashable/dict issues
                print("[fetch_data] stop_selector is not a string — stopping to avoid errors.")
                break

        page += 1

    return soups


def extract_data(soup, selectors: Dict[str, str]) -> List[Dict]:
    """
    Extracts structured data from HTML using CSS selectors.
    
    Parses a BeautifulSoup object and extracts text content based on a 
    selector mapping. Supports repeating elements via a 'container' selector
    or single-page extraction if no container is specified.
    
    Args:
        soup: BeautifulSoup object containing parsed HTML
        selectors: Dict mapping field names to CSS selectors
                   Special key 'container': selector for repeating elements
                   
    Returns:
        List of dicts, each containing extracted field data
        
    Example:
        selectors = {
            "container": "div.article",
            "title": "h2.article-title",
            "date": "span.date",
            "author": "div.author-name"
        }
        data = extract_data(soup, selectors)
        # Returns: [{"title": "...", "date": "...", "author": "..."}, ...]
    """
   
    records: List[Dict] = []
   
    container_sel = selectors.get("container")
    if container_sel:
        containers = soup.select(container_sel)
    else:
         #If no container is provided, treat the whole soup as one container
        containers = [soup]
    

   
    for cont in containers:
        record: Dict = {}
        for key, sel in selectors.items():
            if key == "container":
                continue
            # defensive: ensure selector is string
            if not isinstance(sel, str):
                record[key] = None
                continue
            el = cont.select_one(sel)
            record[key] = el.get_text(strip=True) if el else None

        # add metadata (safe primitives)
        record["_source_url"] = getattr(soup, "url", None) or None
        record["_extraction_timestamp"] = datetime.utcnow().isoformat() + "Z"
        records.append(record)

    return  records


# -------------------------
# Tool
# -------------------------

@tool("alll")
def alll(base_url: str, params: Optional[Dict] = None, selectors: Optional[Dict] = None) -> List[Dict]:
    """
        Scrapes paginated web data and extracts structured information.
        
        Fetches multiple pages from a base URL with query parameters, then extracts
        data from each page using CSS selectors. Aggregates all extracted data into
        a single list.
        
        Args:
            base_url: The target website URL to scrape
            params: Query parameters for the request (e.g., search filters)
            selectors: CSS selectors mapping field names to HTML elements
            
        Returns:
            A list of dictionaries containing extracted data from all pages
            
        Example:
            base_url = "https://www.scrapethissite.com/pages/forms/"
            params = {'q': 'sharks'}
            selectors = {
                "container": "tr.team",
                "team_name": "td.name",
                "year": "td.year"
            }
            results = alll(base_url, params, selectors)
    """
    try:
        if selectors is None or not isinstance(selectors, dict):
            return [{"error": "selectors must be provided as a dict of CSS selectors"}]

        # Important: for fetch_data we must pass a string stop_selector (not the whole dict)
        stop_selector = selectors.get("container")  # this must be a string or None

        soups = fetch_data(base_url, params=params, stop_selector=stop_selector)

        all_records: List[Dict] = []
        for soup in soups:
            records = extract_data(soup, selectors)
            all_records.extend(records)

        return all_records

    except Exception as e:
        # Always return a JSON-serializable error structure from tools
        return [{"error": f"unexpected error in alll: {str(e)}"}]




