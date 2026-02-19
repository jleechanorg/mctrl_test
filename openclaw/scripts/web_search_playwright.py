#!/usr/bin/env python3
"""
Web search using Playwright - no API key required
Automates Google search and extracts results
"""

import sys
import json
from playwright.sync_api import sync_playwright

def search_web(query, max_results=5):
    """Search DuckDuckGo using Playwright and return results"""
    results = []

    with sync_playwright() as p:
        # Launch browser with realistic settings
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Navigate to DuckDuckGo search
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            page.goto(search_url, timeout=30000)

            # Wait for results to load
            page.wait_for_selector('article[data-testid="result"]', timeout=10000)

            # Extract search results
            result_elements = page.query_selector_all('article[data-testid="result"]')

            for i, element in enumerate(result_elements[:max_results]):
                try:
                    # Extract title
                    title_elem = element.query_selector('h2')
                    title = title_elem.inner_text() if title_elem else 'No title'

                    # Extract URL
                    link_elem = element.query_selector('a[data-testid="result-title-a"]')
                    url = link_elem.get_attribute('href') if link_elem else ''

                    # Extract snippet
                    snippet_elem = element.query_selector('div[data-result="snippet"]')
                    snippet = snippet_elem.inner_text() if snippet_elem else ''

                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'position': i + 1
                        })
                except Exception as e:
                    continue

        except Exception as e:
            return {'error': str(e), 'results': []}
        finally:
            browser.close()

    return {
        'query': query,
        'results': results,
        'total': len(results)
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: web_search_playwright.py "search query"'}))
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_web(query)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
