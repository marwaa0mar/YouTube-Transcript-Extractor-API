#!/usr/bin/env python3
"""
Helper script to generate fresh YouTube cookies
Run this script to extract cookies from your browser and save them to cookies.txt
"""

import subprocess
import sys
import os

def generate_cookies():
    """Generate fresh cookies from browser"""
    print("🔐 YouTube Cookie Generator")
    print("=" * 40)
    
    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp not found. Please install it first:")
        print("   pip install yt-dlp")
        return False
    
    print("✅ yt-dlp found")
    print("\n📋 Available browsers:")
    print("1. Chrome (may need to be closed)")
    print("2. Firefox")
    print("3. Edge")
    print("4. Safari")
    
    browser_choice = input("\nSelect your browser (1-4): ").strip()
    
    browser_map = {
        "1": "chrome",
        "2": "firefox", 
        "3": "edge",
        "4": "safari"
    }
    
    if browser_choice not in browser_map:
        print("❌ Invalid choice")
        return False
    
    browser = browser_map[browser_choice]
    
    if browser == "chrome":
        print("\n⚠️  IMPORTANT: Chrome may need to be completely closed!")
        print("   If you get permission errors, close all Chrome windows and try again.")
        print("   Alternative: Use Firefox or Edge instead.")
        
        proceed = input("\nContinue with Chrome? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Try Firefox or Edge instead!")
            return False
    
    print(f"\n🔄 Extracting cookies from {browser}...")
    print("⚠️  Make sure you're logged into YouTube in your browser!")
    
    try:
        # Extract cookies and save to cookies.txt
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", browser,
            "--cookies", "cookies.txt",
            "--print", "cookies"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cookies extracted successfully!")
            print(f"📁 Saved to: {os.path.abspath('cookies.txt')}")
            
            # Check the file
            if os.path.exists("cookies.txt"):
                with open("cookies.txt", "r") as f:
                    lines = f.readlines()
                    cookie_count = len([line for line in lines if line.strip() and not line.startswith('#')])
                    print(f"🍪 Found {cookie_count} cookies")
                    
                    if cookie_count > 0:
                        print("\n🎉 You can now use your API!")
                        print("💡 Test with: /transcript/dQw4w9WgXcQ")
                    else:
                        print("⚠️  No cookies found. Make sure you're logged into YouTube!")
            return True
        else:
            print("❌ Failed to extract cookies")
            print(f"Error: {result.stderr}")
            
            # Check for specific Chrome permission error
            if "Permission denied" in result.stderr and browser == "chrome":
                print("\n🔧 Chrome Permission Error Detected!")
                print("This happens when Chrome is running and locks its cookie database.")
                print("\nSolutions:")
                print("1. Close ALL Chrome windows completely")
                print("2. Check Task Manager for remaining Chrome processes")
                print("3. Try again after closing Chrome")
                print("4. Or use Firefox/Edge instead")
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = generate_cookies()
    if not success:
        print("\n💡 Alternative manual method:")
        print("1. Install browser extension: 'Get cookies.txt LOCALLY' for Chrome/Firefox")
        print("2. Go to YouTube and export cookies")
        print("3. Save as 'cookies.txt' in your project root")
        sys.exit(1)
