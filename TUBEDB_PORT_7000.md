# TubeDB UI - Port 7000 Configuration

## ✅ IMPORTANT: Server ALWAYS Runs on Port 7000

The TubeDB UI has been configured to **ALWAYS** run on port **7000**. This ensures consistency across all services and APIs.

## 🚀 Quick Start Commands

### From anywhere in the terminal:
```bash
# Start the server
./tubedb-manager.sh start

# Stop the server
./tubedb-manager.sh stop

# Restart the server
./tubedb-manager.sh restart

# Check status
./tubedb-manager.sh status
```

### Alternative commands from AI-Workspace:
```bash
# Start
./start-tubedb.sh

# Stop
./stop-tubedb.sh

# Restart
./restart-tubedb.sh
```

## 📍 Access Points

- **Frontend UI**: http://localhost:7000
- **API Endpoint**: http://localhost:7000/api/batch
- **Videos Data**: http://localhost:7000/api/batch

## 🔧 Configuration Files Updated

All these files have been configured for port 7000:

1. **package.json** - Scripts updated to use port 7000
2. **.env.local** - PORT=7000 configured
3. **server.sh** - Management script with port enforcement
4. **ecosystem.config.js** - PM2 configuration for port 7000
5. **tubedb-manager.sh** - Master control script

## 🛠️ Port Management Features

### Automatic Port Clearing
If port 7000 is occupied by another process, the scripts will:
1. Detect the process using the port
2. Ask for confirmation (or auto-kill if it's a stuck process)
3. Clear the port before starting

### Port Lock Protection
The server scripts ensure that:
- Only one instance runs at a time
- Port 7000 is reserved for TubeDB UI
- Automatic cleanup of stuck processes

## 🔄 PM2 Process Management (Optional)

For production or persistent running:

```bash
# Start with PM2 (auto-restart on crash)
./tubedb-manager.sh start-pm2

# Start production build with PM2
./tubedb-manager.sh start-prod

# PM2 commands
pm2 status              # Check status
pm2 logs tubedb-ui-dev  # View logs
pm2 restart tubedb-ui-dev  # Restart
pm2 stop tubedb-ui-dev  # Stop
pm2 monit              # Real-time monitoring
```

## 📊 Verify Everything Works

Run status check:
```bash
./tubedb-manager.sh status
```

You should see:
```
✓ Server is running
  Port: 7000
  PID: [process_id]
  URL: http://localhost:7000
  Status: Responding
  Videos in DB: 60+
```

## 🐛 Troubleshooting

### If server won't start:
```bash
# Kill anything on port 7000
./tubedb-manager.sh kill-port

# Then start fresh
./tubedb-manager.sh start
```

### If you see "port already in use":
```bash
# Force kill and restart
lsof -ti:7000 | xargs kill -9
./tubedb-manager.sh start
```

### Check logs:
```bash
# Dev logs
tail -f tubedb-ui/server.log

# PM2 logs (if using PM2)
pm2 logs tubedb-ui-dev
```

## 🔐 Port 7000 Guarantee

The following mechanisms ensure port 7000:

1. **package.json** - Hardcoded port 7000 in npm scripts
2. **.env.local** - PORT environment variable set to 7000
3. **Shell scripts** - Force port 7000 and kill conflicting processes
4. **PM2 config** - Ecosystem file locks to port 7000
5. **Next.js** - Configured to respect PORT environment variable

## 📝 Notes

- The frontend will auto-reload on code changes
- All API calls are configured for localhost:7000
- The database reader now loads all transcripts automatically
- Videos are displayed from `/data/transcripts/*.json` files

## ✅ Summary

**Your TubeDB UI will ALWAYS run on port 7000**. Use any of the provided scripts to start/stop/restart the server, and it will automatically handle port management for you.

Access your UI at: **http://localhost:7000**