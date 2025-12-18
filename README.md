# System Optimizer - Windows Performance Tool

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A powerful Windows system optimization tool for performance enhancement

[English](README.md) | [简体中文](README_zh.md)

</div>

## ✨ Key Features

### 🕒 Scheduled Tasks
- **Scheduled Shutdown/Sleep**: Set countdown timers for automatic system shutdown or sleep
- **Smart Grace Period**: Provides buffer time before execution - move mouse to cancel
- **Safe Control**: Close the app to cancel all tasks anytime

### 🛡️ System Lock
- **Complete Lock**: Kernel-level keyboard and mouse blocking, including Win key, Alt+Tab, etc.
- **Physical Restriction**: Confines mouse to a small area to prevent accidental operations
- **Password Protection**: Can only be unlocked with the correct password
- **Prevent Sleep**: Keeps screen active during lock

## 📥 Quick Start

### Using exe Version (Recommended)

1. Download [latest release](https://github.com/xqy272/OfficeGuard/releases)
2. Right-click and "Run as administrator"
3. Follow the first-run guide

### Run from Source

```powershell
# Clone repository
git clone https://github.com/xqy272/OfficeGuard.git
cd OfficeGuard

# Run directly (requires admin privileges)
python office_tool_final.py
```

## 🔨 Build from Source

### Automatic Build (Recommended)

```powershell
# Double-click or run in command line
.\build.bat
```

The build script will automatically:
- ✅ Check and install PyInstaller
- ✅ Clean old files
- ✅ Package as standalone exe
- ✅ Create release package

### Manual Build

```powershell
# Install dependencies
pip install pyinstaller

# Build single-file exe
pyinstaller --onefile --windowed --name="OfficeGuard" --uac-admin --version-file=version.txt office_tool_final.py
```

Output location: `dist\OfficeGuard.exe`

## 📖 Usage Guide

### Scheduled Tasks

1. Switch to "Timer Tasks" tab
2. Set countdown time (minutes)
3. Set grace period (seconds)
4. Click "Start Shutdown" or "Start Sleep"
5. Move mouse before countdown ends to cancel

### System Lock

1. Switch to "Stealth Guard" tab
2. Set unlock password (numbers only)
3. Click "Lock System Now"
4. Type password blindly to unlock

## 📂 Data Storage

All data is stored in user directory, not in program folder:

```
C:\Users\{User}\AppData\Local\OfficeGuard\
├── logs\               # Log files
│   ├── guard.log      # Current log (max 5MB)
│   ├── guard.log.1    # Backup 1
│   ├── guard.log.2    # Backup 2
│   └── guard.log.3    # Backup 3
└── config\
    └── guard_config.json  # Configuration file
```

## ⚙️ System Requirements

- **OS**: Windows 10/11
- **Privileges**: Administrator (required)
- **Runtime**: .NET Framework 4.0+
- **Python**: 3.7+ (only for running from source)

## 🔧 Configuration

Configuration file `guard_config.json` contains:

```json
{
    "password": "000",           // Unlock password
    "timer_minutes": 60,         // Default countdown (minutes)
    "grace_seconds": 30,         // Grace period (seconds)
    "mouse_threshold": 15,       // Mouse movement threshold (pixels)
    "win_w": 520,               // Window width
    "win_h": 480,               // Window height
    "win_x": -1,                // Window X position
    "win_y": -1,                // Window Y position
    "first_run": false          // First run flag
}
```

## ⚠️ Safety Tips

1. **Scheduled Tasks**: Close app to safely cancel all tasks
2. **System Lock**: Can only unlock with password - remember it!
3. **Admin Rights**: Required for proper functionality
4. **Data Backup**: All settings saved in AppData directory

## 🐛 Troubleshooting

### exe Won't Start

```powershell
# Check log file
notepad %LOCALAPPDATA%\OfficeGuard\logs\guard.log
```

### Feature Issues

```powershell
# Reset configuration
rmdir /s /q "%LOCALAPPDATA%\OfficeGuard\config"
```

### Permission Denied

Right-click exe file and select "Run as administrator"

## 🗑️ Uninstall

1. Delete exe file
2. (Optional) Clean data directory:
   ```powershell
   rmdir /s /q "%LOCALAPPDATA%\OfficeGuard"
   ```

## 📝 Changelog

### v1.0.0 (2025-12-10)

**New Features**
- ✅ First-run guide interface
- ✅ Complete logging system
- ✅ Auto-save data to AppData
- ✅ Support for standalone exe

**Improvements**
- ✅ Optimized exe packaging
- ✅ Improved shutdown task safety
- ✅ Enhanced mouse confinement logic
- ✅ Better keyboard input recognition

**Bug Fixes**
- ✅ Fixed multiple exception handling issues
- ✅ Fixed config file save problems
- ✅ Fixed window position memory issues

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

## 💖 Acknowledgments

Thanks to all contributors and users for their support!

## 📧 Contact

- **GitHub**: [xqy272](https://github.com/xqy272)
- **Issues**: [Submit Issue](https://github.com/xqy272/OfficeGuard/issues)

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

</div>
