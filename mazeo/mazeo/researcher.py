# import requests
import urllib.request
import urllib.error
try:
    from googlesearch import search
except ImportError:
    def search(query, num_results=10):
        print(f"[Research Warning] googlesearch module not found. Returning empty results.")
        return []
import urllib.parse
import json
import re

class WebResearcher:
    def __init__(self):
        self.trusted_domains = [
            'wikipedia.org', 'britannica.com', 'history.com', 'nasa.gov', 
            'edu', 'gov', 'science.org', 'nature.com', 'reuters.com', 'bbc.com',
            'aljazeera.net', 'cnn.com', 'nytimes.com', 'skynewsarabia.com', 
            'theverge.com', 'techcrunch.com', 'wired.com'
        ]
        self.banned_keywords = ['forum', 'blog', 'reddit', 'twitter', 'facebook', 'quora', 'youtube']

    def is_reliable(self, url):
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in self.banned_keywords):
            return False
        if any(domain in url_lower for domain in self.trusted_domains):
            return True
        if '.gov' in url_lower or '.edu' in url_lower:
            return True
        if any(ext in url_lower for ext in ['.com', '.news', '.org', '.net', '.info']):
            if not any(bad in url_lower for bad in ['adclick', 'doubleclick', 'analytics', 'pixel']):
                return True
        return False

    def search_trusted_sources(self, query):
        print(f"[Research] Searching for: {query}")
        results = []
        try:
            for url in search(query, num_results=10):
                if self.is_reliable(url):
                    results.append(url)
                if len(results) >= 5:
                    break
        except Exception as e:
            print(f"[Research Error] googlesearch failed: {e}")

        if not results:
            print("[Research] Trying DuckDuckGo fallback...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}", headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    html = response.read().decode('utf-8')
                    resp_text = html
                links = re.findall(r'href="(https?://[^"]+)"', resp_text)
                for url in links:
                    if 'duckduckgo.com' not in url and self.is_reliable(url):
                        results.append(url)
                    if len(results) >= 5:
                        break
            except Exception as e:
                print(f"[Research Error] Fallback failed: {e}")
        return results

    def fetch_content(self, url):
        try:
            print(f"[Research] Fetching: {url}")
            print(f"[Research] Fetching: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')
                # html = html

                html = re.sub(r'<(script|style|nav|footer|header).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<[^<]+?>', ' ', html)
                text = ' '.join(text.split())
                return text[:3000]
        except Exception as e:
            print(f"[Research Error] Fetch failed for {url}: {e}")
        return ""

    def verify_and_synthesize(self, query, urls):
        if len(urls) < 1:
            return None, 0
        contexts = []
        for url in urls:
            content = self.fetch_content(url)
            if content:
                contexts.append({"url": url, "content": content})
        if not contexts:
            return None, 0
        return contexts, 0.8
