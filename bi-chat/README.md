# BI Intelligence Chat

Intelligent chat interface for analyzing business intelligence data with high-reasoning AI models.

## Features

- 🤖 **Multiple AI Models**: GPT-4, Claude Sonnet 4.5, O1, Gemini Pro, and more
- 🧠 **Three Thinking Modes**:
  - ⚡ **Quick Analysis**: Fast responses (5-10s)
  - 🧠 **Deep Reasoning**: Multi-step analysis with cross-referencing (30-60s)
  - 🔍 **Critical Analysis**: Systematic validation and risk assessment (60-120s)
- 📊 **MCP Integration**: Direct access to your business intelligence data
- 💬 **Streaming Responses**: Real-time streaming for immediate feedback
- 📱 **Modern UI**: Clean, responsive interface built with Next.js and Tailwind

## Architecture

```
┌─────────────────┐
│   Chat UI       │
│   (Next.js)     │
└────────┬────────┘
         │
    ┌────▼────┐
    │ FastAPI │
    │ Backend │
    └────┬────┘
         │
    ┌────▼──────────┐
    │   OpenRouter  │
    │ (AI Models)   │
    └───────────────┘
         │
    ┌────▼────────────┐
    │  MCP Servers    │
    │  - bi-vault     │
    │  - railway-pg   │
    │  - coding-brain │
    └─────────────────┘
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenRouter API key
- Existing MCP servers (bi-vault, railway-postgres)

## Setup

### 1. Install Backend Dependencies

```bash
cd bi-chat/server
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd bi-chat/ui
npm install
```

### 3. Configure Environment

Add to your `.env` file:

```bash
# OpenRouter API Key (required)
OPENROUTER_API_KEY=your_key_here

# Railway Database (for MCP servers)
RAILWAY_DATABASE_URL=postgresql://...
```

### 4. Start Backend Server

```bash
cd bi-chat/server
python bi_chat_api.py
```

The backend will start on `http://localhost:8000`

### 5. Start Frontend

```bash
cd bi-chat/ui
npm run dev
```

The UI will be available at `http://localhost:3001`

## Usage

### Quick Start

1. **Select a Model**: Choose from GPT-4, Claude, O1, or other models
2. **Choose Thinking Mode**:
   - ⚡ Quick: For simple queries
   - 🧠 Deep: For opportunity analysis
   - 🔍 Critical: For idea validation
3. **Ask Questions**: Type your query and press Enter

### Example Queries

**Finding Opportunities:**
```
What are the best opportunities in AI agents right now?
```

**Market Timing:**
```
Is it too late to build a content repurposing AI tool?
```

**Idea Validation:**
```
Validate my idea: AI-powered meeting summarizer for remote teams
```

**GTM Strategy:**
```
How should I launch a SaaS for small agencies?
```

**Trend Analysis:**
```
What's the trajectory of the 'AI agents' trend? Where is it heading?
```

## How It Works

### Quick Mode (⚡)
1. Your query is sent to the selected AI model
2. Model has access to MCP tool descriptions
3. Returns fast, concise answer with evidence

### Deep Reasoning Mode (🧠)
1. **Planning Phase**: Model plans which MCP tools to call
2. **Data Retrieval**: Backend fetches data from bi-vault, Railway DB
3. **Analysis Phase**: Model reasons over retrieved data
4. **Response**: Comprehensive analysis with citations

### Critical Analysis Mode (🔍)
1. Systematic validation framework
2. Evidence checking across multiple sources
3. Assumption testing
4. Risk assessment
5. Balanced evaluation with caveats

## API Endpoints

- `GET /health` - Check backend health and connected MCP servers
- `GET /models` - List available AI models
- `GET /tools` - List available MCP tools
- `GET /examples` - Get example queries
- `POST /chat` - Main chat endpoint (streaming)

## Data Sources

The chat interface has access to:

- **7,008+ Business Insights** from 331 videos
- **416 Unique Trends** with frequency and stage data
- **1,056 Opportunities** (startup ideas, market gaps, trends)
- **5,487 Y Combinator Companies** with enrichment data
- **Validated Problems & Solutions** from business intelligence
- **GTM Strategies** from successful cases
- **Comment Intelligence** from thousands of viewers

## Customization

### Adding New Models

Edit `server/reasoning_orchestrator.py`:

```python
self.model_map = {
    "your-model-id": "provider/model-name",
    ...
}
```

### Adding New Thinking Modes

Edit `server/prompts/reasoning_prompts.py` to add custom reasoning strategies.

### Styling

The UI uses Tailwind CSS. Edit `ui/app/globals.css` for custom styles.

## Troubleshooting

### Backend Won't Start

- **Check MCP Servers**: Ensure bi-vault and railway-postgres servers exist
- **Check API Key**: Verify OPENROUTER_API_KEY is set in `.env`
- **Port Conflict**: Backend uses port 8000, frontend uses 3001

### MCP Connection Issues

```bash
# Test MCP servers independently
python mcp-servers/bi-vault/server.py
python mcp-servers/railway-postgres/server.py
```

### Streaming Not Working

- **CORS**: Frontend expects backend on localhost:8000
- **Firewall**: Check if ports 8000/3001 are blocked
- **Browser**: Try Chrome/Firefox (best SSE support)

## Development

### Backend Development

```bash
# Auto-reload enabled
cd bi-chat/server
python bi_chat_api.py
```

### Frontend Development

```bash
# Hot reload enabled
cd bi-chat/ui
npm run dev
```

### Adding MCP Tools

1. Add tool to MCP server
2. Restart backend to refresh tool cache
3. Tool automatically available to AI models

## Architecture Details

### MCP Client

The `mcp_client.py` handles:
- Connecting to multiple MCP servers
- Caching available tools
- Executing tool calls asynchronously
- Error handling and retries

### Reasoning Orchestrator

The `reasoning_orchestrator.py` coordinates:
- AI model selection and routing
- System prompt construction
- Multi-pass reasoning (plan → execute → analyze)
- Response streaming

### Frontend Components

- **ChatInterface**: Main container, manages state
- **ChatMessage**: Renders messages with markdown
- **ModelSelector**: Dropdown for model selection
- **ThinkingModeSelector**: Visual selector for modes

## Performance

- **Quick Mode**: 5-10 seconds
- **Deep Reasoning**: 30-60 seconds (multiple MCP calls)
- **Critical Analysis**: 60-120 seconds (comprehensive validation)

## Costs

Using OpenRouter with pay-per-use pricing:
- **GPT-4 Turbo**: ~$0.01-0.03 per query
- **Claude Sonnet**: ~$0.01-0.02 per query
- **O1 Models**: ~$0.05-0.10 per query (advanced reasoning)

## Future Enhancements

- [ ] Conversation export/import
- [ ] Saved query templates
- [ ] Collaborative sessions
- [ ] Voice input/output
- [ ] Data visualization
- [ ] Custom MCP tool creation UI

## License

MIT

## Support

For issues or questions:
1. Check logs in `bi-chat/server/` output
2. Verify MCP servers are running
3. Test backend health: `curl http://localhost:8000/health`
