# Reddit API Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create a Reddit App

1. **Go to Reddit Apps page**: https://www.reddit.com/prefs/apps
2. **Scroll to bottom** and click **"create app"** or **"create another app"**
3. **Fill in the form**:
   - **name**: `reddit-sentiment-analyzer` (or any name you want)
   - **App type**: Select **"script"** (important!)
   - **description**: `Historical sentiment analysis tool`
   - **about url**: Leave blank
   - **redirect uri**: `http://localhost:8080`
4. **Click "create app"**

### Step 2: Get Your Credentials

After creating, you'll see:

```
personal use script
<YOUR_CLIENT_ID>          ← This is your CLIENT_ID (14 characters)

secret
<YOUR_CLIENT_SECRET>      ← This is your CLIENT_SECRET (27 characters)
```

### Step 3: Add to .env File

Open `/Users/yourox/AI-Workspace/.env` and add:

```bash
# Reddit API
REDDIT_CLIENT_ID=<your_client_id_here>
REDDIT_CLIENT_SECRET=<your_client_secret_here>
REDDIT_USER_AGENT=python:reddit-sentiment-analyzer:v1.0
```

**Example**:
```bash
# Reddit API
REDDIT_CLIENT_ID=abc123XYZ45678
REDDIT_CLIENT_SECRET=xyz789ABC012345-LONG_SECRET
REDDIT_USER_AGENT=python:reddit-sentiment-analyzer:v1.0
```

### Step 4: Test Connection

Run:
```bash
python3 scripts/reddit_historical_collector.py --subreddit Entrepreneur --weeks 4
```

---

## Alternative: Use Environment Variables Directly

If you don't want to edit `.env`, you can set them temporarily:

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="python:reddit-sentiment-analyzer:v1.0"

python3 scripts/reddit_historical_collector.py --subreddit Entrepreneur --weeks 4
```

---

## Troubleshooting

### "401 Unauthorized" Error
- Double-check your CLIENT_ID and CLIENT_SECRET
- Make sure you selected "script" type (not "web app")
- Try creating a new app

### "429 Too Many Requests" Error
- Reddit API rate limit reached
- Wait 1 minute and try again
- The script has built-in rate limiting (2 seconds between weeks)

### "403 Forbidden" Error
- Reddit may be blocking your user agent
- Try changing REDDIT_USER_AGENT to something more descriptive
- Example: `REDDIT_USER_AGENT=macos:sentiment-tool:v1.0 (by /u/yourusername)`

---

## API Limits

**Reddit API Free Tier:**
- ✅ 100 requests per minute
- ✅ 10,000 requests per day
- ✅ No cost

**Our Usage:**
- ~10 requests per week of data
- 4 weeks = ~40 requests
- 52 weeks = ~520 requests
- 10 subreddits × 52 weeks = ~5,200 requests

**Time estimate:**
- Single subreddit (4 weeks): ~2 minutes
- Single subreddit (52 weeks): ~30 minutes
- All 10 Tier 1 subreddits (52 weeks): ~5-6 hours (with rate limiting)

---

## Security Notes

- ✅ Never commit `.env` to git (already in .gitignore)
- ✅ CLIENT_SECRET is sensitive - treat like a password
- ✅ You can revoke/regenerate credentials anytime at https://www.reddit.com/prefs/apps

---

## Next Steps After Setup

1. **Test with 4 weeks** on r/Entrepreneur:
   ```bash
   python3 scripts/reddit_historical_collector.py --subreddit Entrepreneur --weeks 4
   ```

2. **If successful, run full collection**:
   ```bash
   python3 scripts/reddit_historical_collector.py --tier1 --weeks 52
   ```

3. **View results**:
   ```bash
   ls -la data/reddit_snapshots/entrepreneur/
   cat data/reddit_snapshots/entrepreneur/entrepreneur_2024_w42.json | jq
   ```
