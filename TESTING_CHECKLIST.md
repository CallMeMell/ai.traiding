# ✅ Testing Checklist - Windows-First Dev Live Session

**Use this checklist to verify the implementation on Windows**

---

## 📋 Pre-Test Requirements

- [ ] Windows 10/11 system
- [ ] PowerShell installed (default on Windows)
- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] VS Code installed (for VS Code tests)

---

## 🧪 Test Suite

### Test 1: Fresh Clone - PowerShell Script

**Scenario:** New Windows user clones and starts Dev Live Session

**Steps:**
```powershell
# 1. Clone repository
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding

# 2. Run start script
.\scripts\start_live.ps1
```

**Expected Results:**
- [ ] venv created automatically
- [ ] Dependencies installed (pip, requirements.txt, streamlit, etc.)
- [ ] Configuration displayed (DRY_RUN: true, etc.)
- [ ] Automation Runner starts (dry-run mode)
- [ ] Streamlit starts on port 8501
- [ ] Output: "Both processes started!"
- [ ] Output: "http://localhost:8501"

**Browser Check:**
- [ ] Open http://localhost:8501
- [ ] View Session dashboard loads
- [ ] Events are visible (after 5-10 seconds)

**Cleanup:**
- [ ] Press Ctrl+C
- [ ] Processes stop cleanly
- [ ] No hanging processes

---

### Test 2: ExecutionPolicy Error Handling

**Scenario:** User has restricted ExecutionPolicy

**Steps:**
```powershell
# 1. Try to run script
.\scripts\start_live.ps1
# (Expect error if policy is restricted)

# 2. Apply fix
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Run again
.\scripts\start_live.ps1
```

**Expected Results:**
- [ ] First attempt fails with clear error
- [ ] Fix command works
- [ ] Second attempt succeeds
- [ ] Both processes start

---

### Test 3: VS Code Task - Dev: Live Session

**Scenario:** VS Code user runs compound task

**Steps:**
1. Open project in VS Code
2. Press `Ctrl+Shift+P`
3. Type: "Tasks: Run Task"
4. Select: "Dev: Live Session"

**Expected Results:**
- [ ] Task starts without errors
- [ ] Two terminal panels open (Runner + Streamlit)
- [ ] Runner shows DRY_RUN mode
- [ ] Streamlit shows "You can now view" message
- [ ] Port 8501 appears in Ports panel
- [ ] Port label is "View Session"
- [ ] Port auto-forwards (Codespaces/Remote)
- [ ] Port opens automatically in preview

**Terminal Check:**
- [ ] Default terminal is PowerShell (not CMD)

---

### Test 4: VS Code Individual Tasks

**Test 4a: Install Dev Deps**

**Steps:**
- Run task: "Install Dev Deps"

**Expected Results:**
- [ ] venv created if not exists
- [ ] pip upgraded
- [ ] requirements.txt installed (or skipped gracefully)
- [ ] streamlit, plotly, pandas, etc. installed
- [ ] No errors about activation

**Test 4b: Run: Automation Runner (Dry-Run)**

**Steps:**
- Run task: "Run: Automation Runner (Dry-Run)"

**Expected Results:**
- [ ] Runner starts in dry-run mode
- [ ] No API keys needed
- [ ] Events generated
- [ ] No activation errors

**Test 4c: Run: View Session (Streamlit)**

**Steps:**
- Run task: "Run: View Session (Streamlit)"

**Expected Results:**
- [ ] Streamlit starts on port 8501
- [ ] Port visible in VS Code
- [ ] Dashboard accessible

**Test 4d: Stop: All Sessions**

**Steps:**
- Start "Dev: Live Session"
- Run task: "Stop: All Sessions"

**Expected Results:**
- [ ] All Streamlit processes stopped
- [ ] Clean termination
- [ ] No errors

---

### Test 5: .env Override Behavior

**Scenario:** User wants custom configuration

**Steps:**
```powershell
# 1. Create .env file
Copy-Item .env.example .env

# 2. Edit .env
# Set: DRY_RUN=false
# Set: CUSTOM_VAR=test

# 3. Run script
.\scripts\start_live.ps1
```

**Expected Results:**
- [ ] Configuration shows DRY_RUN: false (not true)
- [ ] .env values override defaults
- [ ] Script mentions "Loading environment variables from .env"

---

### Test 6: python-dotenv CLI Verification

**Scenario:** Verify python-dotenv is working

**Steps:**
```powershell
# After running script once (venv exists)
.\venv\Scripts\python.exe -m dotenv list
```

**Expected Results:**
- [ ] Command works (no "No module named dotenv")
- [ ] Shows environment variables from .env
- [ ] No errors

---

### Test 7: Direct Python Calls (No Activation)

**Scenario:** Verify no activation is used

**Steps:**
```powershell
# Check task commands don't use activation
Get-Content .vscode\tasks.json | Select-String -Pattern "Activate|activate"
```

**Expected Results:**
- [ ] No "Activate.ps1" in Windows commands
- [ ] All use ".\venv\Scripts\python.exe" directly

---

### Test 8: Port 8501 Configuration

**Scenario:** VS Code port forwarding works

**Steps:**
1. Open project in VS Code
2. Run task: "Dev: Live Session"
3. Check Ports panel (View → Terminal → Ports)

**Expected Results:**
- [ ] Port 8501 appears automatically
- [ ] Label: "View Session"
- [ ] Status: Running/Forwarded
- [ ] Click opens preview

---

### Test 9: Error Handling - Python Not Found

**Scenario:** User doesn't have Python

**Steps:**
```powershell
# Temporarily rename Python (or test on system without it)
.\scripts\start_live.ps1
```

**Expected Results:**
- [ ] Clear error: "Python is not installed!"
- [ ] Script exits cleanly
- [ ] No confusing errors

---

### Test 10: Error Handling - Port Already in Use

**Scenario:** Port 8501 is occupied

**Steps:**
```powershell
# 1. Start Dev Live Session twice (second will fail)
.\scripts\start_live.ps1
# In another window:
.\scripts\start_live.ps1
```

**Expected Results:**
- [ ] Second instance shows port error
- [ ] Error message mentions port 8501
- [ ] Can stop processes with Ctrl+C

**Cleanup:**
```powershell
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*"
```

---

## 📊 Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Fresh Clone - PowerShell Script | ⬜ | |
| 2. ExecutionPolicy Error Handling | ⬜ | |
| 3. VS Code Task - Dev: Live Session | ⬜ | |
| 4a. VS Code - Install Dev Deps | ⬜ | |
| 4b. VS Code - Automation Runner | ⬜ | |
| 4c. VS Code - View Session | ⬜ | |
| 4d. VS Code - Stop All Sessions | ⬜ | |
| 5. .env Override Behavior | ⬜ | |
| 6. python-dotenv CLI Verification | ⬜ | |
| 7. Direct Python Calls | ⬜ | |
| 8. Port 8501 Configuration | ⬜ | |
| 9. Error - Python Not Found | ⬜ | |
| 10. Error - Port In Use | ⬜ | |

**Legend:** ⬜ Not Tested | ✅ Pass | ❌ Fail

---

## 🎯 Success Criteria

For implementation to be considered successful:
- [ ] All core tests (1-8) pass
- [ ] Error handling tests (9-10) show clear messages
- [ ] No ExecutionPolicy errors with bypass
- [ ] No activation errors
- [ ] .env override works correctly
- [ ] Port 8501 auto-forwards in VS Code
- [ ] Both processes start reliably

---

## 📝 Notes

Use this space for any issues found:

```
[Test results and notes here]
```

---

**Testing Date:** _____________  
**Tester:** _____________  
**Windows Version:** _____________  
**Python Version:** _____________  
**VS Code Version:** _____________
