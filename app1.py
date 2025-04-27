# Import required libraries
from serpapi import GoogleSearch               # For performing Google searches via SerpAPI
from bs4 import BeautifulSoup                  # For parsing HTML content
import requests                                # To fetch web page content
import re                                      # Regular expressions for pattern matching
from fuzzywuzzy import fuzz                    # To deduplicate similar sentences
from transformers import pipeline              # For transformer-based summarization
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


    
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        api_key = "dc88c7575c985ca8924d7d3d8bb76a2ea8cde77c382bfa4688af0b08e21f19ae"  # Replace with your SerpAPI key
        query = "Jawaharlal Nehru"
        user_message = request.form.get("message")
        agent = WebResearchAgent(api_key)
        output = agent.run(user_message)
        

        return render_template("index.html", user_message=user_message, output=output)

    return render_template("index.html")



# Initialize the Hugging Face summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Step 1: WebSearcher - Responsible for finding relevant URLs using Google Search via SerpAPI
class WebSearcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query, num_results=3):
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        links = []
        for result in results.get("organic_results", [])[:num_results]:
            link = result.get("link")
            if link:
                links.append(link)
        return links

# Step 2: WebScraper - Fetches and extracts raw text (paragraphs) from a given URL
class WebScraper:
    def scrape(self, url):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)  # Pass the options here
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            driver.quit()
            return text
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""

# Step 3: ContentAnalyzer - Cleans and summarizes content using BART
class ContentAnalyzer:
    def analyze(self, text, query):
        boilerplate_patterns = [
            r'your name', r'e-?mail', r'phone', r'contact us', r'cookies', r'privacy policy',
            r'terms of service', r'subscribe', r'sign up', r'login', r'username', r'password'
        ]
        
        cleaned_lines = []
        for line in text.splitlines():
            if not any(re.search(pattern, line, re.IGNORECASE) for pattern in boilerplate_patterns):
                cleaned_lines.append(line.strip())
        cleaned_text = " ".join(cleaned_lines)

        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', cleaned_text) if 50 < len(s.strip()) < 300]
        relevant = [s for s in sentences if any(word.lower() in s.lower() for word in query.split())]

        context = " ".join(relevant[:10])  # limit to 10 sentences

        if len(context) > 100:
            
            result = summarizer(context, max_length=200, min_length=150, do_sample=False)
            summary_text = result[0]['summary_text']
            #print(summary_text)
        else:
            
            summary_text = context

        return summary_text.strip()
            
        

# Step 4: Synthesizer - Combines all extracted points and removes duplicates
class Synthesizer:
    def deduplicate_points(self, points):
        final_points = []
        for pt in points:
            if not any(fuzz.ratio(pt, existing) > 80 for existing in final_points):
                final_points.append(pt)
        return final_points

    def synthesize(self, results):
        all_summaries = [res["summary"] for res in results if res["summary"]]
        final_paragraph = " ".join(all_summaries)
        key_points = [pt for res in results for pt in res["key_points"]]
        deduped_points = self.deduplicate_points(key_points)
        return {
            "final_summary": final_paragraph.strip(),
            "key_points": deduped_points
        }

# Step 5: WebResearchAgent - Ties all components together
class WebResearchAgent:
    def __init__(self, api_key):
        self.searcher = WebSearcher(api_key)
        self.scraper = WebScraper()
        self.content_analyzer = ContentAnalyzer()
        self.synthesizer = Synthesizer()

    def run(self, query):
        print(f"🔍 Searching for: {query}")
        links = self.searcher.search(query)
        print(f"🌐 Found {len(links)} links")

        results = {}
        for i,link in enumerate(links):
            print(f"📄 Scraping: {link}")
            text = self.scraper.scrape(link)
            if text:
                analysis = self.content_analyzer.analyze(text, query)
                results[i]={ "link":link,"summary":analysis}
                   
        return results
        #final_output = self.synthesizer.synthesize(results)
        #return final_output

# Main execution block
if __name__ == "__main__":
    

    #print("\n🧠 Final Summary:\n", output["final_summary"])
    #print("\n📌 Key Points:")
    #for point in output["key_points"]:
    #    print("-", point)
    
    app.run(debug=True)