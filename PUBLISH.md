# Publish your course online (free)

Your course is a **static site** — just HTML, CSS, and a little JavaScript. There's no server, database, build step, or API key. That means you can host it anywhere for **$0**, and it will work from any device, anywhere.

- **Entry point:** `index.html` (opens automatically)
- **What to upload:** the whole `genai-engineer-course` folder (all files, including the `assets`, `track1`…`track12`, `start-here` folders and the hidden `.nojekyll` file)
- **Total size:** ~2 MB

Pick **one** of the options below. If you just want it live in two minutes, use Option B.

---

## Option A — GitHub Pages  *(recommended: free, permanent, your own URL)*

Best if you want a lasting home you control. ~10 minutes, no command line needed.

1. Create a free account at **github.com**.
2. Click **New repository**. Name it `genai-engineer-course`, choose **Public**, and create it.
3. On the new repo page, click **Add file → Upload files**.
4. Open your `genai-engineer-course` folder, select **everything inside it** (so that `index.html` sits at the top level of the repo — *not* nested in another folder), and drag it into the upload area. Wait for it to finish, then click **Commit changes**.
5. Go to **Settings → Pages**. Under **Source**, choose **Deploy from a branch**; set **Branch** to `main` and folder to **/ (root)**; click **Save**.
6. Wait about a minute, then refresh. Your live URL appears at the top:
   **`https://YOUR-USERNAME.github.io/genai-engineer-course/`**

Share that link — anyone can open it.

- **Easier uploads/updates:** install **GitHub Desktop** (free app), drag your folder into the repo, and click *Commit → Push*. The site updates automatically each time.
- A `.nojekyll` file is already included so GitHub serves every file (including the SVG diagrams and logo) exactly as-is.

---

## Option B — Netlify Drop  *(fastest: drag-and-drop, ~2 minutes)*

1. Go to **app.netlify.com/drop**.
2. Drag your entire **`genai-engineer-course`** folder onto the page.
3. It uploads and instantly gives you a live URL like `cheerful-otter-1234.netlify.app`.
4. Create a free account to keep the site, rename it to something nicer, or add a custom domain.

- **To update later:** drag the folder onto the page again — or connect the site to a GitHub repo so it redeploys automatically whenever you change a file.

---

## Option C — Cloudflare Pages  *(free, very fast worldwide)*

Go to **pages.cloudflare.com**, then either connect a GitHub repo (Option A) or upload the folder directly. Free tier, global CDN, custom domains included.

---

## Optional: use your own domain

All three hosts let you attach a custom domain (e.g. `yourname.com`) for free. You only pay for the domain itself (~$10–15/year from any registrar) — the hosting stays free. Look for **"Custom domain"** in the site's settings on whichever host you chose.

---

## Quick comparison

| | Setup time | Keeps a permanent URL | Auto-updates | Custom domain |
|---|---|---|---|---|
| **GitHub Pages** | ~10 min | ✅ yes | ✅ (via repo) | ✅ free |
| **Netlify Drop** | ~2 min | ✅ (after free sign-up) | ✅ (if linked to repo) | ✅ free |
| **Cloudflare Pages** | ~5 min | ✅ yes | ✅ (via repo) | ✅ free |

**Recommendation:** want it live this minute → **Netlify Drop**. Want a professional, permanent home you fully control → **GitHub Pages**.

---

## Good to know

- It's completely self-contained — no API keys or backend — so nothing can "expire" and there are no running costs.
- The site works at any URL depth, so the GitHub Pages sub-path (`/genai-engineer-course/`) is fine.
- To make changes: edit the files locally, preview by double-clicking `index.html` in your browser, then re-upload/redeploy.
