import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re

class DarkwebOSINTCrawler:
    """
    POC Module: Darkweb & Onion Index Monitoring Scraper (Enhanced Parser)
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch_ahmia_onion_links(self, session, keyword):
        """
        Nge-crawl link .onion dari Ahmia (Tor Search Indexer)
        """
        url = f"https://ahmia.fi/search/?q={keyword}"
        print(f"[*] Crawling Tor Index (Ahmia) for target: {keyword}...")
        
        try:
            async with session.get(url, headers=self.headers, timeout=12) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    
                    # Cari semua tag <li> yang ada di halaman pencarian
                    for li in soup.find_all('li'):
                        a_tag = li.find('a', href=True)
                        if a_tag:
                            href = a_tag['href']
                            # Deteksi link .onion atau redirect ahmia
                            if '.onion' in href or '/redirect/' in href:
                                title = a_tag.text.strip()
                                desc_p = li.find('p')
                                snippet = desc_p.text.strip() if desc_p else "No snippet available"
                                
                                # Formatting link onion
                                onion_url = href
                                if '/redirect/' in href:
                                    match = re.search(r'redirect_url=(.+)', href)
                                    if match:
                                        onion_url = match.group(1)
                                
                                if title and onion_url not in [r['onion_url'] for r in results]:
                                    results.append({
                                        "source": "Ahmia Tor Indexer",
                                        "title": title,
                                        "onion_url": onion_url,
                                        "snippet": snippet
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
    crawler = DarkwebOSINTCrawler()
    return asyncio.run(crawler.run_monitoring(target))

if __name__ == "__main__":
    target = input("\nMasukkan Email/Username/Keyword Target: ").strip()
    if target:
        res = check_darkweb_mentions(target)
        print("\n================--- [ DARKWEB CRAWLER RESULT ] ---================")
        print(json.dumps(res, indent=4))
        print("==================================================================")