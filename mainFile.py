import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from sources import news_sources  # Assuming news_sources is a dictionary of sources

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

# Function to fetch headlines based on the mapping
def fetch_headlines(source_info):
    try:
        response = requests.get(source_info["url"], allow_redirects=False)
        if response.status_code in [301, 302]:  # Check if it's a redirect
            print(f"Redirect encountered for {source_info['url']}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting headlines based on the tags specified
        headlines = []
        for tag in source_info["headline_tags"]:
            headlines.extend(soup.find_all(tag))
        return headlines
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Function to save the headlines and their URLs to a CSV file
def save_headlines_to_csv(source_name, headlines, filename, base_url=None):
    with open(filename, 'a', newline='', encoding='utf-8') as file:  # Open file with UTF-8 encoding
        writer = csv.writer(file)
        for headline in headlines:
            headline_text = headline.get_text().strip()
            href = headline.find('a')
            if href and 'href' in href.attrs:
                link = href['href']
                if link.startswith('/'):  # Handle relative URLs
                    link = base_url + link
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

# Function to label headlines based on keywords
def label_headlines(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read and write the header with an additional "Label" column
        header = next(reader)
        header.append("Label")
        writer.writerow(header)

        # Assign labels based on keywords
        for row in reader:
            headline = row[1].strip().lower()  # Assuming the headline is in the second column
            label = 'general'  # Default label

            # Check if any stock-related keyword is in the headline
            if any(keyword in headline for keyword in stock_keywords):
                label = 'stocks'

            row.append(label)
            writer.writerow(row)

# Function to add 'result' column based on headline analysis
def add_result_column(df):
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

    # Function to determine the result based on the headline
    def determine_result(headline):
        headline_lower = headline.lower()  # Convert headline to lowercase for case-insensitive matching
        if any(word in headline_lower for word in buy_keywords):
            return 'Buy shares of the company'
        elif any(word in headline_lower for word in sell_keywords):
            return 'Sell shares of the company'
        else:
            return 'Hold/No action'

    # Apply the function to the 'Headline' column to create the 'result' column
    df['result'] = df['Headline'].apply(determine_result)

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

    # Label headlines
    input_csv2 = './headlines/filtered_headlines.csv'
    output_csv2 = './headlines/labeled_headlines.csv'
    label_headlines(input_csv2, output_csv2)
    print(f"Labeled headlines have been saved to '{output_csv2}'")

    # Clean the data
    print("---------------cleared function is running------------")
    clean_data()
    print("-------------------cleared function executed-------------------")

    # Add result column
    df = pd.read_csv('./headlines/cleaned_file.csv')
    print("Adding labels whether to buy, sell or hold...")
    add_result_column(df)
    print("--------------Executed--------------")
