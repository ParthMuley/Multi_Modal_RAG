import os
import json
import trafilatura
from bs4 import BeautifulSoup
from link_extractor import extract_links_from_pdf
from config import DATA_DIR, SCRAPED_CONTENT_DIR

# --- SETTINGS ---
# Allowed domains for recursive crawling (to stay in technical docs)
ALLOWED_DOMAINS = [
    "aws.amazon.com",
    "docs.aws.amazon.com",
    "azure.microsoft.com",
    "docs.microsoft.com"
]

def clean_url(url):
    """Simple URL cleaner."""
    return url.split("#")[0].strip("/")

def scrape_and_find_links(url, visited):
    """
    Scrapes a URL using trafilatura for quality text, 
    and BS4 to find more links for depth=1.
    """
    if url in visited:
        return None, []
    
    visited.add(url)
    print(f"Scraping: {url}...")
    
    try:
        # Use trafilatura for the MAIN content (removes menus/ads)
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None, []
            
        content = trafilatura.extract(downloaded, include_links=False, include_images=False)
        
        # Use BeautifulSoup to find NEW links for recursion
        new_links = []
        soup = BeautifulSoup(downloaded, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Normalize and check if it's an allowed domain
            if href.startswith("http") and any(dom in href for dom in ALLOWED_DOMAINS):
                new_links.append(clean_url(href))
        
        return content, list(set(new_links))
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, []

def process_recursive_ingest(max_links=20):
    """
    1. Extracts links from all PDFs in data/
    2. Scrapes them and finds additional links (Depth 1)
    3. Saves high-quality text to scraped_content/
    """
    os.makedirs(SCRAPED_CONTENT_DIR, exist_ok=True)
    
    all_start_links = set()
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
    
    for pdf in pdf_files:
        print(f"Finding links in {pdf}...")
        links = extract_links_from_pdf(os.path.join(DATA_DIR, pdf))
        for l in links:
            all_start_links.add(clean_url(l))

    visited = set()
    to_scrape = list(all_start_links)[:max_links] # Limit for MVP
    
    scraped_count = 0
    
    for url in to_scrape:
        content, sub_links = scrape_and_find_links(url, visited)
        
        if content:
            # Sanitize filename (remove ? : * " < > | )
            safe_name = "".join([c if c.isalnum() or c in "._-" else "_" for c in url.split("//")[-1]])[:100]
            with open(os.path.join(SCRAPED_CONTENT_DIR, f"{safe_name}.txt"), "w", encoding="utf-8") as f:
                f.write(f"SOURCE URL: {url}\n\n{content}")
            scraped_count += 1
            
            # Depth 1: Add a few sub-links if we haven't hit the limit
            for sl in sub_links:
                if sl not in visited and len(visited) < max_links + 10:
                    to_scrape.append(sl)

    print(f"Successfully scraped {scraped_count} high-quality documentation pages.")

if __name__ == "__main__":
    process_recursive_ingest(max_links=15)
