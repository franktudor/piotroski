import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

class NewsService:

    SOURCE_URLS = {
        "reuters": "http://feeds.reuters.com/Reuters/worldNews",
        "ap": "https://apnews.com/rss"
    }

    def get_news(self, ticker: str, sources: List[str] = None) -> List[Dict]:
        """
        Fetches news for a given ticker from specified RSS feeds.
        Note: The free feeds are not ticker-specific. This service will
        fetch general news from the sources. A more advanced implementation
        would use a news API that allows for ticker-specific searches.
        """
        if sources is None:
            sources = ['reuters', 'ap']

        all_news = []
        for source in sources:
            url = self.SOURCE_URLS.get(source.lower())
            if not url:
                print(f"Warning: Unknown news source '{source}'")
                continue

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else 'No Title'
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''

                    news_item = {
                        "title": title,
                        "source": source.capitalize(),
                        "publishedAt": pub_date,
                        "url": link
                    }
                    all_news.append(news_item)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching news from {source}: {e}")
            except ET.ParseError as e:
                print(f"Error parsing XML from {source}: {e}")

        # Limit to top 5 for now as per TRD
        return all_news[:5]