#!/usr/bin/env python3
"""
install.py - Installation script for NanoERP
"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def print_header():
    """Print installation header"""
    print("\n" + "="*60)
    print("        NANOERP - SINGLE USER ERP INSTALLATION")
    print("="*60)

def check_requirements():
    """Check system requirements"""
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]} or higher required.")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✓ Python {current_version[0]}.{current_version[1]} detected")
    
    # Check Tkinter
    try:
        import tkinter
        print("✓ Tkinter available")
    except ImportError:
        print("❌ Tkinter not available")
        print("   Install Tkinter:")
        if platform.system() == "Linux":
            print("   Ubuntu/Debian: sudo apt-get install python3-tk")
            print("   Fedora: sudo dnf install python3-tkinter")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except:
        print("❌ pip not available. Cannot install dependencies.")
        return False
    
    # Install requirements
    requirements = ["fpdf2", "openpyxl", "pillow"]
    
    for package in requirements:
        try:
            print(f"   Installing {package}...", end="", flush=True)
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"], 
                          check=True, capture_output=True)
            print(" ✓")
        except subprocess.CalledProcessError:
            print(" ✗")
            print(f"   Warning: Failed to install {package}")
            print("   Some features may be limited.")
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut"""
    print("\n🖥️  Creating shortcuts...")
    
    system = platform.system()
    
    if system == "Windows":
        create_windows_shortcut()
    elif system == "Darwin":  # macOS
        create_macos_shortcut()
    elif system == "Linux":
        create_linux_shortcut()
    
    return True

def create_windows_shortcut():
    """Create Windows shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "NanoERP.lnk")
        
        target = os.path.abspath("run.py")
        working_dir = os.path.dirname(target)
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = os.path.abspath("assets/icon.ico") if os.path.exists("assets/icon.ico") else ""
        shortcut.save()
        
        print("✓ Desktop shortcut created")
        return True
    except Exception as e:
        print(f"⚠ Could not create shortcut: {e}")
        return False

def create_macos_shortcut():
    """Create macOS application"""
    try:
        app_dir = Path.home() / "Applications" / "NanoERP.app"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create app structure
        contents_dir = app_dir / "Contents" / "MacOS"
        contents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create launcher script
        launcher = contents_dir / "nanoerp"
        with open(launcher, "w") as f:
            f.write("""#!/bin/bash
cd "`dirname \"$0\"`/../../../"
python3 run.py
""")
        
        os.chmod(launcher, 0o755)
        
        # Create Info.plist
        plist = app_dir / "Contents" / "Info.plist"
        with open(plist, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>nanoerp</string>
    <key>CFBundleIdentifier</key>
    <string>com.nanoerp.app</string>
    <key>CFBundleName</key>
    <string>NanoERP</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>""")
        
        print("✓ Application bundle created in ~/Applications/NanoERP.app")
        return True
    except Exception as e:
        print(f"⚠ Could not create application bundle: {e}")
        return False

def create_linux_shortcut():
    """Create Linux desktop entry"""
    try:
        desktop_entry = Path.home() / ".local" / "share" / "applications" / "nanoerp.desktop"
        desktop_entry.parent.mkdir(parents=True, exist_ok=True)
        
        with open(desktop_entry, "w") as f:
            f.write("""[Desktop Entry]
Type=Application
Name=NanoERP
Comment=Single User Desktop ERP
Exec={}/run.py
Path={}
Terminal=false
Categories=Office;Finance;
""".format(os.path.abspath("."), os.path.abspath(".")))
        
        os.chmod(desktop_entry, 0o755)
        print("✓ Desktop entry created")
        return True
    except Exception as e:
        print(f"⚠ Could not create desktop entry: {e}")
        return False

def setup_directories():
    """Create required directories"""
    print("\n📁 Setting up directories...")
    
    directories = ["data", "backups", "config", "assets"]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"   Created {directory}/")
        else:
            print(f"   {directory}/ already exists")
    
    return True

def copy_sample_data():
    """Copy sample data if needed"""
    print("\n📊 Setting up sample data...")
    
    sample_data = {
        "company_name": "My Business",
        "tax_rate": "18",
        "currency": "₹",
        "next_invoice_number": "1001"
    }
    
    try:
        import sqlite3
        db_path = Path("data") / "nano_erp.db"
        
        if not db_path.exists():
            print("   Creating sample database...")
            
            # This will be created by the application
            print("   Database will be created on first run")
        else:
            print("   Database already exists")
    
    except Exception as e:
        print(f"⚠ Could not setup sample data: {e}")
    
    return True

def main():
    """Main installation function"""
    print_header()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Installation failed: Requirements not met")
        return 1
    
    # Ask for installation type
    print("\n" + "-"*60)
    print("Installation Options:")
    print("1. Minimal (Application only)")
    print("2. Standard (Application + Desktop shortcut)")
    print("3. Full (All features + Sample data)")
    print("-"*60)
    
    try:
        choice = input("\nSelect option (1-3, default=2): ").strip() or "2"
        choice = int(choice)
    except ValueError:
        choice = 2
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create shortcuts
    if choice in [2, 3]:
        create_desktop_shortcut()
    
    # Copy sample data
    if choice == 3:
        copy_sample_data()
    
    # Final message
    print("\n" + "="*60)
    print("✅ INSTALLATION COMPLETE!")
    print("="*60)
    print("\nTo run NanoERP:")
    print("  Option 1: Double-click run.py or run.bat/run.sh")
    print("  Option 2: Open terminal and type: python run.py")
    print("\nFirst-time setup:")
    print("  1. Launch the application")
    print("  2. Go to Settings → Company Info")
    print("  3. Add your company details")
    print("  4. Start adding customers and products")
    print("\nNeed help? Check README.md or contact support.")
    print("="*60)
    
    # Launch application?
    if input("\nLaunch NanoERP now? (y/N): ").strip().lower() == 'y':
        print("\n🚀 Launching NanoERP...")
        subprocess.run([sys.executable, "run.py"])
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled.")
        sys.exit(1)