# Real-Time Architecture Panel Update - Verification Guide

## Verification Steps

### 1. Launch the Application
```powershell
cd C:\TestRepo\demo-tool
mvn javafx:run
```

### 2. Select and Configure Demo
- In the left panel, click on **"sip-003: Validate Complete IMS Call Flow"**
- Switch to the **"Architecture"** tab (keep it visible)
- Return to **"Configuration"** tab
- Click **"Run Demo"** button

### 3. Expected Log Output (During Test Execution)

When the demo runs, you should see these INFO-level log messages in the console:

```
[INFO] [REALTIME] Cleared architecture panel actor tracking
[INFO] [REALTIME] New actors detected: Client (total: 1)
[INFO] [REALTIME] Updating architecture panel immediately
[INFO] [REALTIME] Architecture panel updated with 1 actors: Client
[INFO] [REALTIME] New actors detected: Server (total: 2)
[INFO] [REALTIME] Scheduling architecture update in 123ms
[INFO] [REALTIME] Architecture panel updated with 2 actors: Client, Server
[INFO] [REALTIME] New actors detected: TAS (total: 3)
[INFO] [REALTIME] Updating architecture panel immediately
[INFO] [REALTIME] Architecture panel updated with 3 actors: Client, Server, TAS
```

**Note:** Actual actor names may vary based on the test scenario. For sip-003, you might see:
- `UE (Client)` or `Client`
- `UE (Server)` or `Server`  
- `TAS` (Telephony Application Server)

### 4. Visual Verification (What You Should See on Architecture Tab)

**Timeline of visual changes:**

| Time | Architecture Panel State |
|------|-------------------------|
| **T+0s** (Test Start) | All nodes visible, NONE highlighted |
| **T+1-2s** | First actor appears with **green glow** (usually Client/UE-A) |
| **T+2-4s** | Second actor lights up green (usually Server/TAS) |
| **T+4-6s** | Third actor lights up green (usually TAS/UE-B) |
| **T+End** | All detected actors remain highlighted green |

### 5. Log Analysis

#### What to look for:
1. **"Cleared architecture panel actor tracking"** - Appears when demo starts
2. **"New actors detected: X"** - Appears each time a new actor is found in messages
3. **"Updating architecture panel immediately"** - Triggered if 500ms has passed since last update
4. **"Scheduling architecture update in Xms"** - Triggered if within throttle window
5. **"Architecture panel updated with N actors: ..."** - Actual UI update with actor names

#### Timing verification:
- Updates should occur **at most once every 500ms** (throttling)
- Multiple actors detected within 500ms window will be batched into one update
- Each new actor triggers an update attempt (but throttled)

### 6. Failure Indicators

If real-time updates are NOT working, you would see:
- ❌ No `[REALTIME]` log messages during execution
- ❌ Architecture tab shows no green highlights until test completes
- ❌ Only one update at the very end (not during execution)

### 7. Quick Verification Test

**Without running full demo:**
```java
// The logs should show on demo start:
[INFO] [REALTIME] Cleared architecture panel actor tracking

// This confirms the tracking system is initialized
```

## Technical Details

### Throttling Mechanism
- **Update Interval:** Maximum 1 update per 500ms
- **Purpose:** Prevent UI flickering from rapid message arrival
- **Behavior:** First actor triggers immediate update, subsequent actors within 500ms are batched

### Thread Safety
- `liveActiveActors` uses `Collections.synchronizedSet()`
- Updates run on JavaFX Application Thread via `Platform.runLater()`
- Background thread handles throttle delay scheduling

### Performance
- **Trigger:** Only when NEW actor detected (not every message)
- **Typical scenario:** 3 actors = 3 updates over ~5-10 seconds
- **Without optimization:** Would be 20+ updates for 20 messages

## Troubleshooting

### If no [REALTIME] logs appear:
1. Check that the selected demo is **SIP/IMS protocol** (not Diameter/RADIUS)
2. Verify `selectedDemo.getProtocol() == Demo.Protocol.SIP_IMS` condition is met
3. Check that messages have valid `sourceActor` and `targetActor` fields

### If logs appear but Architecture tab doesn't update:
1. Ensure Architecture tab is open and visible during test
2. Check `architecturePanel` is not null
3. Verify `NetworkArchitecturePanel.setActiveActors()` is being called

### If updates are too slow:
1. Current throttle: 500ms (configurable in `scheduleArchitectureUpdate()`)
2. Can reduce to 200ms if needed (but may cause flickering)

## Expected Output Example

```
13:25:01.123 [JavaFX Application Thread] INFO  - Demo run started: Validate Complete IMS Call Flow
13:25:01.125 [JavaFX Application Thread] INFO  - [REALTIME] Cleared architecture panel actor tracking
13:25:03.456 [pool-3-thread-1] INFO  - [REALTIME] New actors detected: Client (total: 1)
13:25:03.457 [pool-3-thread-1] INFO  - [REALTIME] Updating architecture panel immediately
13:25:03.459 [JavaFX Application Thread] INFO  - [REALTIME] Architecture panel updated with 1 actors: Client
13:25:04.789 [pool-3-thread-1] INFO  - [REALTIME] New actors detected: Server (total: 2)
13:25:04.790 [pool-3-thread-1] INFO  - [REALTIME] Scheduling architecture update in 333ms
13:25:05.123 [Thread-7] INFO  - [REALTIME] Architecture panel updated with 2 actors: Client, Server
13:25:06.234 [pool-3-thread-1] INFO  - [REALTIME] New actors detected: TAS (total: 3)
13:25:06.235 [pool-3-thread-1] INFO  - [REALTIME] Updating architecture panel immediately
13:25:06.237 [JavaFX Application Thread] INFO  - [REALTIME] Architecture panel updated with 3 actors: Client, Server, TAS
13:25:15.678 [JavaFX Application Thread] INFO  - Demo run completed: Validate Complete IMS Call Flow - SUCCESS
```

## Conclusion

If you see the `[REALTIME]` log messages with actor names during test execution (not just at the end), the real-time architecture panel updates are working correctly. The Architecture tab should visually reflect these updates with green highlighting appearing progressively as actors are detected.
