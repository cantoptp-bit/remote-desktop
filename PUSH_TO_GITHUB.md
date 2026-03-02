# Push to GitHub

Your repo is ready. Do one of the following.

## Option A: Create repo on GitHub, then push

1. **Create a new repository** on [github.com/new](https://github.com/new):
   - Name it e.g. `remote-desktop`
   - Leave it empty (no README, no .gitignore)

2. **Add the remote and push** (replace `YOUR_USERNAME` with your GitHub username):

   ```bash
   cd /Users/michael/test/remote-desktop
   git remote add origin https://github.com/YOUR_USERNAME/remote-desktop.git
   git branch -M main
   git push -u origin main
   ```

   If you use SSH:
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/remote-desktop.git
   git push -u origin main
   ```

## Option B: Use GitHub CLI (after logging in)

```bash
gh auth login
cd /Users/michael/test/remote-desktop
gh repo create remote-desktop --private --source=. --push
```

Use `--public` instead of `--private` if you want the repo public.
