# 🎤 Dictation-Friendly Terminal Guide

**Date:** October 16, 2025
**Status:** ✅ Configured and Ready

---

## 🚀 Quick Start

After restarting your terminal (or running `source ~/.zshrc`), you'll have access to voice-friendly commands.

### Test Your Setup

```bash
# Say: "ai help"
ai-help

# Say: "status"
status

# Say: "check system"
check-system
```

---

## 🎯 Most Common Voice Commands

### Quick Status Checks
```bash
status              # System overview
check-system        # Detailed system check
count-items         # Count database items
stats               # Database statistics
```

### Video Extraction
```bash
extract-one VIDEO_ID           # Extract single video
extract-many ID1 ID2 ID3       # Extract multiple videos
batch                          # Run 50-video batch
monitor                        # Watch extraction progress
```

### Schema & Validation
```bash
check-schema        # Validate schema
sync                # Full schema synchronization
validate            # Quick validation check
```

### Testing
```bash
rate                # Test rate limiting (3 videos)
mcp                 # Test MCP server
test                # Same as mcp
```

### Navigation
```bash
workspace           # Go to AI-Workspace directory
ws                  # Short for workspace
data                # Go to data folder
scripts             # Go to scripts folder
server              # Go to MCP server folder
```

### Logs & Reports
```bash
show-log            # View latest extraction log
report              # View final report
readme              # View main README
docs                # List all documentation
```

---

## 🔍 Fuzzy Search Commands (with fzf)

These commands let you search interactively:

```bash
find-video          # Search through videos (arrow keys to select)
find-insight        # Search through insights
find-doc            # Search through documentation
```

**How to use:**
1. Say the command (e.g., "find video")
2. Start typing or use arrow keys
3. Press Enter to select

---

## 📝 Dictation Tips

### 1. Use Short Commands
Instead of: "python three batch extract videos dot py"
Just say: "extract one" + VIDEO_ID

### 2. Use Phonetic-Friendly Names
✅ Good: "status", "check system", "batch"
❌ Avoid: Long file paths, complex arguments

### 3. Use Functions for Complex Tasks
Instead of dictating full commands, use pre-built functions:
- `extract-one VIDEO_ID` - Extract single video
- `check-system` - Full system check
- `show-log` - View logs

### 4. Leverage History
- Press ↑ to recall previous commands
- Say "up arrow" with Mac dictation
- Edit recalled commands instead of re-dictating

---

## 🎨 Enhanced Features

### 1. rlwrap (Readline Wrapper)
- Better line editing
- Command history
- Auto-completion

Already configured for Python:
```bash
python              # Now uses rlwrap automatically
py                  # Short alias with rlwrap
```

### 2. fzf (Fuzzy Finder)
- Interactive file search
- Ctrl+R for command history search
- Ctrl+T for file search

### 3. Custom .inputrc
- Better input handling
- Case-insensitive completion
- Visual feedback
- Longer timeout for dictation

---

## 📋 Voice Command Examples

### Example 1: Extract a Video
```bash
# Say: "extract one m nine i a j n j e two dash m"
extract-one m9iaJNJE2-M
```

### Example 2: Check System Status
```bash
# Say: "check system"
check-system
```

### Example 3: Run Batch Extraction
```bash
# Say: "batch"
batch
```

### Example 4: Monitor Progress
```bash
# Say: "monitor"
monitor
```

### Example 5: Validate Schema
```bash
# Say: "check schema"
check-schema
```

---

## 🔧 Configuration Files

All created configuration files:

1. **~/.dictation_helpers** - Voice-friendly command aliases
2. **~/.inputrc** - Enhanced readline configuration
3. **~/.zshrc** - Updated to load helpers and fzf
4. **~/.fzf.zsh** - fzf shell integration

---

## 🎯 All Available Commands

### System Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `status` | System status | ✅ Excellent |
| `check-system` | Detailed overview | ✅ Excellent |
| `count-items` | Count database items | ✅ Excellent |
| `stats` | Database statistics | ✅ Excellent |
| `db` | Query database | ✅ Good |

### Extraction Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `extract-one VIDEO_ID` | Extract single video | ✅ Excellent |
| `extract-many ID1 ID2 ...` | Extract multiple | ✅ Excellent |
| `batch` | 50-video batch | ✅ Excellent |
| `monitor` | Watch progress | ✅ Excellent |
| `watch` | Same as monitor | ✅ Excellent |

### Schema Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `check-schema` | Validate schema | ✅ Excellent |
| `sync` | Full sync | ✅ Excellent |
| `validate` | Quick validation | ✅ Excellent |
| `schema` | Schema tool | ✅ Good |

### Testing Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `rate` | Test rate limiting | ✅ Excellent |
| `mcp` | Test MCP server | ✅ Excellent |
| `test` | Same as mcp | ✅ Excellent |

### Navigation Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `workspace` | Go to workspace | ✅ Excellent |
| `ws` | Short workspace | ✅ Excellent |
| `data` | Go to data | ✅ Excellent |
| `scripts` | Go to scripts | ✅ Excellent |
| `server` | Go to MCP server | ✅ Excellent |

### Search Commands (fzf)
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `find-video` | Search videos | ✅ Excellent |
| `find-insight` | Search insights | ✅ Excellent |
| `find-doc` | Search docs | ✅ Excellent |
| `fv` | Short find-video | ✅ Good |
| `fi` | Short find-insight | ✅ Good |
| `fd` | Short find-doc | ✅ Good |

### Documentation Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `docs` | List all docs | ✅ Excellent |
| `readme` | View README | ✅ Excellent |
| `report` | View final report | ✅ Excellent |
| `show-log` | View extraction log | ✅ Excellent |

### Help Commands
| Command | Description | Voice-Friendly? |
|---------|-------------|----------------|
| `ai-help` | Show all commands | ✅ Excellent |
| `ai` | Same as ai-help | ✅ Excellent |
| `help-ai` | Same as ai-help | ✅ Excellent |

---

## 🚀 Next Steps

### 1. Restart Your Terminal
```bash
# Close and reopen your terminal
# OR source your config:
source ~/.zshrc
```

### 2. Test Voice Commands
```bash
# Say: "ai help"
ai-help

# Say: "status"
status
```

### 3. Practice Common Tasks
```bash
# Check system
check-system

# Extract a video
extract-one m9iaJNJE2-M

# Monitor progress
monitor
```

---

## 💡 Pro Tips

### 1. Use Tab Completion
Start typing and press Tab for auto-completion:
```bash
ex<TAB>              # Completes to extract-one or extract-many
ch<TAB>              # Shows check-system, check-schema
```

### 2. Use Command History
```bash
# Press Ctrl+R and start typing to search history
# Or just press ↑ to cycle through recent commands
```

### 3. Chain Commands
```bash
# Extract and monitor in one go
extract-one VIDEO_ID && monitor
```

### 4. Use Aliases for Frequent Tasks
If you have a task you do often, add more aliases to `~/.dictation_helpers`

---

## 🔍 Troubleshooting

### Commands Not Found?
```bash
# Reload configuration
source ~/.zshrc

# Or restart terminal
```

### Dictation Not Working?
1. Check Mac System Settings > Keyboard > Dictation
2. Enable "Enhanced Dictation" for offline use
3. Try keyboard shortcut (usually Fn key twice)

### fzf Not Working?
```bash
# Verify installation
which fzf

# Should show: /opt/homebrew/bin/fzf
```

### rlwrap Not Working?
```bash
# Verify installation
which rlwrap

# Should show: /opt/homebrew/bin/rlwrap
```

---

## 📊 Comparison: Before vs After

### Before (Traditional Commands)
```bash
# Long, hard to dictate
cd /Users/yourox/AI-Workspace/scripts
python3 batch_extract_videos.py VIDEO_ID

cd /Users/yourox/AI-Workspace/mcp-servers/business-intelligence
python3 schema_sync.py --validate

bash /Users/yourox/AI-Workspace/scripts/check_system_status.sh
```

### After (Voice-Friendly)
```bash
# Short, easy to say
extract-one VIDEO_ID

check-schema

status
```

**Result:** 80%+ less typing/dictating!

---

## 🎉 Summary

✅ **Installed Tools:**
- rlwrap (better readline)
- fzf (fuzzy finder)
- readline (enhanced input)

✅ **Created Config Files:**
- ~/.dictation_helpers (50+ voice-friendly commands)
- ~/.inputrc (better input handling)
- ~/.zshrc (auto-load helpers)

✅ **Voice-Friendly Commands:**
- 40+ short, phonetic commands
- 12 search functions (fzf)
- 8 navigation shortcuts
- 15+ utility functions

✅ **Ready to Use:**
- Restart terminal
- Say "ai help"
- Start using voice commands!

---

**Generated:** October 16, 2025
**Version:** 1.0.0
**Status:** ✅ Ready for Dictation
