# Web Scraping Lessons Learned

**Date**: 2024-10-16
**Project**: Pinkbike Collector for Cycling Trends Domain
**Technologies**: Browserbase, Playwright, Python

## Executive Summary

Successfully built a Pinkbike article scraper using Browserbase to bypass bot protection. Learned critical lessons about CSS selector debugging and the importance of inspecting actual HTML structure before writing extraction code.

---

## Key Learnings

### 1. Never Guess CSS Selectors

**Problem**: Initially wrote generic CSS selectors based on common patterns:
```python
# WRONG: Generic selectors that didn't match Pinkbike
content_selectors = [
    'article .body',
    '.article-body',
    '.content-body'
]
```

**Result**: Extracted 0 chars of content, 0 comments, 0 images despite successful page loads.

**Solution**: Always inspect the actual HTML first using a debug script:

```python
# Debug script to capture real HTML
def capture_html(url):
    # Use Browserbase to load page
    page.goto(url)
    time.sleep(3)

    # Save full HTML
    html = page.content()
    with open('debug_page.html', 'w') as f:
        f.write(html)

    # Quick diagnostics
    for selector in ['article', '.blog-body', '.content']:
        try:
            elem = page.locator(selector).first
            print(f"Found {selector}: {len(elem.inner_text())} chars")
        except:
            print(f"Not found: {selector}")
```

**Outcome**: Discovered Pinkbike uses:
- `.blog-body` for article content (not `.article-body`)
- `.cmcont` for comments (not `.comment`)
- `.news-photo` for images (not generic `img`)
- `.commentUser` for comment authors (not `.author`)

### 2. Site-Specific Patterns Are Common

Different sites use unique class names and structures. Document patterns discovered:

| Site Element | Common Pattern | Pinkbike Actual | Notes |
|-------------|----------------|-----------------|-------|
| Article body | `.article-body`, `article` | `.blog-body` | Main content container |
| Article sections | `.section` | `.blog-section-inside` | Individual content blocks |
| Comments | `.comment`, `.comment-item` | `.cmcont` | Comment containers |
| Comment author | `.author`, `.comment-author` | `.commentUser` | Author links |
| Images | `article img` | `.news-photo` | Specific class for photos |
| Engagement | `.views`, `.view-count` | `data-analytics-data` | Embedded in JSON |

### 3. Browserbase Debugging Workflow

**Effective debugging sequence**:

1. **Create debug script** to capture HTML
   ```python
   # Save page HTML for inspection
   output_file = Path("debug_page.html")
   with open(output_file, 'w') as f:
       f.write(page.content())
   ```

2. **Use grep to find patterns** in saved HTML
   ```bash
   grep -n 'class="[^"]*comment[^"]*"' debug_page.html | head -10
   grep -n 'class="[^"]*body[^"]*"' debug_page.html
   ```

3. **Read HTML at specific line ranges** where content should be
   ```python
   # Found comments at line 1740 in grep
   # Read context around that area
   read_file(offset=1740, limit=100)
   ```

4. **Update selectors** based on actual HTML structure

5. **Test incrementally** - verify each selector type separately

### 4. Common Scraping Pitfalls

#### Lazy-Loaded Content
**Issue**: Images and comments may not load until scrolled into view.

**Solution**:
```python
# Scroll to trigger lazy loading
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
time.sleep(2)

# For comments specifically
page.evaluate("window.scrollTo(0, 800)")  # Scroll to comments section
time.sleep(2)
```

**Lesson**: Still didn't capture images/comments on Pinkbike - may need longer waits or multiple scrolls.

#### Dynamic Content
**Issue**: Some data embedded in JavaScript or loaded via AJAX.

**Evidence**: Found in Pinkbike HTML:
```html
<a data-analytics-data="{&quot;comments&quot;: &quot;188&quot;}">188 Comments</a>
```

**Lesson**: Engagement metrics might be in `data-*` attributes, not visible text.

#### Nested Structures
**Issue**: Comment threads have replies nested inside parent comments.

**Challenge**: Extracting `.cmcont` gets parent + all child text concatenated.

**Partial Solution**:
```python
# Get full text and try to clean it
full_text = comment_elem.inner_text()
if author in full_text:
    comment_text = full_text.replace(author, '', 1).strip()

# Limit length if too long (likely includes nested replies)
if len(comment_text) > 1000:
    comment_text = comment_text[:1000]
```

**Better Solution**: Target specific child elements, exclude nested `.cmcont`

### 5. Browserbase Best Practices

**Session Management**:
```python
# Always clean up sessions
try:
    # ... scraping work ...
finally:
    bb.sessions.delete(session_id)
```

**Timeouts**:
```python
# Use appropriate timeouts for page loads
page.goto(url, wait_until="domcontentloaded", timeout=60000)

# Wait for dynamic content
time.sleep(3)  # Conservative wait after page load
```

**Error Handling**:
```python
# Try multiple selectors, don't fail on first miss
for selector in content_selectors:
    try:
        elem = page.locator(selector).first
        if elem and len(elem.inner_text()) > 100:
            content = elem.inner_text()
            break
    except:
        continue
```

### 6. Successful Patterns

**What Worked**:

1. ✅ **Iterative selector approach** - try multiple variations
2. ✅ **HTML inspection first** - debug script to capture actual structure
3. ✅ **Incremental testing** - test each extraction component separately
4. ✅ **Fallback mechanisms** - alternative selectors when primary fails
5. ✅ **Multiple waits** - give time for page to fully render

**Content Extraction Success**:
```python
# This pattern worked well
content_selectors = [
    '.blog-body',           # Site-specific primary
    '.blog-section-inside', # Site-specific secondary
    'article .body',        # Generic fallback
    '.article-body'         # Generic fallback
]

# Fallback to multiple elements
if not content:
    sections = page.locator('.blog-section .blog-section-inside').all()
    content = '\n\n'.join([s.inner_text() for s in sections])
```

**Result**: 18,394 characters extracted from YT Jeffsy review (vs 0 before)

---

## Metrics: Before vs After

| Metric | Before (Generic Selectors) | After (Site-Specific) |
|--------|---------------------------|---------------------|
| Content | 0 chars | 18,394 chars ✅ |
| Title | Extracted | Extracted ✅ |
| Author | Partial | Full ✅ |
| Tags | 11 tags | 11 tags ✅ |
| Comments | 0 | 0 (needs more work) |
| Images | 0 | 0 (lazy-load issue) |
| Videos | 0 | 0 (rare in articles) |

**Key Win**: Content extraction working means AI pipeline can now process articles for business intelligence.

---

## Recommended Workflow for Future Scraping Projects

### Phase 1: Reconnaissance (15-30 min)
1. Create debug script to capture HTML from 2-3 sample pages
2. Save HTML files locally
3. Use grep/search to identify actual CSS classes used
4. Document site-specific patterns

### Phase 2: Selector Development (30-60 min)
1. Write selectors based on actual HTML patterns
2. Include site-specific selectors first, generic fallbacks second
3. Test each selector type independently (title, content, comments, etc.)
4. Validate with `inner_text()` length checks

### Phase 3: Incremental Testing (30-60 min)
1. Test on 2-3 diverse articles
2. Check what's missing (images, comments, metadata)
3. Add scroll/wait logic for lazy-loaded content
4. Refine selectors based on failures

### Phase 4: Production Validation (1-2 hours)
1. Test on 10+ articles
2. Calculate success rates per field
3. Identify edge cases
4. Document known limitations

### Phase 5: Documentation (15-30 min)
1. Document site-specific selectors
2. Note lazy-load requirements
3. Record success rates
4. Save lessons learned

---

## Tools & Commands Reference

### Grep patterns for selector discovery
```bash
# Find comment-related classes
grep -n 'class="[^"]*comment[^"]*"' debug.html | head -10

# Find content containers
grep -n 'class="[^"]*body[^"]*"' debug.html

# Find author elements
grep -n 'class="[^"]*author[^"]*"' debug.html

# Find engagement metrics
grep -n 'class="[^"]*view[^"]*"' debug.html
grep -n 'data-analytics' debug.html
```

### Playwright debugging
```python
# Check if selector matches anything
try:
    elems = page.locator('.my-selector').all()
    print(f"Found {len(elems)} elements")
except:
    print("Selector failed")

# Get attribute values
elem.get_attribute('data-analytics-data')
elem.get_attribute('datetime')

# Scroll and wait
page.evaluate("window.scrollTo(0, 800)")
time.sleep(2)
```

---

## Open Questions / Future Work

1. **Lazy-loaded images**: Need to implement scroll-and-wait loop to trigger image loading
2. **Comment extraction**: `.cmcont` selector found 188+ elements in HTML but extracted 0 - timing issue?
3. **Engagement metrics**: Found in `data-analytics-data` JSON attributes, need to parse
4. **Multiple article structures**: Second test article (Ibis Ripmo) had 0 content - different structure?

---

## Impact

**Before this work**: Web scraper would fail silently, extracting empty data.

**After this work**:
- Systematic debugging process established
- 18K+ chars of article content extracted successfully
- Reusable patterns documented for future domains
- Clear workflow for any new website scraping

**Business Value**: Can now feed full Pinkbike reviews into AI extraction pipeline for product intelligence, pricing trends, and community sentiment analysis.

---

## References

- Pinkbike HTML structure analysis: `/Users/yourox/AI-Workspace/debug_pinkbike_page.html`
- Collector implementation: `/Users/yourox/AI-Workspace/domains/cycling_trends/pinkbike_collector.py`
- Test results: `/Users/yourox/AI-Workspace/data/pinkbike_articles/`
- Browserbase docs: https://docs.browserbase.com/
