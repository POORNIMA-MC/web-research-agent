Web Research Agent

A Flask-based Web Research Agent that:
Takes a user query.

Searches Google (via SerpAPI) for relevant pages.

Scrapes and cleans the content.

Summarizes the information using a transformer model.

Displays the results neatly on a web page.

Features

Google Search integration via SerpAPI.

Web scraping using Selenium and BeautifulSoup.

Summarization using Hugging Face Transformers (BART model).

Duplicate removal using FuzzyWuzzy.

Simple web interface using Flask.

Setup Instructions

1. Clone the repository


$ git clone <repository-link>
$ cd <project-folder>

2. Install dependencies


$ pip install flask serpapi beautifulsoup4 requests selenium fuzzywuzzy transformers torch

3. Setup SerpAPI Key

Get your API key from SerpAPI.

Replace the placeholder API key inside app.py:

api_key = "your_serpapi_key_here"

4. Setup ChromeDriver

Install ChromeDriver that matches your Chrome browser version.

Ensure chromedriver is in your system's PATH.

5. Run the application

# Start the Flask server
$ python app.py

Access the app at: http://127.0.0.1:5000



Author

Poornima M.C

Happy researching! 🚀

