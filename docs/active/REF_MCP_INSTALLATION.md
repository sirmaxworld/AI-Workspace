# 🚀 REF MCP Server Installation Guide

**Date:** October 13, 2025  
**Status:** Ready to Install

---

## 📋 **What is REF?**

REF is the #1 MCP server from the YouTube video you watched. It provides:

✅ **85% Token Reduction** - Only pulls relevant docs (not entire documentation)  
✅ **Smart Documentation Search** - Finds exact functions/APIs you need  
✅ **1000s of Sites** - Public GitHub repos, documentation sites, APIs  
✅ **Private Docs** - Can index your internal repos and PDFs (beta)  
✅ **Web Search Fallback** - Falls back to web search when needed  

### **How It Works:**

Instead of loading Figma's 80k token API documentation, REF finds the exact 200 tokens you need!

**Example:**
- **Old way (Context 7):** Load 80,000 tokens ($0.12 per call)
- **REF way:** Load 200 tokens ($0.0003 per call)
- **Savings:** 99.6% reduction in costs!

---

## 🎯 **Installation Steps**

### **Step 1: Get Your API Key**

1. Go to: https://ref.tools/signup
2. Sign up for an account
3. Copy your API key (looks like: `ref_xxxxxxxxxxxxx`)

💡 **Free Tier Available** - You can start for free!

### **Step 2: Choose Installation Method**

**METHOD A: HTTP (Recommended - Easiest)**  
Hosted by ref.tools, no local dependencies needed

**METHOD B: Local (Advanced)**  
Runs locally via npx, requires Node.js

---

## 📝 **METHOD A: HTTP Installation (Recommended)**

Create this file: `/Users/yourox/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_API_KEY_HERE"
    },
    "DesktopCommander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    }
  }
}
```

**Replace `YOUR_API_KEY_HERE` with your actual API key from Step 1.**

---

## 📝 **METHOD B: Local Installation (Advanced)**

If you prefer to run REF locally:

```json
{
  "mcpServers": {
    "ref": {
      "command": "npx",
      "args": ["ref-tools-mcp@latest"],
      "env": {
        "REF_API_KEY": "YOUR_API_KEY_HERE"
      }
    },
    "DesktopCommander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    }
  }
}
```

---

## ✅ **Step 3: Restart Claude Desktop**

After saving the config file:
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Go to Settings → Developer
4. Verify REF shows as "Connected"

---

## 🧪 **Step 4: Test It Works**

Open a new conversation in Claude Desktop and try:

```
"Search Figma API documentation for how to post a comment endpoint"
```

Claude should use REF to find the exact documentation!

---

## 🎁 **What You Get with REF**

### **Available Tools:**

1. **`ref_search_documentation`**  
   Search for documentation across 1000s of sites
   
   Example:
   ```
   "Search for Next.js getServerSideProps documentation"
   ```

2. **`ref_read_url`**  
   Fetch and convert any URL to markdown
   
   Example:
   ```
   "Read the React hooks documentation from react.dev"
   ```

3. **`ref_search_web`** (optional fallback)  
   General web search for when docs aren't enough

---

## 📊 **Comparison with Other Tools**

| Feature | REF | Context 7 | No Tool |
|---------|-----|-----------|---------|
| Token Usage | 200 (85% less) | 10,000+ | N/A |
| Cost per call | $0.0003 | $0.015 | N/A |
| Speed | Fast | Slow | N/A |
| Coverage | 1000s of sites | Limited | N/A |
| Smart Search | ✅ Yes | ❌ No | N/A |
| Private Docs | ✅ Yes (beta) | ❌ No | N/A |

---

## 🔧 **Troubleshooting**

### **REF Not Showing in Claude Desktop?**

1. Check config file location is correct
2. Verify JSON syntax is valid (use jsonlint.com)
3. Make sure you replaced `YOUR_API_KEY_HERE` with actual key
4. Restart Claude Desktop completely
5. Check Settings → Developer for error messages

### **Getting API Errors?**

1. Verify your API key is valid
2. Check you haven't exceeded free tier limits
3. Visit ref.tools dashboard to check status

### **Want to Test Configuration?**

Run this command to validate your JSON:
```bash
cat "/Users/yourox/Library/Application Support/Claude/claude_desktop_config.json" | python3 -m json.tool
```

If it outputs formatted JSON, your config is valid!

---

## 💡 **Pro Tips**

### **Best Prompts for REF:**

✅ **Good:**  
- "Search Stripe API documentation for creating a payment intent"
- "Find the React Query documentation for mutations"
- "Look up the OpenAI chat completions API parameters"

❌ **Avoid:**  
- "Search for general Python tutorials" (too broad)
- "Find me code examples" (be more specific about what)

### **Combine with Other MCP Servers:**

REF works great alongside:
- **Desktop Commander** (file system access) ✅ Already installed!
- **GitHub MCP** (repository management)
- **Semgrep** (security scanning)
- **Playwright** (UI testing)

---

## 📚 **Additional Resources**

- **REF Website:** https://ref.tools
- **GitHub Repo:** https://github.com/ref-tools/ref-tools-mcp
- **Documentation:** https://docs.ref.tools
- **MCP Specification:** https://modelcontextprotocol.io

---

## 🎉 **You're Almost Ready!**

**TODO List:**
- [ ] Sign up at ref.tools and get API key
- [ ] Create claude_desktop_config.json with your API key
- [ ] Restart Claude Desktop
- [ ] Test with a documentation search
- [ ] Enjoy 85% token savings!

---

**Created:** October 13, 2025  
**Your Workspace:** /Users/yourox/AI-Workspace  
**Config File:** /Users/yourox/Library/Application Support/Claude/claude_desktop_config.json
