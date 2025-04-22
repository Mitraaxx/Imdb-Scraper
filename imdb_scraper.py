import requests
from bs4 import BeautifulSoup
import argparse
from urllib.parse import quote_plus
import time

class IMDBSeriesScraper:
    def __init__(self):
        self.base_url = "https://www.imdb.com"
        self.search_url = "https://www.imdb.com/find?q="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.imdb.com/'
        }

    def search_series(self, query):
        """Search for a series on IMDb and return potential matches"""
        try:
            print(f"\nSearching IMDb for: '{query}'...")
            search_response = requests.get(
                f"{self.search_url}{quote_plus(query)}&s=tt&ttype=tv",
                headers=self.headers,
                timeout=10
            )
            search_response.raise_for_status()
            
            soup = BeautifulSoup(search_response.text, 'html.parser')
            results = []
            
            result_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
            
            for item in result_items[:5]:  
                title_element = item.find('a', class_='ipc-metadata-list-summary-item__t')
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                link = title_element['href'].split('?')[0]
                results.append({
                    'title': title,
                    'url': f"{self.base_url}{link}"
                })
                
            return results if results else None
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return None

    def get_series_rating(self, series_url):
        """Get the rating for a specific series"""
        try:
            print(f"Fetching details from: {series_url}")
            time.sleep(1)  
            series_response = requests.get(series_url, headers=self.headers, timeout=10)
            series_response.raise_for_status()
            
            soup = BeautifulSoup(series_response.text, 'html.parser')
            
          
            rating_element = soup.select_one('[data-testid="hero-rating-bar__aggregate-rating__score"] span:first-child')
            rating = rating_element.text.strip() if rating_element else "N/A"
            
            
            title_element = soup.select_one('h1[data-testid="hero__pageTitle"] span')
            title = title_element.text if title_element else "Unknown Title"
            
            return {
                'title': title,
                'rating': rating,
                'url': series_url
            }
            
        except Exception as e:
            print(f"Rating fetch error: {str(e)}")
            return None

    def get_series_rating_by_name(self, series_name):
        """Search for a series by name and return its rating"""
        search_results = self.search_series(series_name)
        
        if not search_results:
            print(f"\n❌ No results found for '{series_name}'")
            return None
            
        print(f"\n🔍 Found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"{i}. {result['title']}")
        
       
        print("\nFetching rating for the first result...")
        return self.get_series_rating(search_results[0]['url'])

def main():
    parser = argparse.ArgumentParser(description="IMDb TV Series Rating Checker")
    parser.add_argument('series', nargs='+', help="Name of the TV series to search")
    args = parser.parse_args()
    
    series_name = ' '.join(args.series)
    scraper = IMDBSeriesScraper()
    
    result = scraper.get_series_rating_by_name(series_name)
    
    if result:
        print("\n" + "="*50)
        print(f"📺 Title: {result['title']}")
        print(f"⭐ Rating: {result['rating']}/10")
        print(f"🔗 URL: {result['url']}")
        print("="*50 + "\n")
    else:
        print("\nFailed to get rating information.")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")  