# twitter_final.py

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup
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
                        PageMethod('wait_for_timeout', 5000),
                    ],
                },
                callback=self.parse,
            )
    
    def parse(self, response):
        print(f"\n📥 Scraping: {response.url}\n")
        
        # Use BeautifulSoup for better extraction
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title_tag = soup.find('title')
        title = title_tag.get_text() if title_tag else 'No title'
        
        # Find article
        article = soup.find('article')
        
        if not article:
            print("❌ No article found\n")
            return
        
        # Extract all text
        all_text = article.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # Filter out UI elements
        skip_words = ['Follow', 'Sign in', 'More', 'Home', 'Explore', 
                      'Notifications', 'Messages', 'Grok', 'Lists', 
                      'Bookmarks', 'Communities', 'Premium', 'Profile', 
                      'Post', 'Search', 'Like', 'Reply', 'Repost', 'Share']
        
        content_lines = []
        for line in lines:
            if len(line) < 10:
                continue
            if any(word in line for word in skip_words) and len(line) < 50:
                continue
            content_lines.append(line)
        
        # Combine
        full_content = '\n\n'.join(content_lines)
        word_count = len(full_content.split())
        
        # Print results
        print(f"{'='*70}")
        print(f"✅ SUCCESS!")
        print(f"{'='*70}")
        print(f"📰 Title: {title}")
        print(f"📝 Words: {word_count}")
        print(f"⏱️  Read: {word_count // 200} min")
        print(f"\n📄 Preview:\n")
        print(full_content[:800])
        print("\n...")
        print(f"{'='*70}\n")
        
        # Save
        with open('twitter_final.txt', 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n")
            f.write(full_content)
        
        print("💾 Saved to: twitter_final.txt\n")
        
        # JSON
        result = {
            'success': True,
            'url': response.url,
            'title': title,
            'content': full_content,
            'word_count': word_count,
            'read_time': max(1, word_count // 200)
        }
        
        with open('twitter_final.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("💾 Saved to: twitter_final.json\n")
        
        yield result

if __name__ == '__main__':
    print("\n🐦 Twitter Article Scraper - FINAL\n")
    
    url = "https://x.com/thedankoe/status/2010751592346030461"
    
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
    
    print("\n✅ Complete!\n")
