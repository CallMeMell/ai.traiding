# 🚀 Windows Quickstart - Dev Live Session

**One-page reference for Windows developers**

---

## ⚡ Quick Start (3 Steps)

### 1️⃣ Clone Repository
```powershell
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding
```

### 2️⃣ (Optional) Create .env
```powershell
Copy-Item .env.example .env
notepad .env
```

### 3️⃣ Start Dev Live Session
```powershell
.\scripts\start_live.ps1
```

**Done!** Open browser: http://localhost:8501

---

## 🛠️ ExecutionPolicy Fix

If you get "execution policy" error:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_live.ps1
```

---

## 📋 VS Code Alternative

1. Open project in VS Code
2. Press `Ctrl+Shift+P`
3. Type: "Tasks: Run Task"
4. Select: **"Dev: Live Session"**

✅ Both processes start automatically
✅ Port 8501 auto-forwards

---

## 🔍 What Gets Started

- ✅ **Automation Runner** (DRY_RUN mode - no real trades)
- ✅ **Streamlit View Session** (http://localhost:8501)
- ✅ **Event Generation** (live demo data)

---

## 🎯 Default Settings

| Setting | Value |
|---------|-------|
| DRY_RUN | `true` (safe mode) |
| BROKER_NAME | `binance` |
| BINANCE_BASE_URL | `https://testnet.binance.vision` |
| Port | `8501` |

Override any setting in `.env` file.

---

## ⚠️ Common Issues

### Python Not Found
```powershell
# Install Python 3.8+ from python.org
# Make sure "Add Python to PATH" is checked
python --version
```

### Port 8501 In Use
```powershell
# Stop old processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*"
# Or:
taskkill /F /IM streamlit.exe
```

### python-dotenv Not Found
```powershell
# Install in venv
.\venv\Scripts\python.exe -m pip install python-dotenv
```

---

## 🛑 Stop Session

Press `Ctrl+C` in PowerShell window

Or run VS Code task: **"Stop: All Sessions"**

---

## 📚 More Info

- Full README: [README.md](README.md)
- Implementation Details: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
- Changes Summary: [WINDOWS_FIRST_CHANGES_SUMMARY.md](WINDOWS_FIRST_CHANGES_SUMMARY.md)

---

**Made for Windows ⭐ | PowerShell-First | One-Click Setup**
