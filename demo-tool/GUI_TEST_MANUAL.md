# GUI Verification Test Manual

## Test Environment
- **Application**: TTS Demo Tool (JavaFX Desktop)
- **Date**: May 13, 2026
- **Test Type**: Manual GUI Verification + Automated Unit Tests
- **Purpose**: Verify RCA panel display, call flow rendering, and real-time updates

---

## Automated Unit Tests

Run these tests first (they don't require GUI display):

```powershell
# Run unit tests only (excludes GUI tests)
cd C:\TestRepo\demo-tool
mvn test

# Expected: All existing unit tests + new RCA unit tests should pass
# Look for: MainControllerRcaUnitTest - 5 tests
```

---

## Manual GUI Test Suite

### Prerequisites
1. Stop any running TTS Demo Tool instances
2. Compile the latest code: `mvn compile`
3. Launch the application: `mvn javafx:run`

---

### Test 1: RCA Panel Visibility ⚠️ HIGH PRIORITY

**Issue**: RCA panel not appearing after failures

**Steps**:
1. Select demo: **"VoLTE Call Failure Diagnostics (RCA Demo)"**
2. Click **"Execution"** tab
3. Verify initial state:
   - ✓ Call flow diagram placeholder visible
   - ✓ Terminal output area visible (collapsible)
   - ✓ No RCA panel present

4. Click **"Run Demo"** button
5. Wait for execution (~10-15 seconds)
6. Observe during execution:
   - ✓ Terminal shows JMeter output
   - ✓ Call flow diagram updates with SIP messages
   - ✓ Status shows "Running..."

7. After completion, verify:
   - ✓ Status shows "Completed Successfully" OR "Failed"
   - ✓ Call flow diagram shows messages with arrows
   - ✓ **RCA panel appears** below terminal (right side)
   - ✓ RCA panel shows:
     - Yellow warning background
     - "🔍 Root Cause Analysis" title
     - Failure summary
     - Root cause text
     - Affected node (e.g., "P-CSCF", "S-CSCF")
     - Evidence bullets
     - Numbered recommendations

**Expected Result**: RCA panel MUST be visible and contain diagnostic information

**PASS/FAIL**: __________

**Screenshots**: (Take screenshot if FAIL)

**Logs to Check**:
```
grep "RCA" C:\TestRepo\demo-tool\logs\*.log
# Should show: "Creating RCA panel UI", "Adding RCA panel to UI", "✓ RCA panel successfully added"
```

---

### Test 2: Call Flow Diagram Rendering

**Issue**: Diagrams not rendering or showing 0 messages

**Steps**:
1. Select demo: **"Self-Contained VoLTE Call Setup & Teardown"**
2. Click **"Execution"** tab
3. Click **"Run Demo"**
4. Wait for completion (~30-40 seconds)

5. Verify call flow diagram:
   - ✓ Diagram canvas appears (not blank)
   - ✓ Actor names shown at top (UE, P-CSCF, S-CSCF, etc.)
   - ✓ Vertical lifelines for each actor
   - ✓ Horizontal arrows showing messages
   - ✓ Message labels on arrows (INVITE, 100 TRYING, 180 RINGING, 200 OK, ACK, BYE)
   - ✓ Message flow is left-to-right or right-to-left (not overlapping)

6. Verify status label:
   - ✓ Shows "Call Flow: X messages (Y successful, Z%)"
   - ✓ X should be > 10 (typical VoLTE call has 15-20 messages)
   - ✓ Success rate should be 100% or close

**Expected Result**: Diagram renders with all messages visible and properly positioned

**PASS/FAIL**: __________

**Message Count**: __________ (should be 15-20)

---

### Test 3: Real-Time Updates

**Issue**: Updates not smooth, diagram doesn't update progressively

**Steps**:
1. Select demo: **"Self-Contained VoLTE Call Setup & Teardown"**
2. Click **"Execution"** tab
3. Click **"Run Demo"**
4. **WATCH DURING EXECUTION** (don't wait for completion)

5. Observe real-time behavior:
   - ✓ Terminal scrolls with new output every 1-2 seconds
   - ✓ Call flow status changes: "Not started" → "Initializing..." → "X messages"
   - ✓ Diagram appears and **updates progressively** (messages add one by one)
   - ✓ No UI freezing or lag
   - ✓ Can click "Stop" button during execution

6. After completion:
   - ✓ All messages shown
   - ✓ Diagram is complete (no missing actors or messages)

**Expected Result**: UI updates smoothly during execution, no freezing

**PASS/FAIL**: __________

**Did diagram update progressively?**: YES / NO

---

### Test 4: Multiple Test Runs

**Issue**: Second run breaks RCA panel or diagram

**Steps**:
1. Run **"VoLTE Call Failure Diagnostics"** demo
2. Wait for completion + RCA panel to appear
3. Click **"Configuration"** tab
4. Click **"Execution"** tab again (resets view)
5. Click **"Run Demo"** again
6. Wait for completion

**Verify**:
- ✓ Second run completes successfully
- ✓ RCA panel appears again (not duplicated)
- ✓ Split pane structure is correct (diagram left, terminal+RCA right)
- ✓ No errors in console/logs

**Expected Result**: Multiple runs work without breaking UI structure

**PASS/FAIL**: __________

---

### Test 5: Architecture Panel Updates

**Issue**: Architecture panel doesn't reflect active nodes

**Steps**:
1. Select **"Self-Contained VoLTE Call Setup & Teardown"**
2. Click **"Architecture"** tab
3. Verify initial state: Empty or placeholder message
4. Click **"Configuration"** tab, then **"Execution"** tab
5. Run demo and wait for completion
6. Click **"Architecture"** tab

**Verify**:
- ✓ Architecture diagram shows active network elements
- ✓ Elements highlighted: UE, P-CSCF, S-CSCF, etc.
- ✓ Connections shown between elements
- ✓ Legend/key present

**Expected Result**: Architecture panel populates after demo run

**PASS/FAIL**: __________

---

### Test 6: Failure Highlighting in Diagram

**Issue**: Failed messages not visually highlighted

**Steps**:
1. Run **"VoLTE Call Failure Diagnostics"** (RCA demo)
2. Wait for completion
3. Examine call flow diagram closely

**Verify**:
- ✓ At least one message has RED highlighting
- ✓ Failed message has thicker arrow
- ✓ Warning icon (⚠️) near failed message
- ✓ Failed message matches RCA "Failure Point"

**Expected Result**: Failed messages stand out visually in diagram

**PASS/FAIL**: __________

---

## Test Results Summary

| Test | Pass | Fail | Notes |
|------|------|------|-------|
| 1. RCA Panel Visibility | ☐ | ☐ | |
| 2. Call Flow Rendering | ☐ | ☐ | |
| 3. Real-Time Updates | ☐ | ☐ | |
| 4. Multiple Runs | ☐ | ☐ | |
| 5. Architecture Panel | ☐ | ☐ | |
| 6. Failure Highlighting | ☐ | ☐ | |

**Overall Result**: __________ (X/6 passed)

---

## Troubleshooting

### If RCA panel doesn't appear:
1. Check logs: `C:\TestRepo\demo-tool\logs\*.log`
2. Look for: "RCA panel successfully added" or error messages
3. Verify demo actually failed (check exit code in terminal)
4. Try increasing wait time (test might be passing instead of failing)

### If diagram shows 0 messages:
1. Check JTL file: `C:\TestRepo\demo-tool\logs\*.jtl`
2. Verify file contains CSV data with SIP message labels
3. Check logs for: "JTL file detected", "Parsed X messages"
4. Increase JTL wait timeout if file isn't created in time

### If UI is slow/laggy:
1. Close other applications
2. Check CPU usage during test run
3. Verify throttling settings (200ms diagram, 500ms architecture)
4. Check for infinite loops in logs

---

## Regression Testing Checklist

After any code changes, re-run:
- ✓ All automated unit tests: `mvn test`
- ✓ Manual Test 1 (RCA Panel) - critical
- ✓ Manual Test 2 (Call Flow) - critical
- ✓ Manual Test 3 (Real-Time) - important
- ✓ Manual Test 4 (Multiple Runs) - important

---

## Notes

Test results should be recorded and any failures should be reported with:
1. Screenshots of the issue
2. Log file excerpts
3. Steps to reproduce
4. Expected vs. actual behavior

**Tester**: __________________
**Date**: __________________
**Version**: 1.0.0-SNAPSHOT
