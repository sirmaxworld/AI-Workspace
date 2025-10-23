# Quick Start Guide

Get BI Intelligence Chat running in 5 minutes.

## Step 1: Check Prerequisites

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Node version (need 18+)
node --version

# Check if MCP servers exist
ls ../mcp-servers/bi-vault/server.py
ls ../mcp-servers/railway-postgres/server.py
```

## Step 2: Set OpenRouter API Key

Add to `/Users/yourox/AI-Workspace/.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

Get your key at: https://openrouter.ai/keys

## Step 3: Install Dependencies

```bash
# Backend dependencies
cd /Users/yourox/AI-Workspace/bi-chat/server
pip install -r requirements.txt

# Frontend dependencies
cd /Users/yourox/AI-Workspace/bi-chat/ui
npm install
```

## Step 4: Start the Application

### Option A: Automatic (Recommended)

```bash
cd /Users/yourox/AI-Workspace/bi-chat
./start.sh
```

### Option B: Manual

**Terminal 1 - Backend:**
```bash
cd /Users/yourox/AI-Workspace/bi-chat/server
python bi_chat_api.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/yourox/AI-Workspace/bi-chat/ui
npm run dev
```

## Step 5: Open and Test

1. **Open browser**: http://localhost:3001
2. **Wait for connection**: Should see "Connected" status
3. **Try example query**: Click one of the example buttons or type:
   ```
   What are the best opportunities in AI agents right now?
   ```

## Troubleshooting

### "Backend unhealthy"

```bash
# Check backend logs
cd bi-chat/server
cat backend.log

# Test manually
curl http://localhost:8000/health
```

### "OPENROUTER_API_KEY not set"

```bash
# Check .env file
cat /Users/yourox/AI-Workspace/.env | grep OPENROUTER
```

### MCP servers not connecting

```bash
# Test bi-vault
cd /Users/yourox/AI-Workspace
python mcp-servers/bi-vault/server.py

# Test railway-postgres
python mcp-servers/railway-postgres/server.py
```

## First Query Examples

### 🔍 Find Opportunities
```
What are the top 3 product opportunities with validated demand and low competition?
```

### 📈 Trend Analysis
```
Analyze the AI agents trend - what stage is it at and where is it heading?
```

### ✅ Validate Idea
```
I want to build an AI-powered content repurposing tool for LinkedIn creators. Is this a good opportunity?
```

### 🚀 GTM Strategy
```
How should I launch a B2B SaaS targeting small marketing agencies? What channels worked for similar products?
```

## Tips for Best Results

1. **Start with Quick Mode** for simple questions
2. **Use Deep Reasoning** for opportunity analysis (takes 30-60s but much better)
3. **Use Critical Analysis** when you want to validate or stress-test an idea
4. **Be Specific**: Instead of "AI trends", try "AI agents trend for SaaS products"
5. **Ask Follow-ups**: The model has conversation context

## Understanding the Responses

### Quick Mode (⚡ 5-10s)
- Fast, concise answers
- Good for factual queries
- Example: "What is the AI agents trend?"

### Deep Reasoning (🧠 30-60s)
- Multi-step analysis
- Cross-references multiple data sources
- Synthesizes patterns
- Example: "What should I build in the AI space?"

### Critical Analysis (🔍 60-120s)
- Systematic validation
- Evidence checking
- Risk assessment
- Example: "Should I build [specific idea]?"

## What's Next?

Once you're familiar with the interface:

1. **Explore Different Models**: Try GPT-4, Claude, O1 - each has strengths
2. **Deep Dives**: Use Deep Reasoning for comprehensive opportunity analyses
3. **Validate Ideas**: Use Critical Analysis before committing to build
4. **Export Insights**: Copy valuable insights for your notes
5. **Iterate**: Have conversations, ask follow-ups, explore related topics

## Common Workflows

### Finding Your Next Project
1. Quick Mode: "Show me growing trends in B2B SaaS"
2. Deep Reasoning: "Analyze the top 3 trends - which has best timing for a bootstrap developer?"
3. Critical Analysis: "Validate the best opportunity - what are the risks?"

### Validating an Existing Idea
1. Critical Analysis: "Validate: [your idea]"
2. Follow-up: "What similar products exist?"
3. Follow-up: "How would I differentiate?"
4. Deep Reasoning: "Create a GTM plan for this"

### Learning from Data
1. Quick Mode: "What are common mistakes in SaaS launches?"
2. Deep Reasoning: "What GTM strategies worked for AI tools?"
3. Follow-up: "Show me specific examples with results"

## Support

- 📖 **Full Docs**: See `README.md`
- 🐛 **Issues**: Check logs in `bi-chat/server/backend.log`
- 🔍 **Debug**: Test health at http://localhost:8000/health

Enjoy exploring your business intelligence data! 🚀
