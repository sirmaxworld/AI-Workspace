# 🔒 SECURE MEMORY SYSTEM

**Created:** October 14, 2025  
**Purpose:** Protect sensitive data (API keys, passwords) from unauthorized access

---

## 🎯 THE PROBLEM YOU IDENTIFIED

### **Security Risks:**
```
❌ All memories in one file
❌ Auto-loaded into every conversation  
❌ API keys visible to all MCP servers
❌ No access control
❌ Sensitive data could leak
```

### **Your Concern:**
> "Security for API keys so they are not shared unnecessarily with all other MCP instances"

**This is a CRITICAL security issue. You're absolutely right to address it!**

---

## ✅ THE SOLUTION: Classified Memory System

### **Four Security Levels:**

| Level | Icon | Auto-Load | Use Case | Example |
|-------|------|-----------|----------|---------|
| **PUBLIC** | 📢 | ✅ Yes | Safe conversation history | "User prefers TypeScript" |
| **PRIVATE** | 🔒 | ❌ No | Personal information | "User's birthday is June 15" |
| **CONFIDENTIAL** | ⚠️ | ❌ No | Business secrets | "Company revenue: $2M" |
| **SECRET** | 🔐 | ❌ NEVER | API keys, passwords | "ANTHROPIC_API_KEY=sk-..." |

---

## 🏗️ NEW ARCHITECTURE

### **Separate Storage Files:**

```
/Users/yourox/AI-Workspace/data/claude_memory_json/
├── memories_public.json         # Auto-loaded ✅
├── memories_private.json        # On request only 🔒
├── memories_confidential.json   # Explicit access ⚠️
└── memories_secret.json         # NEVER auto-loaded 🔐
```

### **Access Control:**

```
Claude starts conversation
         ↓
Loads: memory://public (only safe memories)
         ↓
API keys in memories_secret.json are NEVER loaded
         ↓
To access secrets: Use get_secret("key_name") explicitly
```

---

## 🚀 MIGRATION GUIDE

### **Step 1: Migrate Existing Memories**

```bash
cd /Users/yourox/AI-Workspace/scripts
/usr/local/bin/python3.11 secure_memory.py migrate
```

**This will:**
- Read your current 13 memories
- Automatically classify them by keywords
- Split into appropriate security files
- Preserve all data

**Classification Keywords:**
- **SECRET**: api_key, password, secret, token, credential
- **CONFIDENTIAL**: confidential, private key, internal
- **PRIVATE**: personal, private
- **PUBLIC**: everything else (default)

### **Step 2: Replace MCP Server**

Update Claude Desktop config to use secure server:

```bash
# Backup current config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup

# Edit config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Change:**
```json
"claude-memory": {
  "command": "/usr/local/bin/python3.11",
  "args": [
    "/Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py"
  ]
}
```

**To:**
```json
"secure-memory": {
  "command": "/usr/local/bin/python3.11",
  "args": [
    "/Users/yourox/AI-Workspace/mcp_servers/secure_memory_server.py"
  ]
}
```

### **Step 3: Restart Claude Desktop**

For changes to take effect.

---

## 📖 USAGE EXAMPLES

### **Saving Different Security Levels:**

```python
# Public (default) - auto-loads
save_memory("User completed security setup")

# Private - requires explicit access
save_memory("User's email: user@example.com", level="private")

# Confidential - protected
save_memory("Q4 revenue target: $5M", level="confidential")

# Secret - NEVER auto-loaded
save_memory("ANTHROPIC_API_KEY: sk-ant-xxxxx", level="secret")
save_memory("OpenAI API Key: sk-xxxxx", level="secret")
save_memory("Database password: mypass123", level="secret")
```

### **Accessing Secrets:**

```python
# List available API keys (names only)
list_api_keys()
# Output: "ANTHROPIC_API_KEY", "OpenAI API Key", etc.

# Get specific secret
get_secret("ANTHROPIC")
# Output: Full API key value

# Get database password
get_secret("database password")
# Output: Password value
```

### **Searching by Security Level:**

```python
# Search only public memories (safe)
search_memories("TypeScript")

# Search private memories (explicit)
search_memories("email", level="private")

# Search secrets (explicit, protected)
search_memories("API", level="secret")
```

---

## 🛡️ SECURITY FEATURES

### **1. Isolation**
- Each security level in separate file
- File permissions protect sensitive data
- MCP servers can't accidentally access secrets

### **2. Explicit Access**
- Secrets NEVER auto-load
- Must use `get_secret()` tool explicitly
- No accidental leakage in conversations

### **3. Audit Trail**
- All memories timestamped
- Security level recorded
- Can track who accessed what

### **4. Search Protection**
- Default searches exclude confidential/secret
- Must specify level explicitly
- Prevents accidental exposure

---

## 📊 COMPARISON: Before vs After

### **BEFORE (Insecure)**
```
memories.json:
[
  {"text": "User prefers TypeScript"},
  {"text": "ANTHROPIC_API_KEY: sk-ant-xxxxx"},  ← EXPOSED!
  {"text": "Email: user@example.com"}          ← EXPOSED!
]

Auto-loaded into EVERY conversation ❌
All MCP servers can read this file ❌
```

### **AFTER (Secure)**
```
memories_public.json:
[
  {"text": "User prefers TypeScript"}  ← Safe to auto-load ✅
]

memories_secret.json:
[
  {"text": "ANTHROPIC_API_KEY: sk-ant-xxxxx"}  ← NEVER auto-loaded 🔐
]

Only loaded via get_secret() ✅
Protected file permissions ✅
```

---

## 🔧 ADVANCED: Encryption (Optional)

For even more security, add encryption:

```python
# Install cryptography
pip install cryptography

# Encrypt secret file
from cryptography.fernet import Fernet

# Generate key (store in macOS Keychain)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt secrets
with open('memories_secret.json', 'rb') as f:
    encrypted = cipher.encrypt(f.read())

with open('memories_secret.json.enc', 'wb') as f:
    f.write(encrypted)
```

**Benefits:**
- Secrets encrypted at rest
- Even if file is accessed, data is unreadable
- Decrypt only when needed

---

## 🎯 BEST PRACTICES

### **DO:**
✅ Store API keys as **SECRET**  
✅ Store personal info as **PRIVATE**  
✅ Store business data as **CONFIDENTIAL**  
✅ Use `get_secret()` when you need keys  
✅ Keep PUBLIC memories general and safe  

### **DON'T:**
❌ Store passwords in PUBLIC memories  
❌ Auto-load sensitive data  
❌ Share secret file with version control  
❌ Log secret values in plain text  
❌ Store credit card numbers anywhere  

---

## 🔍 VERIFICATION

### **Check Migration:**
```bash
# View statistics
/usr/local/bin/python3.11 /Users/yourox/AI-Workspace/scripts/secure_memory.py stats
```

### **Test Security:**
```bash
# Public should auto-load
cat /Users/yourox/AI-Workspace/data/claude_memory_json/memories_public.json

# Secrets should exist but be separate
cat /Users/yourox/AI-Workspace/data/claude_memory_json/memories_secret.json
```

### **Verify in Claude Desktop:**
After restart:
- Public memories should appear automatically
- Secrets should NOT appear
- `get_secret()` tool should be available

---

## 🚨 EMERGENCY: If Secrets Leaked

### **Immediate Actions:**

1. **Rotate all compromised keys immediately**
   ```bash
   # Generate new keys at:
   - Anthropic Console: https://console.anthropic.com
   - OpenAI: https://platform.openai.com/api-keys
   - etc.
   ```

2. **Clear old memories**
   ```bash
   # Backup first
   cp memories_secret.json memories_secret.json.backup
   
   # Remove compromised secrets
   /usr/local/bin/python3.11 secure_memory.py search "old_key" level="secret"
   # Manually edit to remove
   ```

3. **Update .env file**
   ```bash
   # New keys go in .env, not memory
   nano /Users/yourox/AI-Workspace/.env
   ```

---

## 📁 FILE STRUCTURE

```
AI-Workspace/
├── scripts/
│   ├── secure_memory.py              # Classification system
│   └── claude_memory_ultimate.py     # Legacy (migrate from this)
│
├── mcp_servers/
│   ├── secure_memory_server.py       # New secure MCP server
│   └── claude_memory_server.py       # Old (replace this)
│
└── data/claude_memory_json/
    ├── memories.json                 # Old unified file (migrate from)
    ├── memories_public.json          # NEW: Safe memories
    ├── memories_private.json         # NEW: Personal info
    ├── memories_confidential.json    # NEW: Business secrets
    └── memories_secret.json          # NEW: API keys 🔐
```

---

## ✅ MIGRATION CHECKLIST

- [ ] Backup current memories.json
- [ ] Run migration script
- [ ] Verify all memories classified correctly
- [ ] Update Claude Desktop config
- [ ] Restart Claude Desktop
- [ ] Test: Public memories auto-load
- [ ] Test: Secrets require get_secret()
- [ ] Save new API key as secret
- [ ] Verify it doesn't auto-load
- [ ] Move API keys from .env references

---

**Your security concern was absolutely valid. This system protects your sensitive data properly!** 🔒

---

**Last Updated:** October 14, 2025  
**Status:** Ready to migrate  
**Next:** Run migration, then restart Claude Desktop
