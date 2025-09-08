#!/usr/bin/env python3
"""
Force Railway deployment by making a small change to trigger redeploy
"""

def force_deploy():
    """Add a comment to main.py to trigger Railway redeploy"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the first line and add a comment
    lines = content.split('\n')
    if len(lines) > 0:
        # Add a timestamp comment at the top
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add comment after the first line (or before if it's a shebang)
        if lines[0].startswith('#!'):
            lines.insert(1, f"# Score-based scanner deployed: {timestamp}")
        else:
            lines.insert(0, f"# Score-based scanner deployed: {timestamp}")
    
    # Write back
    new_content = '\n'.join(lines)
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print(f"✅ Added deployment timestamp: {timestamp}")
    print("🚀 This should trigger Railway to redeploy with the latest changes")
    return True

if __name__ == "__main__":
    force_deploy()