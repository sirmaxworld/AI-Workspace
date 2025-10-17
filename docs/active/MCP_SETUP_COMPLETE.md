# 🔌 MCP Server Setup - Access Your Knowledge Base

**Date:** October 15, 2025
**Status:** Ready for Testing

---

## 📊 Current MCP Configuration

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Active Servers:**
1. ✅ **REF** - REF.tools integration
2. ✅ **DesktopCommander** - Desktop automation
3. ✅ **Semgrep** - Code security scanning
4. ✅ **secure-memory** - Your memory system

---

## 🎯 Recommended Update for YouTube Knowledge Access

### **Current Setup:**
```json
"secure-memory": {
  "command": "/usr/local/bin/python3.11",
  "args": ["/Users/yourox/AI-Workspace/mcp_servers/secure_memory_server.py"]
}
```

### **Recommended: Add YouTube Knowledge Server**

Update config to:
```json
{
  "mcpServers": {
    "ref": { ... },
    "DesktopCommander": { ... },
    "semgrep": { ... },
    "memory": {
      "command": "/usr/local/bin/python3.11",
      "args": ["/Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py"]
    }
  }
}
```

**Why?** The `claude_memory_server.py` includes:
- All secure memory functions
- YouTube transcript search
- Knowledge pipeline access
- Recent pipeline runs summaries

---

## 🔧 Update Script

Run this to update your MCP config:

```bash
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "ref": {
      "command": "npx",
      "args": ["-y", "ref-tools-mcp@latest"],
      "env": {
        "REF_API_KEY": "ref-91bc566473a59b3f6b6a"
      }
    },
    "DesktopCommander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "semgrep": {
      "command": "/Users/yourox/.local/bin/uvx",
      "args": ["semgrep-mcp"]
    },
    "memory": {
      "command": "/usr/local/bin/python3.11",
      "args": ["/Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py"]
    }
  }
}
EOF

# Restart Claude Desktop to apply changes
```

---

## 📚 Available MCP Tools & Resources

### **From memory server:**

**Tools:**
- `save_memory(text, memory_type)` - Save to memory
- `search_memories(query, limit)` - Search all memories
- `get_memory_stats()` - Memory statistics
- `run_pipeline(domain_key)` - Trigger knowledge collection

**Resources:**
- `memory://context` - Get memory context
- `knowledge://recent_runs` - Recent pipeline summaries

---

## 🔍 How to Access Your Knowledge in Claude Desktop

After updating config and restarting Claude Desktop:

### **1. Search YouTube Transcripts**
```
Can you search my YouTube knowledge base for "AI agents"?
```

### **2. View Recent Knowledge Runs**
```
Show me my recent knowledge pipeline runs
```

### **3. Get Memory Stats**
```
What's in my memory system?
```

### **4. Run Knowledge Collection**
```
Can you run the knowledge pipeline for ai_trends domain?
```

---

## 📝 Testing Your Setup

### **Test 1: MCP Server Status**
In Claude Desktop, ask:
```
Can you check my memory server status?
```

Should see memory stats with counts.

### **Test 2: Search Transcripts**
After transcripts are loaded:
```
Search my YouTube knowledge for "how to build with AI"
```

Should return relevant segments with timestamp links.

### **Test 3: View Knowledge Base**
```
Show me what domains have been collected in my knowledge base
```

---

## 🚀 Current Status

### **✅ What's Ready:**
- MCP servers configured
- Memory server operational
- YouTube transcriber working
- Quality control system built

### **⏳ In Progress:**
- Transcribing 5 test videos from Greg Isenberg
- Storing in Mem0 knowledge base
- Testing search functionality

### **🔄 After Transcription Completes:**
1. You'll have 5 videos searchable in Mem0
2. Accessible via Claude Desktop MCP
3. Can search by topic, get timestamp links
4. Professional QC scores included

---

## 💡 Quick Commands

### **View Transcripts**
```bash
ls -la /Users/yourox/AI-Workspace/data/transcripts/
```

### **Check Mem0 Database**
```bash
ls -la /Users/yourox/AI-Workspace/data/youtube_qdrant/
```

### **View Extraction Reports**
```bash
cat /Users/yourox/AI-Workspace/data/extraction_reports/*.json | python3 -m json.tool
```

### **Test MCP Server Locally**
```bash
/usr/local/bin/python3.11 /Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py
```

---

## 🎯 Next Steps

1. **Wait for transcription** to complete (running in background)
2. **Update MCP config** (optional - for knowledge access)
3. **Restart Claude Desktop**
4. **Test searching** your knowledge base

---

**Once transcription completes, you'll be able to search Greg Isenberg's videos directly from Claude Desktop!** 🎉
