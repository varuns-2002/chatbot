from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup  # Ensure BeautifulSoup is imported for scraping

app = Flask(__name__)

# API Keys (Replace with your actual keys)
SERPAPI_KEY = "08f0afd6411cdc029c0025538b2956476ae19da6db7545c6811fea35f0cf15d6"
BLACKBOX_API_KEY = "7ebc3c5ae2msh87aa52832a6f16dp1ff018jsnfc8894938279"  # Replace with your actual Blackbox API key

def search_web(query):
    """Fetches top search results from SerpAPI"""
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Extract top search results
    search_results = []
    if "organic_results" in data:
        for result in data["organic_results"][:3]:  # Get top 3 results
            search_results.append(f"{result.get('title')}: {result.get('snippet')} (Link: {result.get('link')})")
    
    return "\n".join(search_results) if search_results else "No relevant search results found."

def summarize_content(content):
    """Uses Blackbox API to summarize the search results"""
    url = "https://blackbox.p.rapidapi.com/v1/1.1.1.1"  # Replace with the actual Blackbox API endpoint
    headers = {
        "Authorization": f"Bearer {BLACKBOX_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "content": content,
        "summary_length": "short"  # Adjust as needed
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("summary", "No summary available.")
    else:
        return "Failed to summarize content."

def scrape_documentation(url):
    """Scrapes documentation from the given URL"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    sections = []
    
    # Find all headings (adjust the tag as needed, e.g., 'h1', 'h2', etc.)
    for heading in soup.find_all("h2"):  # Change 'h2' to the appropriate heading tag
        # Get the heading text
        heading_text = heading.get_text()
        
        # Find the next paragraph after the heading
        paragraph = heading.find_next("p")
        
        # Check if paragraph exists before calling get_text()
        if paragraph:
            paragraph_text = paragraph.get_text()
        else:
            paragraph_text = "No content available."
        
        # Combine heading and paragraph
        sections.append(f"{heading_text}: {paragraph_text}")
    
    return sections

def index_documentation(cdp_name, url):
    """Indexes documentation for a given CDP"""
    sections = scrape_documentation(url)
    # Add your indexing logic here (e.g., store in a database or search engine)
    print(f"Indexed {len(sections)} sections for {cdp_name}.")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    search_results = search_web(question)
    print(search_results)
    chatbot_response = summarize_content(search_results)
    print(chatbot_response)
    return jsonify({"answer": chatbot_response})

if __name__ == '__main__':
    # Example usage of the documentation scraping and indexing
    cdp_name = "Example CDP"
    url = "https://example.com/documentation"  # Replace with the actual documentation URL
    index_documentation(cdp_name, url)
    
    app.run(debug=True)