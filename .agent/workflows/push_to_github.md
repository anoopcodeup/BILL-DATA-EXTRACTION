---
description: Push project to GitHub with authentication
---

### Prerequisites
- Ensure you have Git installed and configured.
- Have access to the repository `https://github.com/anoopcodeup/BILL-DATA-EXTRACTION.git`.

### Authentication Options
1. **GitHub CLI (Recommended)**
   ```bash
   # Install GitHub CLI if not already installed
   winget install --id GitHub.cli
   # Authenticate with your GitHub account
   gh auth login
   # Verify authentication
   gh auth status
   ```
   After successful login, you can push:
   ```bash
   git push -u origin main
   ```

2. **Personal Access Token (PAT)**
   - Generate a new token with `repo` scope from GitHub Settings → Developer settings → Personal access tokens.
   - Use the token when prompted for password, or embed it in the remote URL (be cautious as this stores the token in plain text):
   ```bash
   git remote set-url origin https://<YOUR_TOKEN>@github.com/anoopcodeup/BILL-DATA-EXTRACTION.git
   git push -u origin main
   ```

3. **SSH Keys**
   - Generate an SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   - Add the public key (`~/.ssh/id_ed25519.pub`) to GitHub under Settings → SSH and GPG keys.
   - Change the remote to use SSH:
   ```bash
   git remote set-url origin git@github.com:anoopcodeup/BILL-DATA-EXTRACTION.git
   git push -u origin main
   ```

### Verify Push
After pushing, visit the repository URL to confirm the latest commit appears.

### Troubleshooting
- If you see `remote: Permission denied` errors, double‑check the authentication method you used.
- Ensure your `.gitignore` does not accidentally exclude essential files.
- Run `git status` to confirm you are on the correct branch (`main`).
