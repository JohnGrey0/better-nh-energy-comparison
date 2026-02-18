"""
Automated GitHub Update Script for NH Energy Rates
This script generates fresh energy rate data and pushes it to GitHub automatically.
Run this monthly to keep the GitHub Pages site updated.
"""

import os
import subprocess
import sys
from datetime import datetime
from complete_energy_parser import main as generate_energy_data

def run_command(command, cwd=None):
    """
    Run a shell command and return the result
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            check=True
        )
        return result.stdout.strip(), result.stderr.strip(), 0
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_git_status():
    """
    Check if we're in a git repository and get status
    """
    stdout, stderr, code = run_command("git status --porcelain")
    if code != 0:
        print("❌ Error: Not in a git repository or git not available")
        print(f"Error: {stderr}")
        return False
    return True

def setup_git_if_needed():
    """
    Initialize git repository if needed and set up basic config
    """
    if not os.path.exists('.git'):
        print("🔧 Initializing Git repository...")
        
        # Initialize git repo
        stdout, stderr, code = run_command("git init")
        if code != 0:
            print(f"❌ Failed to initialize git: {stderr}")
            return False
        
        # Set up basic gitignore
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content.strip())
        
        print("✓ Git repository initialized")
    
    return True

def create_github_pages_structure():
    """
    Create the GitHub Pages structure with index.html pointing to our generated file
    """
    # Create a simple index.html that redirects to our generated file
    timestamp = datetime.now().strftime('%B %d, %Y')
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NH Energy Rate Comparison</title>
    <meta http-equiv="refresh" content="0; url=outputs/html/energy_rates.html">
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            margin: 0 auto;
        }}
        a {{
            color: #fff;
            text-decoration: none;
            font-weight: bold;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ NH Energy Rate Comparison</h1>
        <p>Redirecting to the latest energy rate comparison...</p>
        <p>If you are not redirected automatically, <a href="outputs/html/energy_rates.html">click here</a>.</p>
        <p><small>Last updated: {timestamp}</small></p>
    </div>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✓ Created GitHub Pages index.html")

def commit_and_push_changes():
    """
    Commit changes and push to develop branch
    """
    print("\n📝 Committing changes to Git...")
    
    # Check if we have any changes
    stdout, stderr, code = run_command("git status --porcelain")
    if not stdout.strip():
        print("ℹ️  No changes to commit")
        return True
    
    # Add all files
    stdout, stderr, code = run_command("git add .")
    if code != 0:
        print(f"❌ Failed to add files: {stderr}")
        return False
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_message = f"Auto-update energy rates data - {timestamp}"
    
    # Commit changes
    stdout, stderr, code = run_command(f'git commit -m "{commit_message}"')
    if code != 0:
        print(f"❌ Failed to commit: {stderr}")
        return False
    
    print(f"✓ Committed changes: {commit_message}")
    
    # Check if develop branch exists
    stdout, stderr, code = run_command("git branch --list develop")
    if not stdout.strip():
        # Create develop branch
        print("🌿 Creating develop branch...")
        stdout, stderr, code = run_command("git checkout -b develop")
        if code != 0:
            print(f"❌ Failed to create develop branch: {stderr}")
            return False
    else:
        # Switch to develop branch
        print("🌿 Switching to develop branch...")
        stdout, stderr, code = run_command("git checkout develop")
        if code != 0:
            print(f"❌ Failed to switch to develop branch: {stderr}")
            return False
    
    # Check if we have a remote origin
    stdout, stderr, code = run_command("git remote get-url origin")
    if code != 0:
        print("⚠️  No remote origin configured.")
        print("   To set up GitHub integration:")
        print("   1. Create a new repository on GitHub")
        print("   2. Run: git remote add origin https://github.com/yourusername/your-repo.git")
        print("   3. Run this script again")
        return True
    
    # Push to develop branch
    print("🚀 Pushing to GitHub develop branch...")
    stdout, stderr, code = run_command("git push -u origin develop")
    if code != 0:
        print(f"❌ Failed to push to GitHub: {stderr}")
        print("   You may need to authenticate with GitHub or check your remote URL")
        return False
    
    print("✅ Successfully pushed to GitHub develop branch!")
    return True

def main():
    """
    Main automation function
    """
    print("🤖 NH Energy Rates - GitHub Auto-Update Script")
    print("=" * 55)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Step 1: Generate fresh energy data
    print("\n🔌 Step 1: Generating fresh energy rate data...")
    try:
        generate_energy_data()
        print("✅ Energy data generated successfully!")
    except Exception as e:
        print(f"❌ Failed to generate energy data: {e}")
        return False
    
    # Step 2: Set up Git if needed
    print("\n🔧 Step 2: Setting up Git repository...")
    if not setup_git_if_needed():
        return False
    
    if not check_git_status():
        return False
    
    # Step 3: Create GitHub Pages structure
    print("\n🌐 Step 3: Setting up GitHub Pages structure...")
    create_github_pages_structure()
    
    # Step 4: Commit and push changes
    print("\n🚀 Step 4: Committing and pushing to GitHub...")
    if not commit_and_push_changes():
        return False
    
    print(f"\n🎉 Auto-update completed successfully!")
    print("=" * 55)
    print("📋 Next steps:")
    print("   • Enable GitHub Pages in your repository settings")
    print("   • Set source to 'develop' branch")
    print("   • Your site will be available at: https://yourusername.github.io/your-repo")
    print("   • Run this script monthly to keep data current")
    print("   • Consider setting up a GitHub Action for automatic monthly updates")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
