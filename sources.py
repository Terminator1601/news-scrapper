# news_sources.py

news_sources = {
    "Live Mint": {
        "url": "https://www.livemint.com/",
        "headline_tags": ["h1", "h3"],
    },
    "CNBCTV18 Market": {
        "url": "https://www.cnbctv18.com/market/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "CNBCTV18 Main": {
        "url": "https://www.cnbctv18.com/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "India-Express": {
        "url": "https://indianexpress.com/",
        "headline_tags": ["h1", "li"],
    },
    "India-Today-business": {
        "url": "https://www.indiatoday.in/business",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "India-Today": {
        "url": "https://www.indiatoday.in/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    # NDTV's website returns 403 to non-browser clients, so use its RSS feeds
    "NDTV": {
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "type": "rss",
    },
    "NDTV-Profit": {
        "url": "https://feeds.feedburner.com/ndtvprofit-latest",
        "type": "rss",
    },
    "The-Hindu": {
        "url": "https://www.thehindu.com/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "The-Economic-Times": {
        "url": "https://economictimes.indiatimes.com/",
        "headline_tags": ["h1", "h2", "h3", "li"],
    },
    "Hindustan-Times": {
        "url": "https://www.hindustantimes.com/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "Business-Standard": {
        "url": "https://www.business-standard.com/latest-news",
        "headline_tags": ["h1", "h2", "h3"],
    },
    "Deccan-Hearld": {
        "url": "https://www.deccanherald.com/",
        "headline_tags": ["h1", "h2", "h3"],
    },
    # Add more sources as needed
}
