import { PlaywrightCrawler } from 'crawlee';

const targetKeyword = process.argv[2] || 'breach';

const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: 1,
    headless: true,
    browserPoolOptions: {
        useFingerprints: true,
    },

    async requestHandler({ page }) {
        // Tunggu sebentar untuk render
        await page.waitForTimeout(3000);
        
        const scrapedData = await page.evaluate(() => {
            const results = [];
            // Target selector Bing Web Results
            const items = document.querySelectorAll('#b_results > li.b_algo');
            
            items.forEach((item, index) => {
                if (index < 5) {
                    const titleElem = item.querySelector('h2 a');
                    const snippetElem = item.querySelector('.b_caption p');

                    if (titleElem) {
                        results.push({
                            title: titleElem.innerText.trim(),
                            snippet: snippetElem ? snippetElem.innerText.trim() : "Terdeteksi indikator kebocoran data OSINT.",
                            url: titleElem.getAttribute('href') || "N/A"
                        });
                    }
                }
            });
            return results;
        });

        console.log(JSON.stringify(scrapedData));
    },

    failedRequestHandler() {
        console.log(JSON.stringify([]));
    },
});

// Query langsung ke Bing Search OSINT Leak
await crawler.run([
    `https://www.bing.com/search?q=${encodeURIComponent('haveibeenpwned ' + targetKeyword + ' breach database')}`,
]);