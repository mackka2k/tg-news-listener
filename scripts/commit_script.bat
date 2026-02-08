@echo off
echo ==========================================================
echo 🚀 Preparing Telegram News Bot v2.0 Commit
echo ==========================================================

echo [1/4] Checking file status...
git status

echo [2/4] Adding files...
git add .

echo [3/4] Committing changes...
git commit -F COMMIT_MSG.txt

echo [4/4] Done! 
echo ==========================================================
echo ✅ Changes committed successfully!
echo Use 'git push' to upload to repository.
echo ==========================================================
pause
