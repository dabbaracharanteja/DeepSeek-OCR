# Smart Learning Path — Deployable Repo (Frontend + Vercel Serverless API)

This repository is a deployable scaffold for the Smart Learning Path app:
- Frontend: Vite React + Tailwind (in `frontend/`)
- Serverless API: Vercel functions in `api/` (analyze endpoint uses OpenAI)

## What you need before deploy
1. OpenAI API key (create at https://platform.openai.com). Set as `OPENAI_API_KEY` in Vercel environment variables.
2. (Optional) MongoDB connection string if you add persistent storage; set as `MONGODB_URI`.

## Local testing (recommended)
1. Install Node.js (>=18) and npm.
2. From repo root, install frontend deps:
   ```bash
   cd frontend
   npm install
   ```
3. Start frontend dev server:
   ```bash
   npm run dev
   ```
4. To test the API locally you can use Vercel CLI or adapt to run with a local Node server. In production Vercel will run `api/*.js` as serverless functions.

## Deploy to Vercel (recommended)
1. Create a new project in Vercel and connect your GitHub repo (or use Vercel CLI).
2. Add Environment Variables under Project Settings:
   - `OPENAI_API_KEY` = your OpenAI API key
3. Push this repo to GitHub and import into Vercel, or use `vercel` CLI to deploy.
4. After deploy, open the provided Vercel URL. The frontend will call `/api/analyze` which is served by Vercel serverless.

## Notes & Security
- **Do not** commit your OpenAI API key into source control. Use Vercel's Environment Variables UI.
- The analyze endpoint expects a POST with JSON `{resume, role, country}`.
- The serverless function uses the official `openai` Node client and `chat.completions.create`. Update model & params as needed.

---
If you want, I can now:
- Zip this scaffold and provide the download link (so you can push to GitHub and deploy), or
- Guide you step-by-step to deploy it to Vercel and set env vars (I can provide exact CLI commands and Vercel settings).
