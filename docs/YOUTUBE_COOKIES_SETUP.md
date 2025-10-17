# YouTube Cookies Setup for Rate Limit Bypass

## Why Cookies?

YouTube may rate-limit or block transcript API requests from your IP. Using authenticated browser cookies helps bypass these restrictions by making requests appear as if they're coming from a logged-in user.

## Setup Instructions

### Option 1: Browser Extension (Easiest)

1. **Install "Get cookies.txt LOCALLY" extension:**
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. **Export YouTube cookies:**
   - Go to https://www.youtube.com (make sure you're logged in)
   - Click the extension icon
   - Click "Export" to download `cookies.txt`

3. **Move the file:**
   ```bash
   mv ~/Downloads/youtube.com_cookies.txt /Users/yourox/AI-Workspace/.youtube_cookies.txt
   ```

### Option 2: Manual Cookie Extraction

1. **Get cookies from browser:**
   - Go to https://www.youtube.com
   - Open DevTools (F12)
   - Go to Application/Storage > Cookies
   - Copy all cookies

2. **Create cookies file:**
   ```bash
   # Create file in Netscape format
   touch /Users/yourox/AI-Workspace/.youtube_cookies.txt
   ```

3. **Format (Netscape HTTP Cookie File):**
   ```
   # Netscape HTTP Cookie File
   .youtube.com	TRUE	/	TRUE	2147483647	VISITOR_INFO1_LIVE	<value>
   .youtube.com	TRUE	/	FALSE	2147483647	YSC	<value>
   ```

### Option 3: Use yt-dlp to extract cookies

```bash
# Export cookies from your browser
yt-dlp --cookies-from-browser chrome --cookies /Users/yourox/AI-Workspace/.youtube_cookies.txt https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Or from Firefox
yt-dlp --cookies-from-browser firefox --cookies /Users/yourox/AI-Workspace/.youtube_cookies.txt https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Verify Setup

```bash
# Check if file exists
ls -la /Users/yourox/AI-Workspace/.youtube_cookies.txt

# Test extraction with cookies
python3 scripts/parallel_transcriber.py 1
```

## Security Notes

- ⚠️ Keep `.youtube_cookies.txt` private (already in `.gitignore`)
- 🔄 Cookies expire - refresh them every few weeks
- 🔒 These cookies provide access to your YouTube account

## Alternative: Wait for Rate Limit Reset

If you don't want to use cookies, simply wait 30-60 minutes for YouTube's rate limit to reset, then retry:

```bash
# Retry the failed video after waiting
python3 scripts/parallel_transcriber.py 1
```

## Troubleshooting

**Still getting rate limited?**
1. Refresh your cookies (they may have expired)
2. Try a different browser for cookie extraction
3. Wait longer between requests (add delays in the script)
4. Use a VPN to change your IP address

**Cookies not working?**
1. Make sure you're logged into YouTube when exporting
2. Verify the file format is correct (Netscape format)
3. Check file permissions: `chmod 600 .youtube_cookies.txt`
