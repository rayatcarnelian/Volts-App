# How to Upload to GitHub

I have initialized the Git repository locally. Since I cannot access your logged-in browser or GitHub account directly, follow these steps to upload the code:

## STEP 1: Create Repository
1.  Go to [GitHub.com/new](https://github.com/new).
2.  **Repository Name:** `volts-app` (or any name you prefer).
3.  **Visibility:** Private (recommended for apps with keys, though keys are excluded from upload).
4.  Do **NOT** initialize with README, .gitignore, or License (I already created them).
5.  Click **Create repository**.

## STEP 2: Push Code
Copy the **HTTPS** URL from the next page (e.g., `https://github.com/rayatcarnelian/volts-app.git`).

Open your terminal in `e:\Leads app` and run:

```powershell
# Link local repo to GitHub
git remote add origin https://github.com/rayatcarnelian/volts-app.git

# Rename branch to main
git branch -M main

# Push code
git push -u origin main
```

*(If asked for username/password: use your GitHub username and a **Personal Access Token** as the password, or sign in via browser prompt if Git Credential Manager pops up).*

## ALTERNATIVE: Use GitHub CLI (I installed this for you!)
Since I successfully installed the GitHub CLI, you can use this easier method.

**Note:** If `gh` is not found, try using the full path: `& "C:\Program Files\GitHub CLI\gh.exe" ...`

1.  **Login**:
    ```powershell
    & "C:\Program Files\GitHub CLI\gh.exe" auth login
    ```
    - Select **GitHub.com** -> **HTTPS** -> **Yes** -> **Login with browser**.
    - Copy the code it gives you, press Enter to open browser, and paste the code.

2.  **Upload**:
    ```powershell
    & "C:\Program Files\GitHub CLI\gh.exe" repo create volts-app --private --source=. --remote=origin --push
    ```


## STEP 3: Secrets
Note that `.env` is **NOT** uploaded for security. You must manually add these secrets to your deployment platform (e.g., Streamlit Cloud) or copy the `.env` file manually if deploying to another server.
