# GET CAPCUT-QUALITY VIDEOS (2 MINUTES SETUP)

## Step 1: Get FREE Replicate Token

1. **Go to:** https://replicate.com/signin
2. **Sign up** with Google (instant)
3. **Go to:** https://replicate.com/account/api-tokens
4. **Click:** "Create token"
5. **Copy** the token (starts with `r8_`)

## Step 2: Add Token to Your App

**Windows:**
1. Open `.env` file in your `Leads app` folder
2. Add this line:
   ```
   REPLICATE_API_TOKEN=r8_YOUR_TOKEN_HERE
   ```
3. Save the file
4. Restart your app

**That's it!** Your videos will now be:
- ✅ CapCut quality
- ✅ NO watermarks
- ✅ Professional backgrounds
- ✅ Natural emotions
- ✅ FREE

---

## If You Need Help:

Run this command in your `Leads app` folder:
```bash
.\venv\Scripts\python setup_replicate.py
```

It will guide you through setup automatically.
