#!/bin/bash
# Simple web search using curl + HTML parsing
# No API key or Playwright needed

query="$*"
if [ -z "$query" ]; then
    echo '{"error": "Usage: web_search_curl.sh <query>"}'
    exit 1
fi

# URL encode the query
encoded_query=$(echo "$query" | jq -sRr @uri)

# Search DuckDuckGo Lite (simple HTML version)
html=$(curl -s -A "Mozilla/5.0" "https://lite.duckduckgo.com/lite/?q=$encoded_query")

# Extract results using grep and sed
results=$(echo "$html" | grep -oP '<a rel="nofollow" class="result-link" href="\K[^"]+' | head -5)
titles=$(echo "$html" | grep -oP '<a rel="nofollow" class="result-link"[^>]+>\K[^<]+' | head -5)
snippets=$(echo "$html" | grep -oP '<td class="result-snippet">\K[^<]+' | head -5)

# Build JSON output
echo "{"
echo '  "query": "'$query'",'
echo '  "results": ['

i=0
while IFS= read -r url && IFS= read -r title <&3 && IFS= read -r snippet <&4; do
    [ -z "$url" ] && break
    i=$((i+1))

    # Clean up text
    title=$(echo "$title" | sed 's/"/\\"/g' | sed 's/\r//g')
    snippet=$(echo "$snippet" | sed 's/"/\\"/g' | sed 's/\r//g')

    [ $i -gt 1 ] && echo ","
    echo "    {"
    echo '      "position": '$i','
    echo '      "title": "'$title'",'
    echo '      "url": "'$url'",'
    echo '      "snippet": "'$snippet'"'
    echo -n "    }"
done < <(echo "$results") 3< <(echo "$titles") 4< <(echo "$snippets")

echo ""
echo "  ],"
echo '  "total": '$i
echo "}"
