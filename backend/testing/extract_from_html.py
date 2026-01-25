# extract_from_html.py

from bs4 import BeautifulSoup
import json
import re

# Read the saved HTML
with open('twitter_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("📂 Loading HTML file...")
print(f"📏 Size: {len(html)} bytes\n")

soup = BeautifulSoup(html, 'html.parser')

# Find article
article = soup.find('article')

if article:
    print("✅ Found <article> element\n")
    
    # Extract all text from article
    all_text = article.get_text(separator='\n', strip=True)
    
    # Clean up
    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
    
    # Filter out navigation/UI text
    content_lines = []
    skip_words = ['Follow', 'Sign in', 'More', 'Home', 'Explore', 'Notifications', 
                  'Messages', 'Grok', 'Lists', 'Bookmarks', 'Communities', 'Premium',
                  'Profile', 'Post', 'Search', 'Like', 'Reply', 'Repost', 'Share']
    
    for line in lines:
        # Skip short lines and UI elements
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
    print(f"✅ EXTRACTED!")
    print(f"{'='*70}")
    print(f"📝 Lines: {len(content_lines)}")
    print(f"📝 Words: {word_count}")
    print(f"⏱️  Read: {word_count // 200} min")
    print(f"\n📄 Content:\n")
    print(full_content[:1500])
    print("\n...")
    print(f"{'='*70}\n")
    
    # Save
    with open('twitter_extracted.txt', 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print("💾 Saved to: twitter_extracted.txt\n")
    
    # Save JSON
    result = {
        'success': True,
        'word_count': word_count,
        'content': full_content
    }
    
    with open('twitter_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("💾 Saved to: twitter_extracted.json\n")
    
else:
    print("❌ No article found in HTML")
