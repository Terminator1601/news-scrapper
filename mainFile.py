import requests
import feedparser
from bs4 import BeautifulSoup
import csv
import pandas as pd
from urllib.parse import urljoin
from sources import news_sources  # Assuming news_sources is a dictionary of sources

try:
    from gemini_analyzer import analyze_headlines, headline_key
except ImportError:  # google-genai not installed; keyword analysis still works
    analyze_headlines = None
    headline_key = None

# Browser-like headers: several sources (Hindustan Times, Business Standard)
# reject requests that identify as python-requests
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Function to filter headlines
def filter_headlines(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header to the output file
        header = next(reader)
        writer.writerow(header)

        # Filter out single-word, double-word, and null headlines
        for row in reader:
            headline = row[1].strip()
            word_count = len(headline.split())

            if word_count > 2:  # Only keep headlines with more than 2 words
                writer.writerow(row)

# Function to fetch headlines from an RSS feed; returns (title, link) tuples
def fetch_rss_headlines(source_info):
    try:
        response = requests.get(
            source_info["url"], headers=REQUEST_HEADERS, timeout=20)
        if response.status_code != 200:
            print(
                f"Failed to fetch {source_info['url']} (status {response.status_code})")
            return []
        feed = feedparser.parse(response.content)
        return [(entry.get("title", "").strip(), entry.get("link") or 'N/A')
                for entry in feed.entries]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Function to fetch headlines based on the mapping
def fetch_headlines(source_info):
    if source_info.get("type") == "rss":
        return fetch_rss_headlines(source_info)
    try:
        response = requests.get(
            source_info["url"], headers=REQUEST_HEADERS, timeout=20)
        if response.status_code != 200:
            print(
                f"Failed to fetch {source_info['url']} (status {response.status_code})")
            return []
        # Parse from bytes so BeautifulSoup reads the page's declared charset
        # (response.text can mis-guess and produce mojibake like â€™)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting headlines based on the tags/CSS selectors specified
        headlines = []
        for tag in source_info["headline_tags"]:
            headlines.extend(soup.select(tag))
        return headlines
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Function to save the headlines and their URLs to a CSV file
def save_headlines_to_csv(source_name, headlines, filename, base_url=None):
    with open(filename, 'a', newline='', encoding='utf-8') as file:  # Open file with UTF-8 encoding
        writer = csv.writer(file)
        for headline in headlines:
            if isinstance(headline, tuple):  # RSS entries arrive as (title, link)
                headline_text, link = headline
                writer.writerow([source_name, headline_text, link])
                continue
            headline_text = headline.get_text().strip()
            # The link may be inside the headline tag or wrapping it
            anchor = headline.find('a') or headline.find_parent('a')
            if anchor and 'href' in anchor.attrs:
                link = urljoin(base_url, anchor['href'])
            else:
                link = 'N/A'  # If no href found
            writer.writerow([source_name, headline_text, link])

# Keywords related to the stock market
stock_keywords = [
    'stock', 'market', 'wealth', 'buy', 'sell', 'invest', 'investment',
    'trading', 'shares', 'equity', 'ipo', 'dividend', 'bonds', 'fund',
    'portfolio', 'bull', 'bear', 'securities', 'capital', 'mutual',
    'forex', 'commodities', 'derivatives', 'options', 'futures',
    'indices', 'nasdaq', 'dow', 's&p', 'nyse', 'exchange', 'etf',
    'hedge', 'hedge fund', 'margin', 'yield', 'interest rate', 'blue chip',
    'growth stock', 'penny stock', 'short sell', 'long position', 'day trading',
    'recession', 'economy', 'economic', 'earnings', 'valuation', 'assets',
    'liabilities', 'balance sheet', 'cash flow', 'financial statement', 'quarterly results',
    'insider trading', 'merger', 'acquisition', 'stock split', 'buyback',
    'ipo', 'underwriting', 'public offering', 'private equity', 'venture capital',
    'leverage', 'debt', 'credit rating', 'default', 'bankruptcy', 'inflation', 'deflation',
    'federal reserve', 'central bank', 'interest rates', 'monetary policy', 'fiscal policy',
    'gdp', 'gross domestic product', 'cpi', 'consumer price index', 'ppi', 'producer price index',
    'yield curve', 'treasury', 'bond market', 'fixed income', 'junk bond', 'credit spread'
]

# Function to label headlines, preferring Gemini analysis over keywords
def label_headlines(input_filename, output_filename, analysis=None):
    analysis = analysis or {}
    with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read and write the header with an additional "Label" column
        header = next(reader)
        header.append("Label")
        writer.writerow(header)

        for row in reader:
            headline = row[1].strip()
            analyzed = analysis.get(headline_key(headline)) if headline_key else None

            if analyzed is not None:
                label = 'stocks' if analyzed['is_stock_market'] else 'general'
            else:
                # Keyword fallback
                label = 'general'
                if any(keyword in headline.lower() for keyword in stock_keywords):
                    label = 'stocks'

            row.append(label)
            writer.writerow(row)

SIGNAL_TO_RESULT = {
    'buy': 'Buy shares of the company',
    'sell': 'Sell shares of the company',
    'hold': 'Hold/No action',
}

# Function to add 'result' column based on headline analysis
def add_result_column(df, analysis=None):
    # Expanded keywords for buy and sell decisions
    buy_keywords = [
        'invested', 'buy', 'acquire', 'acquisition', 'purchase', 'merger',
        'expand', 'expansion', 'growth', 'invest', 'investment', 'partner',
        'partnership', 'increase stake', 'joint venture', 'funding', 'raising capital',
        'capital injection', 'backing', 'support', 'boost', 'increase holdings'
    ]

    sell_keywords = [
        'sell', 'divest', 'disinvest', 'offload', 'cut stake', 'exit',
        'decrease stake', 'reduce holdings', 'liquidate', 'liquidation', 'spin-off',
        'withdrawal', 'close down', 'shutdown', 'downsizing', 'layoffs', 'job cuts'
    ]

    analysis = analysis or {}

    # Function to determine the result based on the headline
    def determine_result(headline):
        analyzed = analysis.get(headline_key(headline)) if headline_key else None
        if analyzed is not None:
            return SIGNAL_TO_RESULT[analyzed['signal']]
        headline_lower = headline.lower()  # Keyword fallback
        if any(word in headline_lower for word in buy_keywords):
            return 'Buy shares of the company'
        elif any(word in headline_lower for word in sell_keywords):
            return 'Sell shares of the company'
        else:
            return 'Hold/No action'

    def analysis_field(headline, field):
        analyzed = analysis.get(headline_key(headline)) if headline_key else None
        return analyzed[field] if analyzed else ''

    # Apply the function to the 'Headline' column to create the 'result' column
    df['result'] = df['Headline'].apply(determine_result)
    df['Company'] = df['Headline'].apply(lambda h: analysis_field(h, 'company'))
    df['Rationale'] = df['Headline'].apply(lambda h: analysis_field(h, 'rationale'))

    # Save the updated DataFrame to a new CSV file
    df.to_csv('./headlines/result_file.csv', index=False)

    print("The 'result' column has been added and the updated file has been saved as 'result_file.csv'.")

# Function to clean the data by removing general headlines and null URLs
def clean_data():
    # Load the CSV file into a DataFrame
    df = pd.read_csv('./headlines/labeled_headlines.csv')

    # Drop rows where the 'Label' column is 'general'
    df_cleaned = df[df['Label'] != 'general']
    df_cleaned = df_cleaned.dropna(subset=['URL'])

    # Save the cleaned DataFrame to a new CSV file
    df_cleaned.to_csv('./headlines/cleaned_file.csv', index=False)

    print("Rows with label 'general' have been removed. Cleaned data saved to 'cleaned_file.csv'.")

if __name__ == "__main__":
    file_name = './headlines/headlines.csv'

    # Clear the file before writing new content
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Headline", "URL"])  # Write the header row

    # Fetch and save headlines
    for source_name, source_info in news_sources.items():
        headlines = fetch_headlines(source_info)
        save_headlines_to_csv(source_name, headlines, file_name, source_info["url"])

    print(f"All headlines from multiple sources have been stored in '{file_name}'")

    # Filter headlines
    input_csv1 = './headlines/headlines.csv'
    output_csv1 = './headlines/filtered_headlines.csv'
    filter_headlines(input_csv1, output_csv1)
    print(f"Filtered headlines have been saved to '{output_csv1}'")

    # Analyze headlines with Gemini (cached; falls back to keywords per headline)
    analysis = {}
    if analyze_headlines is not None:
        with open(output_csv1, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            all_headlines = [row[1] for row in reader]
        analysis = analyze_headlines(all_headlines)

    # Label headlines
    input_csv2 = './headlines/filtered_headlines.csv'
    output_csv2 = './headlines/labeled_headlines.csv'
    label_headlines(input_csv2, output_csv2, analysis)
    print(f"Labeled headlines have been saved to '{output_csv2}'")

    # Clean the data
    print("---------------cleared function is running------------")
    clean_data()
    print("-------------------cleared function executed-------------------")

    # Add result column
    df = pd.read_csv('./headlines/cleaned_file.csv')
    print("Adding labels whether to buy, sell or hold...")
    add_result_column(df, analysis)
    print("--------------Executed--------------")
