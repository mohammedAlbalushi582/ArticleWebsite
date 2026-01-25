# twitter_article_scraper.py

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
import json

class TwitterArticleSpider(scrapy.Spider):
    name = 'twitter_article'
    
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_timeout', 5000),  # Wait for content
                    ],
                },
                callback=self.parse,
            )
    
    def parse(self, response):
        print(f"\n📥 Scraping: {response.url}\n")
        
        # Extract title
        title = response.css('title::text').get()
        
        # Method 1: Try long-form article selectors
        article_content = []
        
        # Get all paragraphs in article
        paragraphs = response.css('article p::text').getall()
        if paragraphs:
            article_content.extend(paragraphs)
            print(f"✅ Found {len(paragraphs)} paragraphs via <p> tags")
        
        # Get headers
        headers = response.css('article h1::text, article h2::text, article h3::text').getall()
        if headers:
            print(f"✅ Found {len(headers)} headers")
        
        # Get all text from article (fallback)
        if not article_content:
            all_text = response.css('article::text').getall()
            article_content = [t.strip() for t in all_text if t.strip() and len(t.strip()) > 10]
            print(f"✅ Extracted {len(article_content)} text chunks")
        
        # Method 2: Try tweet text (for threads)
        tweet_texts = response.css('[data-testid="tweetText"]::text').getall()
        if tweet_texts:
            article_content.extend(tweet_texts)
            print(f"✅ Found {len(tweet_texts)} tweets")
        
        # Combine content
        full_content = '\n\n'.join(article_content)
        word_count = len(full_content.split())
        
        # Print results
        print(f"\n{'='*70}")
        print(f"✅ EXTRACTION COMPLETE!")
        print(f"{'='*70}")
        print(f"📰 Title: {title}")
        print(f"📝 Total words: {word_count}")
        print(f"⏱️  Read time: {max(1, word_count // 200)} min")
        print(f"\n📄 Content Preview:\n")
        print(full_content[:800])
        print("\n...")
        print(f"{'='*70}\n")
        
        # Save to text file
        if full_content:
            with open('twitter_article.txt', 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"URL: {response.url}\n")
                f.write(f"Words: {word_count}\n")
                f.write(f"\n{'='*70}\n\n")
                f.write(full_content)
            
            print(f"💾 Saved to: twitter_article.txt\n")
        
        # Save to JSON
        result = {
            'success': True,
            'url': response.url,
            'title': title,
            'content': full_content,
            'word_count': word_count,
            'read_time': max(1, word_count // 200),
        }
        
        with open('twitter_article.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved to: twitter_article.json\n")
        
        yield result

if __name__ == '__main__':
    print("\n🐦 Twitter Article Scraper\n")
    
    url = "https://x.com/thedankoe/status/2010751592346030461"
    
    print(f"URL: {url}\n")
    print("⏳ Launching...\n")
    
    process = CrawlerProcess({
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'LOG_LEVEL': 'ERROR',
    })
    
    process.crawl(TwitterArticleSpider, url=url)
    process.start()
    
    print("\n✅ Done!\n")
