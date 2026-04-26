# 📋 Startup Survey — Deploy Guide

## Files in this project
```
├── app.py                    ← Flask backend (PostgreSQL)
├── startup_survey_web.html   ← Your survey form
├── requirements.txt          ← Python dependencies
├── render.yaml               ← Auto-deploy config for Render
└── README.md
```

---

## 🚀 Deploy on Render.com (Free — 5 minutes)

### Step 1 — GitHub
1. Go to https://github.com and create a free account
2. Click **"New repository"** → name it `startup-survey` → **Create**
3. Upload ALL files from this zip into the repository

### Step 2 — Render
1. Go to https://render.com → Sign up free (use GitHub login)
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account → select your `startup-survey` repo
4. Render reads `render.yaml` and sets everything up automatically ✅
5. Click **"Apply"** → wait ~3 minutes

### Step 3 — Done! 🎉
You'll get a public URL like:
```
https://startup-survey.onrender.com        ← Share this link!
https://startup-survey.onrender.com/dashboard  ← View responses
https://startup-survey.onrender.com/export     ← Download all data as JSON
```

---

## ⚠️ Free Plan Notes
- The app **sleeps after 15 mins** of no traffic (first load takes ~30 seconds to wake up)
- PostgreSQL database is **free for 90 days** on Render, then $7/month
- For a permanent free database, use **Supabase** (https://supabase.com) — free forever

---

## 🗄️ Switch to Supabase (Free Forever)

1. Go to https://supabase.com → create free project
2. Go to **Settings → Database → Connection string → URI**
3. Copy the connection string
4. In Render dashboard → your service → **Environment** → set:
   ```
   DATABASE_URL = postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```
