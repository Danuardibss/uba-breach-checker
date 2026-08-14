import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

class DarkwebOSINTCrawler:
    """
    POC Module: Darkweb & Onion Index Monitoring Scraper
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def fetch_ahmia_onion_links(self, session, keyword):
        """
        Nge-crawl link .onion dari Ahmia (Tor Search Indexer) berdasarkan keyword target
        """
        url = f"https://ahmia.fi/search/?q={keyword}"
        print(f"[*] Crawling Tor Index (Ahmia) for target: {keyword}...")
        
        try:
            async with session.get(url, headers=self.headers, timeout=12) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for result in soup.find_all('li', class_='result'):
                        title_elem = result.find('a')
                        desc_elem = result.find('p')
                        
                        if title_elem:
                            results.append({
                                "source": "Ahmia Tor Search Indexer",
                                "title": title_elem.text.strip(),
                                "onion_url": title_elem.get('href', ''),
                                "snippet": desc_elem.text.strip() if desc_elem else "No description available"
                            })
                    return results
                else:
                    return []
        except Exception as e:
            return [{"error": f"Failed to crawl Tor indexer: {str(e)}"}]

    async def run_monitoring(self, target):
        async with aiohttp.ClientSession() as session:
            ahmia_results = await self.fetch_ahmia_onion_links(session, target)
            
            return {
                "target_monitored": target,
                "total_onion_results": len(ahmia_results),
                "darkweb_mentions": ahmia_results
            }

def check_darkweb_mentions(target):
    """
    Synchronous wrapper function untuk kemudahan integrasi dengan core engine
    """
    crawler = DarkwebOSINTCrawler()
    return asyncio.run(crawler.run_monitoring(target))

if __name__ == "__main__":
    target = input("\nMasukkan Email/Username/Keyword Target: ").strip()
    if target:
        res = check_darkweb_mentions(target)
        print("\n================--- [ DARKWEB CRAWLER RESULT ] ---================")
        print(json.dumps(res, indent=4))
        print("==================================================================")