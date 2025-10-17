# 🚨 RESTART TubeDB UI - Manual Instructions

Due to shell issues, please run these commands manually in your terminal:

## Option 1: Quick Restart (Recommended)

Open a new terminal and run:

```bash
# Step 1: Kill any existing processes
lsof -ti:7000 | xargs kill -9
lsof -ti:4000 | xargs kill -9

# Step 2: Navigate to the directory
cd /Users/yourox/AI-Workspace/tubedb-ui

# Step 3: Start the server on port 7000
npm run dev
```

The server will start and show:
```
> tubedb-ui@0.1.0 dev
> next dev -p 7000

   ▲ Next.js
   - Local:        http://localhost:7000
   - Environments: .env.local
```

## Option 2: Using the Management Script

```bash
cd /Users/yourox/AI-Workspace
chmod +x tubedb-manager.sh
./tubedb-manager.sh restart
```

## Option 3: Using PM2 (if installed)

```bash
# Install PM2 if not already installed
npm install -g pm2

# Navigate to directory
cd /Users/yourox/AI-Workspace/tubedb-ui

# Start with PM2
pm2 start ecosystem.config.js --only tubedb-ui-dev
pm2 logs tubedb-ui-dev
```

## 🔍 Verify It's Working

1. **Open your browser** to: http://localhost:7000

2. **Check the console** - You should see:
   - "Loaded 60+ videos with 15000+ total segments"

3. **Check the UI** - You should see:
   - All your YouTube videos (60+)
   - Proper statistics in the Overview tab
   - Videos loading from the transcripts directory

## ✅ What's New

The server now:
- **ALWAYS runs on port 7000** (configured in package.json, .env.local, and all scripts)
- **Reads ALL videos** from `/data/transcripts/` (not just the batch file)
- **Shows 60+ videos** instead of just 3
- **Auto-kills** any process using port 7000 before starting

## 🛑 If Port 7000 is Still Busy

Run this to force-clear the port:
```bash
# Force kill anything on port 7000
sudo lsof -ti:7000 | xargs sudo kill -9

# Or use Activity Monitor on Mac:
# 1. Open Activity Monitor
# 2. Search for "node"
# 3. Quit any Node.js processes
```

## 📊 Expected Output

When successfully running, you'll see in the browser:
- **Total Videos**: 60+
- **Total Segments**: 15,000+
- **Avg Quality Score**: 85%
- **All videos** from your transcripts directory

## 🎯 Access Points

- **Frontend**: http://localhost:7000
- **API**: http://localhost:7000/api/batch
- **Health Check**: http://localhost:7000/api/batch (should return JSON with videos array)

---

**IMPORTANT**: The server is configured to ALWAYS use port 7000. All configurations have been updated:
- `package.json` → port 7000
- `.env.local` → PORT=7000
- All management scripts → enforce port 7000