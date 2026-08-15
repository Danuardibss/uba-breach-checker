import { PlaywrightCrawler } from 'crawlee';

// Keyword pencarian dari argument terminal (default: breach database)
const targetKeyword = process.argv[2] || 'breach database';

console.log(`[*] Starting Crawlee Engine Scraper for Target: ${targetKeyword}...`);

const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: 5,
    headless: true, // Jalan di background

    async requestHandler({ request, page, log }) {
        log.info(`Crawling URL: ${request.url}`);
        const title = await page.title();
        
        console.log(`\n==================================================`);
        console.log(`[+] SUCCESS SCRAPED DATA:`);
        console.log(`    Title : ${title}`);
        console.log(`    URL   : ${request.url}`);
        console.log(`==================================================\n`);
    },

    failedRequestHandler({ request, log }) {
        log.error(`Request ${request.url} failed.`);
    },
});

// Run crawler nembak pencarian OSINT
await crawler.run([
    `https://html.duckduckgo.com/html/?q=${encodeURIComponent(targetKeyword)}`,
]);