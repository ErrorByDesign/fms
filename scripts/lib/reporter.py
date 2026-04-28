import yfinance as yf
import json

# The "DNA" mapping you specified
mapping = {
    "title": "content.title",
    "description": "content.description",
    "summary": "content.summary",
    "source": "content.provider.displayName",
    "category": "content.canonicalUrl.site",
    "url": "content.canonicalUrl.url",
    "publishDate": "content.pubDate",
    "premium": "content.finance.premiumFinance.isPremiumNews",
    "freemium": "content.finance.premiumFinance.isPremiumFreeNews"
}

def get_val(obj, path):
    for key in path.split('.'):
        obj = obj.get(key, {}) if isinstance(obj, dict) else None
    return obj if obj != {} else None

# Fetch and Filter
ticker = "SPAX.PVT" # Change as needed
raw = yf.Ticker(ticker).news
clean_news = [{k: get_val(art, p) for k, p in mapping.items()} for art in raw]

print(json.dumps({"NEWS": clean_news}, indent=2))
