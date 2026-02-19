#!/usr/bin/env python3
"""
Simple web search using requests - no API key or Playwright needed
Scrapes DuckDuckGo HTML
"""

import sys
import json
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class DuckDuckGoParser(HTMLParser):
    """Parse DuckDuckGo HTML search results"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_result = {}
        self.in_title = False
        self.in_snippet = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Result title link
        if tag == 'a' and attrs_dict.get('class') == 'result__a':
            self.in_title = True
            self.current_result = {'url': attrs_dict.get('href', '')}

        # Result snippet
        if tag == 'a' and attrs_dict.get('class') == 'result__snippet':
            self.in_snippet = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_title:
            self.in_title = False
            if self.current_result.get('title'):
                self.results.append(self.current_result)

        if tag == 'a' and self.in_snippet:
            self.in_snippet = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.in_title:
            self.current_result['title'] = data
        elif self.in_snippet and self.results:
            if 'snippet' not in self.results[-1]:
                self.results[-1]['snippet'] = data

def search_web(query, max_results=5):
    """Search DuckDuckGo and return results"""
    try:
        # URL encode query
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        # Fetch search results
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Parse results
        parser = DuckDuckGoParser()
        parser.feed(html)

        # Format results
        results = []
        for i, result in enumerate(parser.results[:max_results]):
            results.append({
                'position': i + 1,
                'title': result.get('title', 'No title'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', '')
            })

        return {
            'query': query,
            'results': results,
            'total': len(results)
        }

    except Exception as e:
        return {
            'query': query,
            'error': str(e),
            'results': []
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: web_search_simple.py "search query"'}))
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_web(query)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
