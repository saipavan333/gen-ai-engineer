# Publish to GitHub Pages — 3 ways

Your course is a static site, so hosting is free and permanent. Pick **one** method below. All three end at the same live URL:

```
https://YOUR-USERNAME.github.io/genai-engineer-course/
```

---

## Before you start (all methods)

1. Create a free account at **github.com** (remember your **username** — it's in your live URL).
2. In File Explorer, open `...\Tutorials\genai-engineer-course` and **delete the `.git_broken_delete_me` folder** (a failed attempt; harmless but tidy). You can delete `.gitignore` too.
3. Keep the folder structure as-is: `index.html` sits at the **top level** of the folder, next to `assets`, `track1`…`track16`, and the hidden `.nojekyll` file. Do **not** put it inside another subfolder.
4. The repository must be **Public** for free GitHub Pages.

> Tip: GitHub Pages is **case-sensitive** (unlike Windows). This site already uses all-lowercase paths that match its links, so you're fine — just don't rename folders to different capitalization.

---

## Method 1 — GitHub Desktop (easiest, no commands)

1. Install **GitHub Desktop** from **desktop.github.com** and sign in with your GitHub account.
2. **File → Add Local Repository →** browse to your `genai-engineer-course` folder → **Add**.
3. It says *"this directory does not appear to be a Git repository"* → click **"create a repository"** → leave defaults → **Create Repository**.
4. The **Changes** tab now lists every file. At the bottom, type a summary like `Initial commit` → click **Commit to main**.
5. Click **Publish repository** (top bar). **Uncheck "Keep this code private."** Keep the name `genai-engineer-course` → **Publish Repository**.
6. Go to **github.com → your repo → Settings → Pages**. Under **Source**, pick **Deploy from a branch**; set **Branch = main**, **folder = / (root)** → **Save**.
7. Wait ~1 minute, refresh the Pages settings page — it shows **"Your site is live at …"**. Open the link.

**Update later:** edit files → GitHub Desktop shows the changes → type a summary → **Commit to main** → **Push origin**. The live site refreshes automatically in a minute.

---

## Method 2 — VS Code (good if you'll also edit here)

1. Install **VS Code** (code.visualstudio.com) and **Git for Windows** (git-scm.com) — VS Code uses Git under the hood.
2. **File → Open Folder →** select `genai-engineer-course`.
3. Open the **Source Control** panel (the branch icon on the left, or `Ctrl+Shift+G`) → click **Initialize Repository**.
4. Click the **+** to stage all changes, type a message like `Initial commit`, then click the **✓ Commit**.
5. Click **Publish Branch** → VS Code asks you to **sign in to GitHub** (a browser popup) → choose **"Publish to GitHub public repository"** → confirm the name.
6. Go to **github.com → your repo → Settings → Pages → Source: Deploy from a branch → main → / (root) → Save**.
7. Wait ~1 minute → open your live URL.

**Update later:** edit files → in Source Control, stage → commit → click **Sync Changes** (or the ↻). Site updates automatically.

---

## Method 3 — PowerShell (learn real Git)

Best for practice, because these are the commands you'll use as an engineer.

1. Install **Git for Windows** (git-scm.com). Open **PowerShell** and check it works:
   ```powershell
   git --version
   ```
2. On **github.com**, click **New repository** (the **+** top-right). Name it `genai-engineer-course`, choose **Public**, **do NOT** add a README/.gitignore/license → **Create repository**. Copy the URL shown, e.g. `https://github.com/YOUR-USERNAME/genai-engineer-course.git`.
3. In PowerShell, run these (replace the URL with yours):
   ```powershell
   cd "$env:USERPROFILE\OneDrive\Desktop\Personal\Projects\AI\Tutorials\genai-engineer-course"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/genai-engineer-course.git
   git push -u origin main
   ```
   The first `push` opens a browser window to **sign in to GitHub** — approve it once.
4. Go to **github.com → your repo → Settings → Pages → Source: Deploy from a branch → main → / (root) → Save**.
5. Wait ~1 minute → open **`https://YOUR-USERNAME.github.io/genai-engineer-course/`**.

**Update later:** after editing files, from the same folder:
```powershell
git add .
git commit -m "describe what changed"
git push
```

---

## Which should I pick?

- **Just want it live fast, no commands →** GitHub Desktop.
- **You'll also edit the course in an editor →** VS Code.
- **You want to learn Git for your career →** PowerShell (Method 3). It's the most transferable skill.

---

## Troubleshooting

- **Page shows 404 for a minute or two:** normal right after enabling Pages — wait and refresh.
- **404 that won't go away:** re-check **Settings → Pages** shows **main / (root)**, and that `index.html` is at the **top level** of the repo (not inside a subfolder). Confirm the repo is **Public**.
- **Pages option is greyed out / asks for a paid plan:** the repo is Private. Make it Public (Settings → General → Danger Zone → Change visibility), or use a free account with a public repo.
- **A page loads but its diagrams/links are broken:** almost always a capitalization mismatch in a path. This site is verified all-lowercase, so it should not happen — just avoid renaming folders' case.
- **`git push` says authentication failed:** sign in through the browser popup, or install **Git Credential Manager** (bundled with Git for Windows) and retry.

---

## Faster non-GitHub option

If you ever want it live in ~2 minutes with no Git at all: go to **app.netlify.com/drop** and drag the whole `genai-engineer-course` folder onto the page. You get an instant public link; sign up free to keep it.

---

## Method 4 — Everything inside VS Code (integrated PowerShell terminal)

> Note: *GitHub Desktop* is a separate app and does **not** embed in VS Code. You don't need it — VS Code has Git + GitHub built in, plus a PowerShell terminal, so the whole publish happens in one window. This method uses the terminal (great Git practice) with the GUI as a shortcut where handy.

**One-time setup**
1. Install **Git for Windows** (git-scm.com) and **VS Code** (code.visualstudio.com). Restart VS Code after installing Git so `git` is on the PATH.
2. (Optional but smooth) In VS Code, click the **Accounts** icon (bottom-left) → **Sign in with GitHub** — this handles push authentication for you.

**Publish**
1. In File Explorer, delete the leftover `.git_broken_delete_me` folder.
2. VS Code → **File → Open Folder →** select `genai-engineer-course`.
3. Open the terminal: **Terminal → New Terminal** (or press `` Ctrl+` ``). In the terminal's top-right dropdown, make sure it's **PowerShell**.
4. Set your Git identity once (skip if you've done it before):
   ```powershell
   git config --global user.name "Pavan"
   git config --global user.email "uekpavanharish@gmail.com"
   ```
5. Initialize and commit — run these in the integrated terminal:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   ```
6. Create the GitHub repo and push. **Two options:**
   - **A · GitHub CLI (one command):** install GitHub CLI (cli.github.com), then:
     ```powershell
     gh auth login          # follow the browser prompt, first time only
     gh repo create genai-engineer-course --public --source=. --remote=origin --push
     ```
   - **B · Classic:** on github.com create a **New repository** named `genai-engineer-course`, **Public**, with **no** README, then in the terminal:
     ```powershell
     git remote add origin https://github.com/YOUR-USERNAME/genai-engineer-course.git
     git push -u origin main
     ```
     (A browser window opens to authorize the push the first time.)
   - **Shortcut:** you can instead click the **Source Control** panel → **Publish Branch / Publish to GitHub → public repository**, and VS Code does step 6 for you.
7. Turn on Pages: github.com → your repo → **Settings → Pages → Source: Deploy from a branch → main → / (root) → Save**.
8. Wait ~1 minute → open **`https://YOUR-USERNAME.github.io/genai-engineer-course/`**.

**Your update loop (all in VS Code):** edit a file → save → in the PowerShell terminal:
```powershell
git add .
git commit -m "describe the change"
git push
```
…or use the **Source Control** panel: stage (**+**), type a message, **✓ Commit**, then **Sync Changes**. The live site refreshes within a minute.

**If `git` isn't recognized** in the terminal: close and reopen VS Code (so it picks up Git's PATH entry). If it still fails, reinstall Git for Windows and keep the default "Add to PATH" option.
