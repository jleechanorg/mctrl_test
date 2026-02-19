#!/usr/bin/env python3
"""
Tavily AI Search API integration
Free tier: 1,000 queries/month (best for AI agents)
"""

import sys
import json
import os
import urllib.request

def search_tavily(query, api_key, max_results=5):
    """Search using Tavily API"""
    try:
        url = "https://api.tavily.com/search"

        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": max_results
        })

        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers)

        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))

        # Format results
        results = []
        for i, item in enumerate(data.get('results', [])):
            results.append({
                'position': i + 1,
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'snippet': item.get('content', '')
            })

        return {
            'query': query,
            'answer': data.get('answer', ''),  # AI-generated answer
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
    api_key = os.getenv('TAVILY_API_KEY')

    if not api_key:
        print(json.dumps({
            'error': 'Missing TAVILY_API_KEY',
            'help': 'Get free key at: https://tavily.com/ (1,000/month free)'
        }))
        sys.exit(1)

    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: web_search_tavily.py "search query"'}))
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_tavily(query, api_key)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
