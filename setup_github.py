#!/usr/bin/env python3
"""
Quick setup script for GitHub integration
Run this once to set up your repository for automated updates
"""

import subprocess
import sys
import webbrowser

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip(), result.stderr.strip(), 0
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def main():
    print("🚀 NH Energy Rates - GitHub Setup Assistant")
    print("=" * 50)
    print()
    
    print("This script will help you set up GitHub integration for automatic monthly updates.")
    print()
    
    # Get repository information
    repo_name = input("📝 Enter your GitHub repository name (e.g., 'nh-energy-rates'): ").strip()
    if not repo_name:
        repo_name = "nh-energy-rates"
        print(f"   Using default: {repo_name}")
    
    username = input("👤 Enter your GitHub username: ").strip()
    if not username:
        print("❌ GitHub username is required!")
        return False
    
    github_url = f"https://github.com/{username}/{repo_name}.git"
    
    print(f"\n🔧 Setting up repository: {github_url}")
    print()
    
    # Check if git is initialized
    stdout, stderr, code = run_command("git status")
    if code != 0:
        print("🔧 Initializing Git repository...")
        run_command("git init")
        run_command("git branch -M main")
    
    # Add remote origin
    print("🌐 Adding GitHub remote...")
    run_command("git remote remove origin")  # Remove if exists
    stdout, stderr, code = run_command(f"git remote add origin {github_url}")
    if code != 0:
        print(f"⚠️  Warning: {stderr}")
    
    # Create and switch to develop branch
    print("🌿 Setting up develop branch...")
    run_command("git checkout -b develop")
    
    # Initial commit and push
    print("📝 Creating initial commit...")
    run_command("git add .")
    run_command('git commit -m "Initial commit - NH Energy Rates Comparison Tool"')
    
    print("🚀 Pushing to GitHub...")
    stdout, stderr, code = run_command("git push -u origin develop")
    if code != 0:
        print(f"❌ Push failed: {stderr}")
        print("\n🔑 You may need to:")
        print("   1. Create the repository on GitHub first")
        print("   2. Set up authentication (Personal Access Token or SSH key)")
        print("   3. Run this script again")
        return False
    
    print("✅ Repository setup complete!")
    print()
    
    # Instructions for GitHub Pages
    github_repo_url = f"https://github.com/{username}/{repo_name}"
    github_pages_url = f"https://{username}.github.io/{repo_name}"
    
    print("📋 Next steps:")
    print(f"   1. Visit: {github_repo_url}/settings/pages")
    print("   2. Set Source to 'Deploy from a branch'")
    print("   3. Select 'develop' branch")
    print("   4. Click 'Save'")
    print(f"   5. Your site will be available at: {github_pages_url}")
    print()
    print("🤖 Automation:")
    print("   • GitHub Action will run monthly on the 1st")
    print("   • You can also run 'python auto_update_github.py' manually")
    print("   • Or double-click 'monthly_update.bat' on Windows")
    
    # Open browser to repository
    open_browser = input(f"\n🌐 Open GitHub repository in browser? (y/n): ").strip().lower()
    if open_browser in ['y', 'yes', '']:
        webbrowser.open(github_repo_url)
        webbrowser.open(f"{github_repo_url}/settings/pages")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
