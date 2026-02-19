#!/usr/bin/env python3
"""
Google Custom Search API integration
Free tier: 100 queries/day
"""

import sys
import json
import os
import urllib.request
import urllib.parse

def search_google(query, api_key, search_engine_id, max_results=5):
    """Search using Google Custom Search API"""
    try:
        # URL encode query
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={encoded_query}&num={max_results}"

        # Make request
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        # Format results
        results = []
        for i, item in enumerate(data.get('items', [])):
            results.append({
                'position': i + 1,
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })

        return {
            'query': query,
            'results': results,
            'total': len(results),
            'searchInformation': data.get('searchInformation', {})
        }

    except Exception as e:
        return {
            'query': query,
            'error': str(e),
            'results': []
        }

def main():
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print(json.dumps({
            'error': 'Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_ENGINE_ID',
            'help': 'Get free key at: https://developers.google.com/custom-search/v1/overview'
        }))
        sys.exit(1)

    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: web_search_google.py "search query"'}))
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_google(query, api_key, search_engine_id)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
