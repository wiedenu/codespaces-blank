# Portfolio Website Management Guide
## John Wiedenheft Professional Portfolio

**Last Updated:** December 16, 2024  
**Website URL:** https://johnwiedenheft.com  
**GitHub Repository:** https://github.com/johnwiedenheft/johnwiedenheft-portfolio

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Requirements](#system-requirements)
3. [Opening Your Portfolio in Cursor](#opening-your-portfolio-in-cursor)
4. [Editing and Saving Process](#editing-and-saving-process)
5. [Committing Changes to GitHub](#committing-changes-to-github)
6. [Updating the Live Website](#updating-the-live-website)
7. [Common Tasks and Examples](#common-tasks-and-examples)
8. [Troubleshooting](#troubleshooting)
9. [Emergency Procedures](#emergency-procedures)
10. [Quick Reference Commands](#quick-reference-commands)

---

## Project Overview

### What This Is
Your professional portfolio website is a single-page HTML site designed to showcase your Marketing Operations expertise to potential employers and professional contacts. The site features:
- Clean, editorial design with serif typography
- Professional achievement highlights with metrics
- Experience timeline with detailed accomplishments
- Capabilities overview organized by expertise area
- Contact information and LinkedIn connection

### Technology Stack
- **Frontend:** Pure HTML/CSS/JavaScript (no framework)
- **Hosting:** GoDaddy cPanel hosting
- **Version Control:** Git + GitHub (private repository)
- **Code Editor:** Cursor (AI-powered code editor)
- **File:** Single `index.html` file (self-contained)

### File Locations
- **Local Project:** `~/Documents/johnwiedenheft-portfolio/`
- **Main File:** `index.html` (the only file you'll edit)
- **GitHub:** Private repository at https://github.com/johnwiedenheft/johnwiedenheft-portfolio
- **Live Website:** `public_html/index.html` on GoDaddy server

### Important Context
This site was designed to be **discreet** - it serves as a professional portfolio without explicitly signaling active job searching. The language and positioning can be shared with recruiters privately while remaining appropriate if discovered by current employers.

---

## System Requirements

### Software You Need
1. **Cursor** - AI-powered code editor
   - Download: https://cursor.sh
   - Free for personal use
   - Alternative: VS Code works too

2. **Git** - Version control system
   - Mac: Built-in (or install via Terminal)
   - Windows: https://git-scm.com
   - Verify installation: Open Terminal/Command Prompt, type `git --version`

3. **GitHub Account** - Cloud code storage
   - Sign up: https://github.com
   - Username: johnwiedenheft (or whatever you chose)
   - Repository: johnwiedenheft-portfolio (private)

4. **GoDaddy Account** - Web hosting
   - Login: https://godaddy.com
   - Hosting: cPanel hosting (not Managed WordPress)
   - Domain: johnwiedenheft.com

### Access You Need
- ✅ GitHub login credentials
- ✅ GoDaddy account login
- ✅ Local copy of project folder on your computer

---

## Opening Your Portfolio in Cursor

### Method 1: Using Cursor (Recommended)

**Step 1: Launch Cursor**
- Mac: Open Cursor from Applications
- Windows: Open Cursor from Start Menu

**Step 2: Open Project Folder**
1. In Cursor: **File** → **Open Folder** (or press `Cmd+O` on Mac / `Ctrl+O` on Windows)
2. Navigate to: **Documents** → **johnwiedenheft-portfolio**
3. Click **"Open"** or **"Select Folder"**

**What You'll See:**
- Sidebar on left shows your project files
- `index.html` should be visible
- `.gitignore` file (hidden, but there)
- `.git` folder (hidden, but tracking your changes)

**Step 3: Open index.html**
1. In the left sidebar (File Explorer), click on **`index.html`**
2. The file will open in the main editor window
3. You'll see all the HTML code for your website

### Method 2: Using Terminal (Alternative)

**Open Terminal/Command Prompt:**
- Mac: Press `Cmd+Space`, type "Terminal", press Enter
- Windows: Press Windows key, type "cmd", press Enter

**Navigate to project and open Cursor:**
```bash
cd ~/Documents/johnwiedenheft-portfolio
cursor .
```

**What this does:**
- `cd ~/Documents/johnwiedenheft-portfolio` = Change to your project folder
- `cursor .` = Open Cursor in current folder (the dot means "this folder")

---

## Editing and Saving Process

### Understanding the File Structure

Your `index.html` file contains everything in one file:
- HTML structure
- CSS styling (in `<style>` tags)
- JavaScript functionality (in `<script>` tags)
- Google Fonts imports
- All content

**Key Sections to Know:**
```html
<head>
  <!-- Meta info, fonts, and ALL CSS styling -->
  <style>
    /* All your styles are here between these tags */
  </style>
</head>

<body>
  <!-- Navigation -->
  <nav>...</nav>
  
  <!-- Hero Section -->
  <section id="hero" class="hero">...</section>
  
  <!-- About Section -->
  <section id="about">...</section>
  
  <!-- Experience Section -->
  <section id="experience">...</section>
  
  <!-- Capabilities Section -->
  <section id="capabilities">...</section>
  
  <!-- Contact Section -->
  <section id="contact">...</section>
  
  <!-- Footer -->
  <footer>...</footer>
  
  <!-- JavaScript at bottom -->
  <script>
    // All functionality code here
  </script>
</body>
```

### Making Edits

#### Using Cursor's Find Feature
**To find specific content:**
1. Press `Cmd+F` (Mac) or `Ctrl+F` (Windows)
2. Type what you're looking for (e.g., "Director, Marketing Operations")
3. Cursor will highlight all matches
4. Use arrows to jump between matches

#### Using Cursor AI (Powerful!)
Cursor has built-in AI that can help you make changes:

**Method 1 - Chat with AI:**
1. Press `Cmd+L` (Mac) or `Ctrl+L` (Windows) to open AI chat
2. Ask: "Find the experience section and add a new achievement card about [your accomplishment]"
3. Review the suggested changes
4. Accept or modify as needed

**Method 2 - Inline Edit:**
1. Select the text you want to modify
2. Press `Cmd+K` (Mac) or `Ctrl+K` (Windows)
3. Type your instruction: "Change this to say [new text]"
4. Cursor will suggest the edit
5. Accept with `Tab` or reject with `Esc`

#### Manual Editing Tips
- **Line numbers:** Visible on the left - use them to navigate
- **Syntax highlighting:** Colors help you see HTML tags, CSS properties, etc.
- **Auto-complete:** Start typing and Cursor suggests completions
- **Multi-cursor:** Hold `Cmd` (Mac) or `Ctrl` (Windows) and click to edit multiple places at once

### Saving Your Changes

**Save the file:**
- Press `Cmd+S` (Mac) or `Ctrl+S` (Windows)
- Or: **File** → **Save**
- Unsaved changes show a dot next to filename in tab

**Auto-save:**
Cursor auto-saves by default, but manually saving ensures everything is captured.

### Testing Your Changes Locally

**Before uploading to the live site, test locally:**

1. In Cursor, right-click on `index.html` in the sidebar
2. Select **"Open in Browser"** or **"Reveal in Finder/Explorer"**
3. Double-click the file to open in your default browser
4. Review your changes
5. Test navigation links
6. Check on different browser window sizes (responsive design)

**Browser Developer Tools (Optional but Useful):**
- Press `F12` or right-click → **"Inspect"**
- Use to check console for errors
- Test mobile view using device toolbar

---

## Committing Changes to GitHub

### Why Commit?
- **Version history:** Save snapshots of your work
- **Cloud backup:** Your code is safe on GitHub
- **Rollback capability:** Can undo any change
- **Professional practice:** How developers track changes

### Before You Commit: Check What Changed

**In Terminal:**
```bash
cd ~/Documents/johnwiedenheft-portfolio
git status
```

**What you'll see:**
```
On branch main
Changes not staged for commit:
  modified:   index.html
```

**To see the actual changes:**
```bash
git diff
```

This shows line-by-line what changed (+ for additions, - for deletions)

### Method 1: Committing Via Terminal (Traditional)

**Step 1: Stage Your Changes**
```bash
git add index.html
```
Or stage everything:
```bash
git add .
```

**What this does:** Prepares files for commit (like putting them in a box to mail)

**Step 2: Commit with a Message**
```bash
git commit -m "Updated experience section with Q4 achievements"
```

**Message Best Practices:**
- Be descriptive but concise
- Use present tense: "Add" not "Added"
- Examples:
  - ✅ "Add new certification to capabilities section"
  - ✅ "Update contact email address"
  - ✅ "Fix typo in hero section"
  - ❌ "Changes"
  - ❌ "Update"

**Step 3: Push to GitHub**
```bash
git push
```

**What this does:** Uploads your commit to GitHub (like mailing the box)

**If prompted for credentials:**
- Username: Your GitHub username
- Password: Use a Personal Access Token (not your actual password)
- GitHub will guide you through creating a token if needed

### Method 2: Committing Via Cursor (Visual, Easier)

**Step 1: Open Source Control Panel**
1. Click the **Source Control** icon in left sidebar (looks like a branching diagram)
2. Or press `Ctrl+Shift+G` (Windows) or `Cmd+Shift+G` (Mac)

**Step 2: Review Changes**
- You'll see `index.html` listed under "Changes"
- Click on it to see a visual diff (side-by-side comparison)
- Green = additions
- Red = deletions

**Step 3: Stage Changes**
- Click the **"+"** icon next to `index.html`
- Or click **"+"** next to "Changes" to stage everything
- File moves to "Staged Changes" section

**Step 4: Write Commit Message**
1. In the text box at top, type your commit message
2. Example: "Add new achievement card for Agile implementation"

**Step 5: Commit**
- Click the **checkmark (✓)** button above the message box
- Or press `Cmd+Enter` (Mac) / `Ctrl+Enter` (Windows)

**Step 6: Push to GitHub**
- Click the **"..."** menu (three dots)
- Select **"Push"**
- Or click the cloud upload icon in the status bar

### Verifying Your Commit on GitHub

**Check that it worked:**
1. Go to https://github.com/johnwiedenheft/johnwiedenheft-portfolio
2. Sign in if needed
3. You should see your latest commit message at the top
4. Click on "commits" to see full history
5. Click on a commit to see what changed

---

## Updating the Live Website

After committing to GitHub, your code is backed up but NOT yet live. You need to upload to GoDaddy.

### Step 1: Access GoDaddy cPanel

**Login to GoDaddy:**
1. Go to https://godaddy.com
2. Sign in with your account
3. Go to **"My Products"**
4. Find your hosting plan
5. Click **"cPanel Admin"** or **"Manage"**

### Step 2: Open File Manager

**In cPanel:**
1. Scroll to the **"Files"** section
2. Click **"File Manager"**
3. A new tab will open with your file browser

### Step 3: Navigate to public_html

**In File Manager:**
1. Look at the left sidebar (directory tree)
2. Click on **`public_html`** folder
3. This is your website's root directory
4. You should see your current `index.html` file

### Step 4: Upload New Version

**Option A - Replace via Upload (Recommended):**

1. In the File Manager toolbar, click **"Upload"**
2. A new upload interface opens
3. Click **"Select File"** 
4. Navigate to: `Documents/johnwiedenheft-portfolio/`
5. Select `index.html`
6. Click **"Open"**
7. Upload will start automatically
8. When prompted: **"File exists, do you want to overwrite?"**
9. Click **"Yes"** or **"Overwrite"**
10. Close the upload window

**Option B - Delete and Upload (Alternative):**

1. In File Manager, select the old `index.html` (click checkbox)
2. Click **"Delete"** button in toolbar
3. Confirm deletion
4. Now `public_html` has no index.html
5. Click **"Upload"** and upload your new `index.html`

### Step 5: Verify the Update

**Test your live site:**
1. Open a new browser tab
2. Go to https://johnwiedenheft.com
3. **Hard refresh** to bypass cache:
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + F5`
4. Verify your changes are visible
5. Test all navigation links
6. Check on mobile (or use browser dev tools)

**If you don't see changes:**
- Wait 1-2 minutes (server cache)
- Try incognito/private browsing mode
- Clear browser cache
- Try from a different device/network

### Step 6: Final Check

**Verify everything works:**
- ✅ All sections load correctly
- ✅ Navigation links scroll to right sections
- ✅ Contact links work (email, LinkedIn)
- ✅ Mobile responsive (test by resizing browser)
- ✅ No console errors (F12 → Console tab)

---

## Common Tasks and Examples

### Task 1: Adding a New Achievement

**Scenario:** You completed a major project and want to add it to your experience section.

**Steps:**

1. **Open project in Cursor**
2. **Find the experience section:**
   - Press `Cmd+F` / `Ctrl+F`
   - Search for: "achievement-card"
3. **Copy an existing achievement card:**
   ```html
   <div class="achievement-card">
       <div class="achievement-label">Category</div>
       <div class="achievement-title">Title</div>
       <div class="achievement-description">
           Description with <span class="achievement-stat">metric</span>
       </div>
   </div>
   ```
4. **Paste it where you want the new one**
5. **Edit the content:**
   - Change label (e.g., "Process Improvement")
   - Change title (e.g., "Lead Scoring Optimization")
   - Change description and metric
6. **Save** (`Cmd+S` / `Ctrl+S`)
7. **Test locally** (open in browser)
8. **Commit to GitHub:**
   ```bash
   git add index.html
   git commit -m "Add lead scoring optimization achievement"
   git push
   ```
9. **Upload to GoDaddy**

### Task 2: Updating Your Contact Information

**Scenario:** You got a new phone number or email.

**Steps:**

1. **Open project in Cursor**
2. **Find the contact section:**
   - Search for: `id="contact"`
3. **Locate the contact methods:**
   ```html
   <div class="contact-item">
       <span class="contact-label">Email:</span>
       <a href="mailto:johnwiedenheft@gmail.com">johnwiedenheft@gmail.com</a>
   </div>
   ```
4. **Update the email/phone:**
   - Change the `mailto:` link
   - Change the displayed text
5. **Save, test, commit, and upload**

### Task 3: Adding a New Certification

**Scenario:** You earned a new certification (e.g., Salesforce Admin).

**Steps:**

1. **Find the capabilities or education section**
2. **Add to relevant list:**
   ```html
   <span class="tech-badge">Salesforce Admin Certified</span>
   ```
3. **Or update the education section:**
   ```html
   <p>
       <span style="font-weight: bold;">HubSpot Certified (5x)</span>
       • Marketing Software, Sales Software, Content Hub, Inbound Marketing, Platform Enablement
   </p>
   ```
4. **Save, test, commit, and upload**

### Task 4: Changing Colors/Styling

**Scenario:** You want to adjust the accent color.

**Steps:**

1. **Find the CSS variables** (near top of file):
   ```css
   :root {
       --color-accent: #2c5f6f;
       --color-accent-light: #3d7a8c;
       /* other variables */
   }
   ```
2. **Change the hex color codes:**
   - Use a color picker tool online
   - Example: Change `#2c5f6f` to `#1a4d5c` for darker teal
3. **Save and test locally** to see the change
4. **If you like it:** Commit and upload
5. **If you don't:** Press `Cmd+Z` / `Ctrl+Z` to undo

### Task 5: Updating Job Status

**Scenario:** You got a new job and want to update your current role.

**Steps:**

1. **Find the experience section**
2. **Update the current role dates:**
   ```html
   <div class="experience-meta">
       <span class="experience-company">GreatAmerica Financial Services</span>
       • Cedar Rapids, IA • 2019 – Present
   </div>
   ```
   Change "Present" to end date: "2019 – 2025"
3. **Add your new role** at the top of the experience section
4. **Update the hero section** if needed (title, description)
5. **Update About section** to reflect new position
6. **Save, test, commit, and upload**

---

## Troubleshooting

### Problem: Can't Open Project in Cursor

**Symptom:** Cursor says "folder not found" or shows empty project.

**Solutions:**
1. **Verify folder location:**
   - Open Finder (Mac) or File Explorer (Windows)
   - Navigate to Documents
   - Confirm `johnwiedenheft-portfolio` folder exists
   - If not there, check Desktop or Downloads

2. **Re-download from GitHub:**
   ```bash
   cd ~/Documents
   git clone https://github.com/johnwiedenheft/johnwiedenheft-portfolio.git
   ```

3. **Check folder permissions:**
   - Right-click folder → Get Info (Mac) or Properties (Windows)
   - Ensure you have read/write access

### Problem: Git Commands Don't Work

**Symptom:** Terminal says "git: command not found"

**Solutions:**
1. **Verify Git is installed:**
   ```bash
   git --version
   ```
   
2. **Install Git:**
   - Mac: `xcode-select --install`
   - Windows: Download from https://git-scm.com

3. **Check PATH environment variable** (advanced)

### Problem: GitHub Push Fails with Authentication Error

**Symptom:** "Authentication failed" or "Permission denied"

**Solutions:**
1. **Use Personal Access Token instead of password:**
   - Go to GitHub.com → Settings → Developer Settings
   - Generate new token with "repo" permissions
   - Use token as password when prompted

2. **Set up SSH keys** (alternative, more advanced):
   - Follow GitHub's SSH setup guide
   - More secure, no password prompts

3. **Check repository access:**
   - Verify you own the repository
   - Check if repository is private vs public

### Problem: Changes Not Showing on Live Site

**Symptom:** Uploaded new file but website still shows old content.

**Solutions:**
1. **Hard refresh browser:**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + F5`
   - Or try incognito/private mode

2. **Verify file was uploaded:**
   - Go to GoDaddy File Manager
   - Check `index.html` file date/time
   - Should match your recent upload

3. **Check file location:**
   - Ensure uploaded to `public_html` not a subfolder
   - File must be named `index.html` exactly (lowercase)

4. **Wait for server cache to clear:**
   - Can take 5-15 minutes
   - Try from different device/network

5. **Check for .htaccess redirects:**
   - In File Manager, enable "Show Hidden Files"
   - Look for `.htaccess` in public_html
   - If exists and looks suspicious, delete or rename it

### Problem: Cursor AI Not Working

**Symptom:** Cmd+K or Cmd+L doesn't do anything.

**Solutions:**
1. **Check Cursor subscription:**
   - Free tier has usage limits
   - May need to sign up or upgrade

2. **Check internet connection:**
   - AI features require internet

3. **Restart Cursor:**
   - Quit completely and reopen

4. **Check for updates:**
   - Help → Check for Updates

### Problem: Made a Mistake and Need to Undo

**Symptom:** Accidentally deleted or changed something important.

**Solutions:**

**If you haven't saved yet:**
1. Press `Cmd+Z` / `Ctrl+Z` repeatedly to undo
2. Or close file without saving, reopen to get last saved version

**If you saved but haven't committed:**
1. In Terminal:
   ```bash
   git checkout index.html
   ```
   This reverts file to last committed version

**If you already committed:**
1. Find the commit you want to go back to:
   ```bash
   git log
   ```
2. Copy the commit ID (long string of letters/numbers)
3. Revert to that version:
   ```bash
   git checkout COMMIT_ID index.html
   ```
4. Or use Cursor's Source Control panel to browse history

**If you already uploaded to live site:**
1. Revert locally (above steps)
2. Re-upload the corrected version to GoDaddy

---

## Emergency Procedures

### Emergency 1: Website Is Down or Broken

**Immediate Action:**

1. **Don't panic** - you have backups in Git
2. **Check GitHub for last working version:**
   - Go to repository
   - Click "commits"
   - Find last known good commit
   - Download that version of `index.html`
3. **Upload the working version to GoDaddy immediately**
4. **Debug the issue later** in your local copy

### Emergency 2: Lost Local Files

**Recovery Steps:**

1. **Clone from GitHub:**
   ```bash
   cd ~/Documents
   git clone https://github.com/johnwiedenheft/johnwiedenheft-portfolio.git
   cd johnwiedenheft-portfolio
   ```
2. **You now have all your files back from GitHub**
3. **Continue working as normal**

### Emergency 3: Accidentally Deleted GitHub Repository

**Recovery Steps:**

1. **Check GitHub trash/deleted repos** (30-day recovery window)
2. **If truly gone:**
   - You still have local copy
   - Create new repository on GitHub
   - Push local copy to new repo:
     ```bash
     git remote remove origin
     git remote add origin https://github.com/johnwiedenheft/NEW-REPO-NAME.git
     git push -u origin main
     ```

### Emergency 4: Website Hacked or Defaced

**Immediate Action:**

1. **Change GoDaddy account password immediately**
2. **Download the compromised index.html for investigation**
3. **Upload your last known good version from GitHub**
4. **Contact GoDaddy support** about security
5. **Check for additional malicious files in public_html**
6. **Enable two-factor authentication on GoDaddy**

### Emergency 5: Need to Revert to Version from Weeks Ago

**Steps:**

1. **Find the commit in GitHub:**
   - Go to repository → Commits
   - Browse by date
   - Click on the commit to see changes
   
2. **Locally revert to that version:**
   ```bash
   git log --oneline
   # Find the commit ID you want
   git checkout COMMIT_ID index.html
   git commit -m "Revert to version from [date]"
   git push
   ```

3. **Upload to GoDaddy**

---

## Quick Reference Commands

### Essential Terminal Commands

```bash
# Navigate to project
cd ~/Documents/johnwiedenheft-portfolio

# Check status
git status

# See what changed
git diff

# Stage changes
git add index.html
git add .                    # Stage everything

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push

# Pull from GitHub (get latest changes)
git pull

# See commit history
git log
git log --oneline            # Compact view

# Revert file to last commit
git checkout index.html

# Open Cursor from Terminal
cursor .
```

### Cursor Keyboard Shortcuts

**Mac / Windows**

| Action | Mac | Windows |
|--------|-----|---------|
| Save file | `Cmd+S` | `Ctrl+S` |
| Find | `Cmd+F` | `Ctrl+F` |
| Replace | `Cmd+H` | `Ctrl+H` |
| Open AI chat | `Cmd+L` | `Ctrl+L` |
| Inline edit | `Cmd+K` | `Ctrl+K` |
| Command palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Source control | `Cmd+Shift+G` | `Ctrl+Shift+G` |
| Open folder | `Cmd+O` | `Ctrl+O` |
| Close file | `Cmd+W` | `Ctrl+W` |
| Undo | `Cmd+Z` | `Ctrl+Z` |
| Redo | `Cmd+Shift+Z` | `Ctrl+Y` |

### Git Commit Message Templates

```bash
# Adding new content
git commit -m "Add [what you added]"
# Examples:
git commit -m "Add Q4 achievement card to experience section"
git commit -m "Add Salesforce certification to capabilities"

# Updating existing content
git commit -m "Update [what you updated]"
# Examples:
git commit -m "Update contact email address"
git commit -m "Update hero section copy for clarity"

# Fixing issues
git commit -m "Fix [what you fixed]"
# Examples:
git commit -m "Fix typo in about section"
git commit -m "Fix broken LinkedIn link"

# Styling changes
git commit -m "Adjust [what styling]"
# Examples:
git commit -m "Adjust accent color to darker teal"
git commit -m "Adjust spacing in experience cards"
```

### Common HTML Sections to Edit

```html
<!-- Hero Section - Main headline and intro -->
<section id="hero" class="hero">
    <h1>Your main headline</h1>
    <p class="hero-intro">Your introduction...</p>
</section>

<!-- About Section - Your story -->
<section id="about">
    <p>Your professional narrative...</p>
</section>

<!-- Experience Section - Job history and achievements -->
<section id="experience">
    <div class="experience-item">
        <h3 class="experience-title">Job Title</h3>
        <!-- Achievement cards here -->
    </div>
</section>

<!-- Capabilities Section - Skills and expertise -->
<section id="capabilities">
    <div class="capability-category">
        <h3 class="capability-title">Category Name</h3>
        <ul class="capability-list">
            <li>Skill or capability</li>
        </ul>
    </div>
</section>

<!-- Contact Section - How to reach you -->
<section id="contact">
    <a href="mailto:your@email.com">your@email.com</a>
</section>
```

---

## Maintenance Schedule

### Weekly
- ✅ Pull latest changes from GitHub (if working on multiple devices)
- ✅ Check that live site is still functioning correctly
- ✅ Review any analytics or feedback

### Monthly
- ✅ Review content for accuracy and relevance
- ✅ Update achievements with new metrics or projects
- ✅ Check all external links (LinkedIn, etc.)
- ✅ Test site on different browsers/devices

### Quarterly
- ✅ Major content review and updates
- ✅ Add new certifications or skills
- ✅ Refresh metrics with latest data
- ✅ Consider design tweaks or improvements

### As Needed
- ✅ Update when changing jobs
- ✅ Add major achievements as they happen
- ✅ Adjust positioning based on job search focus
- ✅ Fix any bugs or issues discovered

---

## Additional Resources

### Learning Resources
- **Git Basics:** https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- **HTML Reference:** https://developer.mozilla.org/en-US/docs/Web/HTML
- **CSS Reference:** https://developer.mozilla.org/en-US/docs/Web/CSS
- **Cursor Documentation:** https://cursor.sh/docs

### Tools
- **Color Picker:** https://htmlcolorcodes.com
- **Google Fonts:** https://fonts.google.com
- **Can I Use (Browser Compatibility):** https://caniuse.com
- **HTML Validator:** https://validator.w3.org

### Support Contacts
- **GoDaddy Support:** https://www.godaddy.com/contact-us
- **GitHub Support:** https://support.github.com
- **Cursor Support:** https://cursor.sh/support

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2024-12-16 | 1.0 | Initial documentation created |

---

## Notes Section

**Use this space to track your own updates and customizations:**

```
Date: ___________
Changes Made: _________________________________________________
Commit Message: _______________________________________________
Deployed to Live: Yes / No
Issues Encountered: ___________________________________________

Date: ___________
Changes Made: _________________________________________________
Commit Message: _______________________________________________
Deployed to Live: Yes / No
Issues Encountered: ___________________________________________

Date: ___________
Changes Made: _________________________________________________
Commit Message: _______________________________________________
Deployed to Live: Yes / No
Issues Encountered: ___________________________________________
```

---

**End of Guide**

*Last Updated: December 16, 2024*  
*Maintained by: John Wiedenheft*  
*For questions or issues, refer to troubleshooting section or contact relevant support.*
