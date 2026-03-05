# Ralph Agent Instructions — Phase 11: Amazon Clone + PR Polish

You are an autonomous agent. Your current goal is to build a working Amazon clone website in /tmp/amazon-clone/ and verify it.

## Exit Criteria (ALL must be true to declare ORCHESTRATION_ALL_DONE)

1. All userStories in ralph-prd.json have passes: true
2. /tmp/amazon-clone/ exists with 5 files: index.html, product.html, cart.html, style.css, app.js
3. Summary posted to #worldai as jleechan

## Your Task Each Iteration

1. Read `ralph-prd.json` (in repo root — the working directory)
2. Read `ralph-progress.txt` (in repo root — the working directory)
3. Pick the **lowest wave, lowest priority** story where `passes: false`
4. Implement it
5. Verify against acceptanceCriteria
6. Update ralph-prd.json with `passes: true`
7. Append to ralph-progress.txt

## Story-Specific Instructions

### AMZN-1: Build Amazon clone scaffold

Create the directory and all 5 files in /tmp/amazon-clone/:

**index.html**: Homepage with Amazon-style layout:
- Dark nav bar (#131921) with logo "amazon", search input, cart icon with badge
- Product grid showing all 8 products from app.js
- Each product card: image, name, rating stars, price, "Add to Cart" button
- Import style.css and app.js

**product.html**: Product detail page:
- Shows single product info (use URL params like ?id=1)
- Larger image, full description, price, Add to Cart button

**cart.html**: Shopping cart page:
- Lists cart items from localStorage
- Shows quantity, subtotal per item, order total
- Remove from cart buttons

**style.css**: Amazon-inspired styling:
- `nav { background: #131921; }` orange search button and "Add to Cart" buttons
- Product card grid with hover shadow
- Star ratings in orange (#f0c040)
- Responsive grid layout

**app.js**: Full interactivity:
```javascript
const products = [
  { id: 1, name: "Wireless Headphones", price: 49.99, rating: 4.5, reviewCount: 1234, category: "electronics", imageUrl: "https://via.placeholder.com/200x200?text=Headphones" },
  { id: 2, name: "Mechanical Keyboard", price: 89.99, rating: 4.8, reviewCount: 567, category: "electronics", imageUrl: "https://via.placeholder.com/200x200?text=Keyboard" },
  { id: 3, name: "USB-C Hub", price: 34.99, rating: 4.2, reviewCount: 890, category: "electronics", imageUrl: "https://via.placeholder.com/200x200?text=USB+Hub" },
  { id: 4, name: "Coffee Maker", price: 79.99, rating: 4.6, reviewCount: 2345, category: "kitchen", imageUrl: "https://via.placeholder.com/200x200?text=Coffee+Maker" },
  { id: 5, name: "Running Shoes", price: 129.99, rating: 4.4, reviewCount: 678, category: "sports", imageUrl: "https://via.placeholder.com/200x200?text=Running+Shoes" },
  { id: 6, name: "Yoga Mat", price: 29.99, rating: 4.7, reviewCount: 3456, category: "sports", imageUrl: "https://via.placeholder.com/200x200?text=Yoga+Mat" },
  { id: 7, name: "Desk Lamp", price: 24.99, rating: 4.3, reviewCount: 456, category: "home", imageUrl: "https://via.placeholder.com/200x200?text=Desk+Lamp" },
  { id: 8, name: "Water Bottle", price: 19.99, rating: 4.9, reviewCount: 7890, category: "sports", imageUrl: "https://via.placeholder.com/200x200?text=Water+Bottle" },
];

function getCart() { return JSON.parse(localStorage.getItem('cart') || '[]'); }
function saveCart(cart) { localStorage.setItem('cart', JSON.stringify(cart)); }
function addToCart(productId) { ... }
function removeFromCart(productId) { ... }
function updateCartBadge() { ... }
function renderProducts(filter = '') { ... } // filters products array by name
function searchProducts(query) { renderProducts(query); }
```

Verify with:
```bash
ls -la /tmp/amazon-clone/
wc -l /tmp/amazon-clone/*.html /tmp/amazon-clone/*.js /tmp/amazon-clone/*.css
```

### AMZN-2: Verify and post to Slack

Run verification checks:
```bash
grep -c 'addToCart' /tmp/amazon-clone/app.js
grep 'localStorage' /tmp/amazon-clone/app.js
grep -i 'search\|filter' /tmp/amazon-clone/app.js
grep '#131921' /tmp/amazon-clone/style.css
```

Then post to #worldai as jleechan:
```bash
curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel":"C0AH3RY3DK6","text":"Amazon clone built at /tmp/amazon-clone/ — 5 files. Products: Wireless Headphones, Mechanical Keyboard, Coffee Maker, Running Shoes, Yoga Mat, Desk Lamp, USB-C Hub, Water Bottle. Cart uses localStorage. Search filters by name. Ready to demo!"}'
```

Verify curl response has ok:true and user == U09GH5BR3QU.

## Coding Standards
- Write actual file contents — do NOT skip or abbreviate
- ONE story per iteration
- After AMZN-1: mark passes=true in ralph-prd.json, then stop
- After AMZN-2: mark passes=true in ralph-prd.json, then stop

## Stop Condition
When all stories pass AND all exit criteria met, output:
ORCHESTRATION_ALL_DONE
