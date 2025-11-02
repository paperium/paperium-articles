# app.py
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Path, HTTPException
from slugify import slugify

API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise ValueError("C_SHARP_API_KEY environment variable not set!")

# --- FASTAPI SETUP ---
app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
PAGE_SIZE = 50 # Must match the C# API's default page size

def create_slug(title: str) -> str:
    """
    Creates a URL-friendly slug from a given title.

    It handles spaces, punctuation, mixed case, and standardizes it 
    for use in URLs. For example, "The C# API & Python Renderer!" 
    becomes "the-c-api-python-renderer".
    """
    if not title:
        return ""
    
    # Use the slugify function for powerful and comprehensive slug generation.
    # defaults: lower=True, separator='-', safe_chars=''
    return slugify(title)
def extract_first_author(author_string: str) -> str:
    """
    Extracts the first part of the string before the first comma.
    If no comma exists, the full string is returned.
    
    Args:
        author_string: The string containing one or more authors.

    Returns:
        The name of the first author or the original string.
    """
    if not author_string:
        return ""
    
    # The split() method splits the string based on the comma, 
    # and the maxsplit=1 argument ensures it stops after the first split.
    # We take the first element [0] from the resulting list and use strip() 
    # to remove any leading/trailing whitespace.
    first_author = author_string.split(',', maxsplit=1)[0].strip()
    
    return first_author

async def fetch_articles(page: int, search: str | None = None):
    """Calls the secure C# API to get paginated article data."""
    try:
        params = {
            "page": page           
        }
        
        # 2. ⭐ Conditionally add the search term to parameters ⭐
        if search:
            params["search"] = search

        async with httpx.AsyncClient(verify=True) as client:
            response = await client.get(
                API_BASE_URL + "/GetArticles",
               params=params,
                headers={"X-Renderer-Key": API_KEY} # Pass the API Key
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# --- ROUTING AND RENDERING ---

@app.get("/", response_class=HTMLResponse)
@app.get("/GetArticles/{page}", response_class=HTMLResponse)
async def serve_article_list(request: Request, page: int = 1,search: str | None = None):
    
    data = await fetch_articles(page, search=search)
    
    if data is None or not data.get("data"):
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Could not load article data."}, status_code=500
        )

    for article in data['data']:
        # Assuming the title field is 'title'
        article['slug'] = create_slug(article.get('title', ''))
        full_author_name = article.get('author', '') # Assuming the full string is in 'authorName'
        article['shortAuthorName'] = extract_first_author(full_author_name)

        # Calculate pagination links for the template
        total_pages = data['totalPages']
        current_page = data['currentPage']
    
    # Create the context object for the Jinja2 template
    context = {
        "request": request,
        "articles": data['data'],
        "current_page": current_page,
        "total_pages": total_pages,
        "page_size": PAGE_SIZE,
        "search_term": search
    }
    
    return templates.TemplateResponse("articles_template.html", context)

# app.py

# ... (Existing imports like httpx, os, API_BASE_URL, API_KEY) ...

async def fetch_article_by_id(article_id: int):
    """Calls the secure C# API to get a single article by ID using a query parameter."""
    try:
        # 1. Base URL is used without the ID path segment (e.g., http://api/articles)
        # The endpoint for fetching a single article is often the same as the list endpoint.
        article_url = API_BASE_URL + "/GetArticleByID"
        
        # 2. ⭐ Pass the ID as a query parameter in the 'params' dictionary ⭐
        params = {"id": article_id}
        
        async with httpx.AsyncClient(verify=True) as client: 
            response = await client.get(
                article_url,
                params=params, # Pass the ID here: ?id=123
                headers={"X-Renderer-Key": API_KEY}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"API HTTP Error: {e.response.status_code} - Failed to fetch article {article_id}.")
        return None
    except Exception as e:
        print(f"Request failed unexpectedly for article {article_id}: {e}")
        return None
# app.py

# The route remains the same to support the SEO-friendly URL: /article/{article_id}/{slug}
@app.get("/article/{article_id}/{slug}", response_class=HTMLResponse)
async def serve_article_detail(
    request: Request, 
    article_id: int = Path(..., description="The ID of the article"),
    slug: str = Path(..., description="The SEO-friendly slug")
):
    # 1. Fetch the data using the updated function
    # The ID extracted from the path is passed to the function, 
    # which now sends it as a query parameter to C#
    article = await fetch_article_by_id(article_id)
    article = article['D']
   
    if article is None:
        # Use HTTPException 404 since the specific resource wasn't found
        raise HTTPException(status_code=404, detail="Article not found or API call failed")

    # 2. Check slug for SEO redirect (Best Practice)
    # The server should respond with the correct slug if the user used a bad URL.
    expected_slug = create_slug(article.get('Title', ''))
    if slug != expected_slug:
        # Optional: Redirect to the correct URL with the proper slug
        # You'd typically use a RedirectResponse, but for simplicity, we'll proceed
        # print(f"Warning: Incorrect slug used. Expected: {expected_slug}") 
        pass 

    # 3. Create context and render
    context = {
        "request": request,
        "article": article,
        "short_author": extract_first_author(article.get('Authors', '')),
        
        # Assuming you will reuse the extract_first_author function
    }

    return templates.TemplateResponse("article_detail.html", context)
    
 