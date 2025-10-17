# 🚀 Coding History - Quick Start Guide

## Installation (One Command)

```bash
bash /Users/yourox/AI-Workspace/scripts/install_auto_capture.sh
```

Then restart your terminal or run:
```bash
source ~/.zshrc
```

## ✅ That's it! Capture is now automatic.

---

## 🎮 Simple Controls

### Turn ON/OFF
```bash
ch_toggle    # Toggle capture on/off
ch_on        # Turn ON capture
ch_off       # Turn OFF capture
```

### Check Status
```bash
ch_stats     # Show capture statistics
```

---

## 📁 Clean File Structure

### Core Files (Keep These)
```
scripts/
├── coding_history_core.py           # Database & compression engine
├── coding_history_capture_async.py  # Async capture system
├── coding_history_monitor.py        # Performance dashboard
├── coding_history_shell_hooks.sh    # Shell integration
├── install_auto_capture.sh          # Installer
└── cursor_terminal_init.sh          # Cursor integration

mcp_servers/
├── coding_history_mcp.py            # MCP server for Claude Desktop
└── coding_history_config.json       # MCP configuration

data/coding_history/
├── sessions.db                      # SQLite database
├── outputs/                         # Compressed chunks
└── config/                          # Settings
```

### Old Files (Can Delete)
```
scripts/
├── coding_history_capture.py        # OLD - replaced by async version
├── coding_history_vector.py         # OLD - not needed
└── setup_coding_history_mcp.sh      # OLD - replaced by install_auto_capture.sh
```

---

## 🔍 How It Works

1. **Automatic** - Captures all terminal commands in background
2. **Zero Lag** - Async processing, no terminal slowdown
3. **Compressed** - 80-90% size reduction
4. **Searchable** - Via Claude Desktop MCP integration

---

## 📊 Resource Impact

- **CPU**: <1% (background async)
- **Memory**: 5-10MB
- **Storage**: 10-50MB/day (compressed)
- **Terminal Speed**: NO IMPACT

---

## 🎯 Test It's Working

1. After installation, run some commands:
```bash
npm install something
python3 -c "print('test')"
git status
```

2. Check capture:
```bash
ch_stats
```

You should see:
```
Captured: [number increasing]
Deduplicated: [some number]
Queue: 0/1000
```

---

## 🔧 Advanced

### Live Monitoring
```bash
python3 /Users/yourox/AI-Workspace/scripts/coding_history_monitor.py --watch
```

### Manual Cleanup (optional)
To remove old files:
```bash
rm /Users/yourox/AI-Workspace/scripts/coding_history_capture.py
rm /Users/yourox/AI-Workspace/scripts/coding_history_vector.py
rm /Users/yourox/AI-Workspace/scripts/setup_coding_history_mcp.sh
```

---

## 💡 Tips

- Capture is **ON by default** after installation
- Use `ch_off` before sensitive work
- Check `ch_stats` anytime to see if it's working
- Everything is stored locally - no cloud

---

**That's all! Your coding history is now being captured automatically.**