# TTS Demo Tool - TODO List

**Last Updated:** May 6, 2026 (Added TestFX GUI testing task to Priority 2)

---

## 🔴 PRIORITY 1: VoLTE Call Flow Visualization

**Goal:** Replace raw terminal output with visual SIP call flow diagram showing client-server message exchange. Make terminal collapsible/optional. Clearly show the messages that determine test pass/fail.

**Status:** Not Started  
**Target:** Sprint 1 (Phase 1 GUI Enhancement)  
**Estimated Effort:** 2-3 days

---

### Phase 1: Data Model & JTL Parser ✅ Foundation

**Status:** Not Started

- [ ] **Task 1.1:** Create `SipMessage` model class
  - File: `src/main/java/com/tts/demo/model/SipMessage.java`
  - Fields: messageType (String), direction (CLIENT_TO_SERVER/SERVER_TO_CLIENT), threadName, timestamp, elapsed, success (boolean), responseCode
  - Enums: MessageType (INVITE, TRYING, RINGING, OK, ACK, BYE, OTHER), Direction

- [ ] **Task 1.2:** Create `CallFlow` model class
  - File: `src/main/java/com/tts/demo/model/CallFlow.java`
  - Fields: List<SipMessage> messages, int totalMessages, int successfulMessages, boolean callCompleted
  - Methods: analyze() (detect if full flow completed), getClientMessages(), getServerMessages()

- [ ] **Task 1.3:** Create `JtlParser` service
  - File: `src/main/java/com/tts/demo/service/JtlParser.java`
  - Method: `CallFlow parseJtlFile(String filePath)`
  - Parse CSV format: timeStamp, elapsed, label, responseCode, threadName, success
  - Extract SIP message type from label (e.g., "Send INVITE" → INVITE, "Listen for TRYING" → TRYING)
  - Determine direction from threadName (Server 1-1 vs Client 2-1)

- [ ] **Task 1.4:** Create unit tests for JtlParser
  - File: `src/test/java/com/tts/demo/service/JtlParserTest.java`
  - Test data: `logs/phase1_success_baseline.jtl`
  - Verify: 19 messages parsed, correct types detected, direction assigned properly
  - Verify call flow analysis: callCompleted = true, successfulMessages = 19

**Verification:**
```java
CallFlow flow = parser.parseJtlFile("logs/phase1_success_baseline.jtl");
assertEquals(19, flow.getTotalMessages());
assertTrue(flow.isCallCompleted());
// Expected: 2 INVITE, 2 TRYING, 2 RINGING, 4 OK, 2 ACK, 2 BYE
```

---

### Phase 2: Visual Call Flow Component ⚙️ Parallel with Phase 1

**Status:** Not Started

- [ ] **Task 2.1:** Create `CallFlowDiagram` custom JavaFX control
  - File: `src/main/java/com/tts/demo/component/CallFlowDiagram.java`
  - Extends: `Canvas` or custom `Region`
  - Constructor: `CallFlowDiagram(CallFlow callFlow)`
  - Method: `render()` - Draw sequence diagram

- [ ] **Task 2.2:** Implement sequence diagram layout
  - Two vertical lanes: "Client" (left) and "Server" (right)
  - Horizontal arrows for messages with labels
  - Timeline on left edge (elapsed time markers)
  - Message boxes with rounded corners

- [ ] **Task 2.3:** Implement color coding system
  - Green (#27ae60): Successful messages (success=true)
  - Red (#e74c3c): Failed messages (success=false)
  - Blue (#3498db): In-progress/waiting (for real-time updates)
  - Gray (#95a5a6): Informational (timers, delays)

- [ ] **Task 2.4:** Add message labels and details
  - Arrow labels: Message type (INVITE, TRYING, etc.)
  - Hover tooltip: Full details (responseCode, elapsed time, timestamp)
  - Status icons: ✓ (success), ✗ (failure)

- [ ] **Task 2.5:** Add timing indicators
  - Show elapsed time on each message arrow
  - Total call duration at bottom
  - Startup buffer visualization (15-second sync period)

- [ ] **Task 2.6:** Add legend component
  - Color meanings (green=success, red=fail, etc.)
  - Arrow direction (Client→Server, Server→Client)
  - Place at bottom or side of diagram

**Verification:**
- Render test with sample CallFlow → Visual sequence diagram appears
- Check color coding: All green for successful test
- Verify arrow directions: Client→Server (INVITE, ACK, BYE), Server→Client (TRYING, RINGING, OK)

---

### Phase 3: Enhanced Terminal Output 📟 Depends on Phase 1

**Status:** Not Started

- [ ] **Task 3.1:** Enhance `DemoRunner.streamOutput()` to detect SIP messages
  - File: `src/main/java/com/tts/demo/service/DemoRunner.java` (line ~219)
  - Parse patterns: "Send INVITE", "Listen for TRYING", etc.
  - Extract thread name to determine direction

- [ ] **Task 3.2:** Format SIP messages with clear indicators
  - Format: `[Client → Server] INVITE (elapsed: 97ms)` or `[Server → Client] TRYING (elapsed: 38ms)`
  - Use regex to extract message type and timing
  - Color code in terminal (if terminal supports ANSI): Green for success

- [ ] **Task 3.3:** Filter terminal output to reduce noise
  - Keep: [PROGRESS], [INFO], SIP message lines
  - Remove: Raw JMeter logs, DEBUG level, thread dumps
  - Summary line: Keep but format nicely

- [ ] **Task 3.4:** Add call flow summary at end
  - After test completes, output summary:
    ```
    ════════════════════════════════════════════
    Call Flow Summary
    ════════════════════════════════════════════
    Total Messages: 19
    Successful: 19 (100%)
    Failed: 0 (0%)
    Call Completed: ✓ YES
    Duration: 29.1 seconds
    ════════════════════════════════════════════
    Client → Server: INVITE, ACK, BYE
    Server → Client: TRYING, RINGING, OK (×2)
    ════════════════════════════════════════════
    ```

**Verification:**
- Run sip-001 demo → Terminal shows only filtered SIP messages and progress markers
- No raw JMeter noise visible
- Summary appears at end with correct counts

---

### Phase 4: UI Layout Changes 🎨 Depends on Phase 2

**Status:** Not Started

- [ ] **Task 4.1:** Update `main.fxml` layout structure
  - File: `src/main/resources/fxml/main.fxml` (lines 125-135: Live Output section)
  - Replace single TextArea with SplitPane (orientation: VERTICAL)
  - Top pane: CallFlowDiagram component (70% height)
  - Bottom pane: TitledPane with TextArea (30% height, collapsible)

- [ ] **Task 4.2:** Make terminal collapsible by default
  - Use TitledPane or Accordion with title "Terminal Output (Advanced)"
  - Set `expanded="false"` by default (collapsed on startup)
  - Add icon to indicate expandable state

- [ ] **Task 4.3:** Add diagram controls
  - Add toolbar above diagram: [Show Terminal] toggle, [Export PNG] button, [Zoom +/-] buttons
  - Add ScrollPane around diagram for large call flows
  - Add status label: "Call Flow: X messages (Y successful, Z failed)"

- [ ] **Task 4.4:** Update FXML structure
  ```xml
  <!-- Replace existing TextArea section with: -->
  <VBox spacing="10">
      <Label text="Call Flow Visualization:" styleClass="subtitle-label"/>
      
      <!-- Diagram Controls -->
      <HBox spacing="10" alignment="CENTER_LEFT">
          <CheckBox fx:id="showTerminalCheckBox" 
                    text="Show Terminal" 
                    onAction="#handleToggleTerminal"/>
          <Button text="Export Diagram" 
                  onAction="#handleExportDiagram"
                  styleClass="button-secondary"/>
          <Region HBox.hgrow="ALWAYS"/>
          <Label fx:id="callFlowStatusLabel" text="Call Flow: Not started"/>
      </HBox>
      
      <!-- Main Visualization Area -->
      <SplitPane fx:id="visualizationSplitPane" 
                 orientation="VERTICAL" 
                 dividerPositions="0.7"
                 VBox.vgrow="ALWAYS">
          
          <!-- Call Flow Diagram (Top) -->
          <ScrollPane fitToWidth="true" fitToHeight="true">
              <StackPane fx:id="diagramContainer" 
                         style="-fx-background-color: white; -fx-border-color: #bdc3c7; -fx-border-width: 1;">
                  <!-- CallFlowDiagram component injected here -->
              </StackPane>
          </ScrollPane>
          
          <!-- Terminal Output (Bottom, Collapsible) -->
          <TitledPane fx:id="terminalPane" 
                      text="Terminal Output (Advanced)" 
                      expanded="false"
                      collapsible="true">
              <TextArea fx:id="outputTextArea" 
                       editable="false" 
                       wrapText="false"
                       styleClass="text-area"/>
          </TitledPane>
          
      </SplitPane>
  </VBox>
  ```

**Verification:**
- Launch GUI → Diagram area visible, terminal collapsed by default
- Expand terminal → TextArea appears with raw output
- Toggle "Show Terminal" checkbox → Terminal pane visibility toggles

---

### Phase 5: Controller Integration 🔌 Depends on Phases 1-4

**Status:** Not Started

- [ ] **Task 5.1:** Add CallFlowDiagram component to MainController
  - File: `src/main/java/com/tts/demo/controller/MainController.java`
  - Add field: `private CallFlowDiagram callFlowDiagram;`
  - Add FXML reference: `@FXML private StackPane diagramContainer;`
  - Initialize in `initialize()` method

- [ ] **Task 5.2:** Parse JTL after demo completion
  - In `handleRunDemo()` after `RunResult result = demoRunner.runDemo(...)` (line ~287)
  - Call: `CallFlow flow = jtlParser.parseJtlFile(result.getLogFilePath());`
  - Create CallFlowDiagram: `callFlowDiagram = new CallFlowDiagram(flow);`
  - Add to container: `diagramContainer.getChildren().setAll(callFlowDiagram);`

- [ ] **Task 5.3:** Update status label with call flow summary
  - After parsing JTL: `callFlowStatusLabel.setText("Call Flow: " + flow.getTotalMessages() + " messages (" + flow.getSuccessfulMessages() + " successful)");`
  - Change color based on success rate: Green if 100%, yellow if 90-99%, red if <90%

- [ ] **Task 5.4:** Enhanced `appendOutput()` to format SIP messages
  - Modify method at line ~326
  - Detect SIP message patterns in incoming lines
  - Format with direction indicators before appending to TextArea
  - Filter out noise (only show [PROGRESS], [INFO], SIP messages)

- [ ] **Task 5.5:** Add event handlers for controls
  ```java
  @FXML
  private void handleToggleTerminal() {
      boolean show = showTerminalCheckBox.isSelected();
      terminalPane.setExpanded(show);
      if (!show) {
          visualizationSplitPane.setDividerPositions(1.0); // Full diagram
      } else {
          visualizationSplitPane.setDividerPositions(0.7); // 70/30 split
      }
  }
  
  @FXML
  private void handleExportDiagram() {
      if (callFlowDiagram != null) {
          // Export diagram as PNG screenshot
          // Use WritableImage and ImageIO
      }
  }
  ```

- [ ] **Task 5.6:** Optional: Real-time diagram updates
  - Create intermediate CallFlow during execution
  - Update diagram as new SIP messages are detected in streamOutput()
  - Add messages incrementally to show progress (animation effect)

**Verification:**
- Run sip-001 demo → Diagram appears after completion with all messages
- Status label shows "19 messages (19 successful)"
- Terminal shows filtered output with SIP message indicators
- Export PNG button creates valid image file

---

### Phase 6: Polish & Error Handling 🎨 Final

**Status:** Not Started

- [ ] **Task 6.1:** Handle empty/failed tests gracefully
  - If JTL has 0 rows: Show "No messages exchanged" in diagram area
  - If test fails: Highlight failed messages in red, show error details
  - If JTL file not found: Show "Test results unavailable" message

- [ ] **Task 6.2:** Add PNG export functionality
  - Use `WritableImage` to capture diagram snapshot
  - Save to `exports/` folder with timestamp: `sip-001_callflow_20260506_125917.png`
  - Show success notification: "Diagram exported to exports/..."

- [ ] **Task 6.3:** Add hover tooltips on diagram
  - On mouse hover over message arrow: Show tooltip with details
    ```
    INVITE
    Response Code: 200
    Elapsed: 97ms
    Timestamp: 2026-05-06 12:59:36.025
    Thread: Client 2-1
    Status: ✓ Success
    ```
  - Use JavaFX Tooltip class

- [ ] **Task 6.4:** Add CSS styling for diagram component
  - File: `src/main/resources/css/styles.css`
  - Add styles for diagram elements (arrows, labels, legend)
  - Match existing application theme colors

- [ ] **Task 6.5:** Add legend to diagram
  - Static legend at bottom-right of diagram
  - Show: Color meanings (🟢 Success, 🔴 Failed, 🔵 In Progress)
  - Show: Arrow directions (→ Client to Server, ← Server to Client)
  - Small, unobtrusive, semi-transparent background

- [ ] **Task 6.6:** Handle non-SIP protocols gracefully
  - If demo.protocol != SIP_IMS: Show message "Call flow diagram only available for SIP/IMS demos"
  - Still show terminal output normally
  - Future: Add generic message flow for Diameter/RADIUS

**Verification:**
- Run failed test (port conflict) → Diagram shows messages in red
- Export PNG → Valid image file created
- Hover over message → Tooltip appears with details
- Run diameter-001 demo → Shows "Not available for this protocol" message

---

## 🟢 PRIORITY 2: Repository Organization & Infrastructure

**Status:** Backlog

### Organize Local Test Data for Discoverability

**Goal:** Ensure locally-generated test artifacts are in well-structured folders that Copilot and developers can easily discover and reference.

**Current State:** Test results and logs are scattered and not easily discoverable
- 21 JTL test result files in `logs/` (kept locally, git-ignored)
- 3 application log files in `logs/` (kept locally, git-ignored)  
- Run history JSON files in `runs/` (kept locally, git-ignored)

**Tasks:**4
- [ ] **Verify folder structure is intuitive:**
  - `logs/` should contain ONLY JTL test results and application logs
  - `runs/` should contain ONLY run history JSON files
  - Consider: `logs/jtl/` vs `logs/app/` separation?

- [ ] **Add README.md to logs/ folder:**
  - Explain what JTL files are (JMeter test results)
  - Explain application log rotation policy
  - Document baseline file: `phase1_success_baseline.jtl` (must keep)
  - Link to JTL format documentation

- [ ] **Add README.md to runs/ folder:**
  - Explain run history JSON schema
  - Show example JSON structure
  - Document retention policy (keep last N runs?)
  - Add index file or catalog for easy discovery

- [ ] **Update .gitignore comments:**
  - Add inline comments explaining why logs/ and runs/ are ignored
  - Document exceptions (baseline files, etc.)

- [ ] **Add sample/reference files for Copilot:**
  - Keep 1-2 representative JTL files as examples (not just baseline)
  - Keep 1-2 sample run history JSON files
  - Add `.gitkeep` or README to empty folders

- [ ] **Document in PROJECT_STATUS.md:**
  - Add "Test Artifacts" section
  - Explain folder structure
  - Show commands to inspect recent results

**Verification:**
- Copilot can answer: "Show me recent test results"
- Copilot can answer: "What's the format of JTL files?"
- Copilot can find baseline test data easily
- New developers understand where test outputs go

**Estimated Effort:** 1-2 hours

---

### Add GUI Testing Framework (TestFX)

**Goal:** Enable automated JavaFX GUI testing to validate UI components, interactions, and call flow visualization rendering.

**Current State:** No automated GUI testing capability
- Manual testing required for all UI features
- No way to verify call flow diagram rendering programmatically
- Cannot test user interactions (clicks, input, navigation) automatically

**Tasks:**
- [ ] **Create sample GUI test for call flow visualization:**
  - Test: Select sip-001 demo → Click Run → Verify diagram appears
  - Test: Verify diagram container has CallFlowDiagram child node
  - Test: Verify status label updates with message count
  - Test: Click "Show Terminal" checkbox → Verify terminal expands
  - **Status:** NOT COMPLETE - Planned only, no test code written yet

- [ ] **Add test for error scenarios:**
  - Test: Non-SIP demo shows informative message (no diagram)
  - Test: Failed test shows error message in diagram area

- [ ] **Create test for export functionality:**
  - Test: Run demo → Click "Export Diagram" button → Verify PNG file created
  - Test: Verify exports/ folder exists and contains timestamped file
  - **Context:** "Export Diagram" button is in UI (Phase 5 implementation), located next to "Show Terminal" checkbox in Diagram Controls section. Button is disabled initially, enables after successful SIP test. Saves diagram as PNG to `exports/sip-001_callflow_YYYYMMDD_HHMMSS.png`

- [ ] **Add TestFX dependencies and configure Maven:**
  - Add TestFX Core (org.testfx:testfx-core:4.0.18)
  - Add TestFX JUnit5 (org.testfx:testfx-junit5:4.0.18)
  - Add Monocle for headless testing (org.testfx:openjfx-monocle:jdk-12.0.1+2)
  - Scope: test
  - Configure Maven Surefire plugin for GUI tests
  - Add headless mode configuration
  - Set up proper test execution order
  - Configure TestFX properties

**Benefits:**
- Catch UI regressions early
- Verify diagram rendering without manual testing
- Test user interactions programmatically
- Enable CI/CD pipeline GUI validation

**Estimated Effort:** 3-4 hours

---

### Enhance Call Flow Diagram Tooltips with Message-Specific Information

**Goal:** Improve call flow diagram tooltips to provide message-specific, contextual information that explains what each message indicator (green tick, red cross, etc.) means for that particular message type and flow state.

**Current State:** Call flow diagram shows visual indicators (green tick for success) but lacks explanatory tooltips
- Users see green tick (✓) on messages but may not understand what it represents
- Existing tooltip shows raw technical data (timestamp, elapsed time, response code)
- No contextual explanation of message significance in the call flow
- Generic tooltip doesn't explain message-specific meaning

**Problem:** 
- Green tick meaning is ambiguous: Does it mean "message sent successfully"? "Response received"? "Protocol handshake complete"?
- Different messages have different success criteria (e.g., INVITE vs ACK vs BYE)
- Users need business-level interpretation, not just technical status

**Tasks:**
- [ ] **Enhance tooltip content to be message-specific:**
  - File: `src/main/java/com/tts/demo/component/CallFlowDiagram.java` (handleMouseMoved method)
  - Add contextual explanation based on message type and status
  - Example for INVITE with green tick: "✓ Call Initiation Successful - Client sent INVITE and received confirmation"
  - Example for OK with green tick: "✓ Call Accepted - Server confirmed connection establishment"
  - Example for BYE with green tick: "✓ Call Teardown Successful - Connection terminated gracefully"

- [ ] **Define message-specific tooltip templates:**
  - Create method: `String getMessageTooltipText(SipMessage message)`
  - Templates for each MessageType (INVITE, TRYING, RINGING, OK, ACK, BYE):
    ```java
    // Success scenarios
    INVITE + success: "✓ Call Setup Request Sent Successfully\nClient initiated VoLTE call establishment"
    TRYING + success: "✓ Server Processing Request\nCall setup in progress, waiting for final response"
    RINGING + success: "✓ Remote Party Alerted\nDestination is ringing, waiting for answer"
    OK + success: "✓ Call Established/Acknowledged\nConnection successfully established"
    ACK + success: "✓ Acknowledgment Sent\nCall flow handshake completed"
    BYE + success: "✓ Hangup Successful\nCall terminated gracefully"
    
    // Failure scenarios
    INVITE + failure: "✗ Call Setup Failed\nClient could not initiate call - check network connectivity"
    OK + failure: "✗ Response Not Received\nExpected confirmation but got error or timeout"
    ```

- [ ] **Add explanation of status indicators:**
  - Include legend in tooltip: "✓ = Message exchanged successfully"
  - For failed messages: "✗ = Message failed or timed out"
  - For in-progress: "⏱ = Waiting for response"

- [ ] **Add timing context:**
  - Show relative timing: "Elapsed: 97ms (normal for network latency)"
  - Flag slow messages: "Elapsed: 5024ms (slower than expected)"
  - Flag fast messages: "Elapsed: 2ms (cached response)"

- [ ] **Add direction explanation:**
  - Client → Server: "Outgoing request from client to server"
  - Server → Client: "Response from server back to client"
  - Explain significance in call flow context

- [ ] **Add call flow position context:**
  - "Message 3 of 14 in call flow"
  - "Part of call setup phase" / "Part of call teardown phase"
  - "Required for successful call completion"

- [ ] **Handle edge cases:**
  - Missing data: Show "Status information unavailable"
  - Unexpected message: "Unexpected message type - may indicate protocol error"
  - Out-of-order messages: "Warning: Message received out of expected sequence"

- [ ] **Format tooltip for readability:**
  - Use line breaks for multi-line tooltips
  - Bold message type heading
  - Separate sections: Status | Timing | Technical Details
  - Example format:
    ```
    ═══════════════════════════════
    ✓ INVITE - Call Setup Request
    ═══════════════════════════════
    
    Status: Successful
    Meaning: Client initiated VoLTE call
    Direction: Client → Server
    
    Timing: 97ms (normal)
    Position: Message 1 of 14
    Phase: Call Establishment
    
    Technical Details:
    Response Code: 200 OK
    Thread: Client 2-1
    Timestamp: 2026-05-06 15:29:36.025
    ```

**Benefits:**
- Users understand what green tick (and other indicators) mean in context
- Business-level explanation improves usability
- Reduces need for protocol knowledge
- Better troubleshooting with contextual information
- Meets REQ-006 (business-level KPI language)

**Estimated Effort:** 2-3 hours

---

### Convert Call Flow Diagram to UML Sequence Diagram with Vertical Lifelines

**Goal:** Refactor call flow diagram to use standard UML sequence diagram format with vertical lifelines, reducing horizontal width requirements and improving scalability for long call flows.

**Current State:** Call flow diagram uses wide horizontal lanes for client and server
- Client and Server lanes span full height with wide separation
- Requires significant horizontal space (LANE_SPACING = 300px)
- Does not scale well for many messages or small screen sizes
- Non-standard visualization compared to industry sequence diagrams

**Problem:**
- Horizontal layout consumes too much width (600px minimum)
- Difficult to fit in horizontal split pane with terminal
- Not familiar to users who know UML sequence diagrams
- Scaling issues: More messages = wider diagram horizontally

**Proposed Solution: UML-style sequence diagram with vertical lifelines**

**Tasks:**
- [ ] **Refactor diagram layout constants:**
  - File: `src/main/java/com/tts/demo/component/CallFlowDiagram.java`
  - Current: LANE_WIDTH = 150, LANE_SPACING = 300
  - New: LIFELINE_X_CLIENT = 100 (fixed X position), LIFELINE_X_SERVER = 300 (fixed X position)
  - LIFELINE_SPACING = 200 (distance between lifelines)
  - MESSAGE_VERTICAL_SPACING = 50 (vertical space between messages)

- [ ] **Redesign drawLanes() to drawLifelines():**
  - Draw participant labels at top (fixed Y position):
    - "Client" at (LIFELINE_X_CLIENT, HEADER_Y)
    - "Server" at (LIFELINE_X_SERVER, HEADER_Y)
  - Draw vertical dashed lines (lifelines) extending downward:
    - From (LIFELINE_X_CLIENT, HEADER_Y + 30) to (LIFELINE_X_CLIENT, canvasHeight - MARGIN)
    - From (LIFELINE_X_SERVER, HEADER_Y + 30) to (LIFELINE_X_SERVER, canvasHeight - MARGIN)
  - Style: Dashed line (strokeDashArray: 5, 5), gray color

- [ ] **Refactor drawMessages() for horizontal message arrows:**
  - Each message at incremental Y position: `messageY = HEADER_Y + 60 + (messageIndex * MESSAGE_VERTICAL_SPACING)`
  - Outgoing message (Client → Server):
    - Start: (LIFELINE_X_CLIENT, messageY)
    - End: (LIFELINE_X_SERVER, messageY)
    - Arrow direction: rightward (→)
  - Incoming message (Server → Client):
    - Start: (LIFELINE_X_SERVER, messageY)
    - End: (LIFELINE_X_CLIENT, messageY)
    - Arrow direction: leftward (←)

- [ ] **Update canvas sizing logic:**
  - Width calculation: `MARGIN + max(LIFELINE_X_CLIENT, LIFELINE_X_SERVER) + MARGIN` (fixed width ~400px)
  - Height calculation: `HEADER_Y + 60 + (messageCount * MESSAGE_VERTICAL_SPACING) + LEGEND_HEIGHT + MARGIN` (grows vertically)
  - Benefit: Width is now fixed, only height grows with message count

- [ ] **Add activation boxes (optional enhancement):**
  - Small rectangles on lifeline during message processing
  - Visual indicator of "active" processing period
  - Standard UML sequence diagram feature

- [ ] **Update message label positioning:**
  - Place message type label above arrow (centered horizontally)
  - Place timing info below arrow (centered horizontally)
  - Status indicator (✓/✗) at arrow endpoint

- [ ] **Update timing indicators:**
  - Vertical timeline on left edge (Y-axis):
    - Show elapsed time at each message Y position
    - Format: "0ms", "97ms", "142ms", etc.
  - Optional: Add horizontal grid lines at each message Y for readability

- [ ] **Update legend positioning:**
  - Move to bottom (below all messages)
  - Or move to top-right corner (floating)
  - Ensure it doesn't overlap with lifelines

- [ ] **Update hover detection logic:**
  - Current: Detects mouse over message arrow regions
  - Update bounds checking for horizontal arrows between lifelines
  - Adjust tooltip positioning for new layout

**Benefits:**
- **Reduced width:** Fixed width ~400px vs. current ~600px+ (33% reduction)
- **Better scalability:** Only height grows with message count, not width
- **Industry standard:** Familiar UML sequence diagram format
- **Better fit:** Works well in horizontal split pane (60/40 with terminal)
- **Improved readability:** Vertical flow matches time progression (top to bottom)
- **Professional appearance:** Standard notation used in telecom/protocol documentation

**Visual Comparison:**

Current Layout (Wide):
```
┌─────────────────────────────────────────────────┐
│  Client Lane (150px)    Server Lane (150px)    │
│  ┌──────────┐           ┌──────────┐           │
│  │          │  ─────→   │          │  INVITE   │
│  │          │  ←─────   │          │  TRYING   │
│  │          │  ─────→   │          │  ACK      │
│  └──────────┘           └──────────┘           │
│  LANE_SPACING = 300px                          │
└─────────────────────────────────────────────────┘
Total Width: 600px+
```

New Layout (Narrow):
```
┌──────────────────────────────┐
│  Client        Server        │
│    │             │           │
│    │──INVITE────→│  97ms     │
│    │←──TRYING────│  135ms    │
│    │──ACK───────→│  142ms    │
│    │             │           │
│    │             │           │
└──────────────────────────────┘
Total Width: 400px (fixed)
Height: grows with messages
```

**Implementation Notes:**
- Keep color coding system unchanged (green, red, blue)
- Keep tooltip system unchanged (just update bounds)
- Keep real-time update throttling (200ms)
- Maintain backward compatibility with CallFlow model
- Update unit tests if any test diagram dimensions

**Estimated Effort:** 3-4 hours

---

### Add Log Level Selector for Terminal Output

**Goal:** Provide users with dynamic control over terminal log verbosity by adding a log level selector (dropdown/combobox) to filter log messages by level (INFO, WARNING, ERROR, DEBUG, etc.).

**Current State:** Terminal shows all log levels with no filtering capability
- Users see all JMeter output including DEBUG level noise
- No way to focus on specific log levels (e.g., only ERRORs/WARNINGs)
- Cannot dynamically adjust verbosity during or after test execution

**Tasks:**
- [ ] **Add log level selector UI component:**
  - Add ComboBox above terminal output in Execution tab
  - Position: In HBox with "Show Terminal" checkbox and "Export Logs (CSV)" button
  - Options: "ALL", "INFO", "WARNING", "ERROR", "DEBUG"
  - Default: "INFO" (hide DEBUG messages by default)
  - Label: "Log Level:"

- [ ] **Implement log level filtering logic:**
  - Parse log level from each terminal output line (e.g., "[INFO]", "[DEBUG]", "[ERROR]")
  - Filter `outputTextArea` content based on selected level
  - Update filtering in real-time when selector changes
  - Support JMeter log levels: INFO, WARN, ERROR, DEBUG

- [ ] **Add retroactive filtering:**
  - When user changes log level, re-filter all existing terminal content
  - Store original unfiltered output internally
  - Apply filter to display without losing data
  - Show message count: "Showing 45 of 127 log entries"

- [ ] **Persist log level preference:**
  - Save selected log level to user preferences
  - Restore on application restart
  - Per-demo or global setting (consider both options)

- [ ] **Add clear visual indicators:**
  - Color-code log levels in terminal (if feasible):
    - INFO: Default color
    - WARNING: Yellow/Orange
    - ERROR: Red
    - DEBUG: Gray
  - Add icon or badge next to log level selector showing active filter

- [ ] **Update FXML:**
  ```xml
  <!-- Add to terminal controls HBox -->
  <Label text="Log Level:"/>
  <ComboBox fx:id="logLevelComboBox" 
            onAction="#handleLogLevelChange"
            promptText="INFO">
      <items>
          <FXCollections fx:factory="observableArrayList">
              <String fx:value="ALL"/>
              <String fx:value="INFO"/>
              <String fx:value="WARNING"/>
              <String fx:value="ERROR"/>
              <String fx:value="DEBUG"/>
          </FXCollections>
      </items>
  </ComboBox>
  ```

**Benefits:**
- Users can focus on specific log levels (e.g., only errors)
- Reduces terminal clutter during troubleshooting
- Improves debugging workflow
- Maintains full log history while showing filtered view

**Estimated Effort:** 2-3 hours

---

### Add History Tab for Test Execution History

**Goal:** Create a new History tab (alongside Configuration and Execution tabs) to display past test executions with quick access to results, diagrams, and exported logs. Implement configurable retention with storage constraints.

**Current State:** No visual history browser in GUI
- Run history stored as JSON files in `runs/` folder (23 files currently)
- Users must manually browse folder to find past test results
- No easy way to view previous call flow diagrams
- No convenient access to exported terminal logs
- History count grows unbounded (potential storage issue)

**Problem:**
- Users cannot easily review past test results in GUI
- No visual timeline of test executions
- Cannot quickly compare current vs. past results
- No retention policy leads to storage bloat

**Proposed Solution: History Tab with configurable retention**

**Tasks:**
- [ ] **Add History tab to TabPane:**
  - File: `src/main/resources/fxml/main.fxml`
  - Insert as 3rd tab after Configuration and Execution tabs
  - Tab properties: `text="History"`, `fx:id="historyTab"`, always enabled
  - Layout: TableView with columns for history entries

- [ ] **Design History TableView columns:**
  - **Timestamp:** Execution date/time (sortable, default sort descending)
  - **Demo Name:** Demo title (e.g., "VoLTE Call Setup & Teardown")
  - **Category:** Protocol/complexity (e.g., "SIP/IMS - Basic")
  - **Status:** Success/Failed with icon (✓/✗) and color coding
  - **Duration:** Test execution time (e.g., "29.1s")
  - **Actions:** Buttons for "View Diagram" and "Export CSV"

- [ ] **Implement TableView data model:**
  - File: `src/main/java/com/tts/demo/controller/MainController.java`
  - Add field: `@FXML private TableView<RunResult> historyTableView;`
  - Create ObservableList<RunResult> from ConfigManager.getRunHistory()
  - Bind to TableView with proper cell factories
  - Auto-refresh when new test completes

- [ ] **Add "View Diagram" action button:**
  - Column with Button in each row
  - Click handler: Load JTL file, parse CallFlow, display diagram in popup or Execution tab
  - For SIP/IMS demos only (disable for other protocols)
  - Show message if JTL file not found: "Test results unavailable"
  - Popup dialog with diagram or navigate to Execution tab with loaded diagram

- [ ] **Add "Export CSV" action button:**
  - Column with Button in each row
  - Click handler: Export terminal logs to CSV file
  - CSV format: `Timestamp,LogLevel,Message`
  - Save to `exports/` folder: `{demoId}_logs_{timestamp}.csv`
  - Show success notification: "Logs exported to exports/..."
  - Handle case where terminal output not available

- [ ] **Implement configurable retention policy:**
  - File: `src/main/java/com/tts/demo/service/ConfigManager.java`
  - Add config property: `history.retention.count` (default: 5, max: 20)
  - Method: `setHistoryRetentionCount(int count)` with validation (1-20 range)
  - Auto-cleanup: When saving new run result, delete oldest if count exceeds limit
  - Sort by timestamp, keep newest N results, delete rest

- [ ] **Add retention settings UI:**
  - Location: Settings menu or preferences dialog (future task)
  - Or: Add spinner control at bottom of History tab
  - Label: "Keep last N executions:" with Spinner (range 1-20, default 5)
  - Save preference immediately on change
  - Show warning if reducing count: "This will delete X older test results"

- [ ] **Update ConfigManager.saveRunResult():**
  - After saving new RunResult JSON:
    ```java
    // Auto-cleanup based on retention policy
    int retentionCount = getHistoryRetentionCount();
    List<RunResult> allResults = getRunHistory();
    if (allResults.size() > retentionCount) {
        // Sort by timestamp descending
        allResults.sort(Comparator.comparing(RunResult::getTimestamp).reversed());
        // Delete files beyond retention count
        for (int i = retentionCount; i < allResults.size(); i++) {
            deleteRunResult(allResults.get(i).getRunId());
        }
    }
    ```

- [ ] **Add storage monitoring:**
  - Calculate total storage used by `runs/` folder
  - Display at bottom of History tab: "Storage used: 245 KB (22 files)"
  - Add warning if approaching limit: "Consider reducing retention count"
  - Limit calculation: Assume ~10-15 KB per run result

- [ ] **Implement "Clear All History" button:**
  - Location: Bottom of History tab
  - Confirmation dialog: "Are you sure you want to delete all test history?"
  - Clear all JSON files from `runs/` folder
  - Refresh TableView to show empty state

- [ ] **Add empty state message:**
  - When no history exists: Show centered message
  - Text: "No test executions found. Run a demo to see history here."
  - Icon: Info icon or empty inbox icon

- [ ] **Update FXML for History tab:**
  ```xml
  <Tab text="History" fx:id="historyTab" closable="false">
      <VBox spacing="10" style="-fx-padding: 15;">
          
          <!-- History Table -->
          <TableView fx:id="historyTableView" VBox.vgrow="ALWAYS">
              <columns>
                  <TableColumn text="Timestamp" prefWidth="150"/>
                  <TableColumn text="Demo Name" prefWidth="250"/>
                  <TableColumn text="Category" prefWidth="120"/>
                  <TableColumn text="Status" prefWidth="100"/>
                  <TableColumn text="Duration" prefWidth="80"/>
                  <TableColumn text="Diagram" prefWidth="100"/>
                  <TableColumn text="Export CSV" prefWidth="100"/>
              </columns>
              <placeholder>
                  <Label text="No test executions found. Run a demo to see history here."
                         style="-fx-text-fill: #95a5a6;"/>
              </placeholder>
          </TableView>
          
          <!-- Controls at bottom -->
          <HBox spacing="15" alignment="CENTER_LEFT">
              <Label text="Keep last:"/>
              <Spinner fx:id="retentionCountSpinner" 
                       min="1" max="20" initialValue="5" 
                       prefWidth="80"
                       onValueChange="#handleRetentionChange"/>
              <Label text="executions"/>
              <Region HBox.hgrow="ALWAYS"/>
              <Label fx:id="storageInfoLabel" text="Storage: 0 KB (0 files)"/>
              <Button text="Clear All History" 
                      onAction="#handleClearHistory"
                      styleClass="button-danger"/>
          </HBox>
          
      </VBox>
  </Tab>
  ```

- [ ] **Style status column with color coding:**
  - Success: Green text with ✓ icon
  - Failed: Red text with ✗ icon
  - Use custom TableCell factory for styling

- [ ] **Add sorting and filtering (optional enhancement):**
  - Default sort: Timestamp descending (newest first)
  - Allow sorting by any column (click header)
  - Add search field to filter by demo name
  - Add protocol filter dropdown (SIP/IMS, Diameter, RADIUS, All)

**Benefits:**
- **Easy access:** View past test results without leaving GUI
- **Quick comparison:** See success/failure patterns over time
- **Convenient replay:** Reopen diagrams from past executions
- **Storage control:** Configurable retention prevents unbounded growth
- **Audit trail:** Visual timeline of all test executions
- **Export capability:** Access to logs for analysis/debugging

**Storage Constraints:**
- Default retention: 5 executions (~50-75 KB)
- Maximum retention: 20 executions (~200-300 KB)
- Per-run storage: ~10-15 KB (JSON + JTL reference)
- Total maximum: <500 KB (negligible storage impact)

**Verification:**
- Run 3 demos → History tab shows 3 entries
- Set retention to 2 → Oldest entry auto-deleted, 2 remain
- Click "View Diagram" → Call flow diagram appears
- Click "Export CSV" → CSV file created in exports/
- Click "Clear All History" → All entries removed

**Estimated Effort:** 4-5 hours

---

## 🟢 PRIORITY 3: Additional Features (Future)

**Status:** Backlog

- [ ] Add authentication/authorization for GUI access
- [ ] Add Diameter protocol call flow visualization
- [ ] Add RADIUS protocol message flow visualization
- [ ] Add test scheduling/automation features
- [ ] Add comparative analysis (compare 2+ test runs side-by-side)
- [ ] Add performance trending charts (duration over time, success rate over time)

---

## 🟡 PRIORITY 4: Phase 2 Architecture (Spring Boot Migration)

**Status:** Planning Phase

- [ ] Design REST API endpoints around existing service layer
- [ ] Create Vanilla JS frontend (reuse business language from JavaFX)
- [ ] Implement WebSocket for real-time progress streaming
- [ ] Maintain CLI for automation/CI integration
- [ ] Database layer for persistent run history (currently JSON files)

---

## 📋 Completed Items

### ✅ Phase 1-5: VoLTE Client-Server Implementation (May 5, 2026)
- ✅ Phase 1: Modified JMX with 15s synchronization buffer
- ✅ Phase 2: CLI integration with license handling (8/8 tests passed)
- ✅ Phase 3: UDP port validation (ports 5060, 5065)
- ✅ Phase 4: Enhanced logging with [PROGRESS] markers
- ✅ Phase 5: Reliability testing (100% success - 5/5 runs)

### ✅ GUI Deployment (May 6, 2026)
- ✅ Launched JavaFX GUI successfully
- ✅ 10 demos loaded from catalog
- ✅ 18 run results loaded from history
- ✅ JMeter installation validated

---

## 📝 Notes

**Current Branch:** `develop`  
**Java Version:** 11.0.30 (Oracle JDK)  
**JavaFX Version:** 17.0.2  
**Maven Version:** 3.9.9

**Testing Strategy:**
- Unit test each component in isolation (JtlParser, CallFlow, SipMessage)
- Integration test with actual JTL files from `logs/` folder
- Manual GUI testing with sip-001 demo
- Verify both success and failure scenarios

**Design Principles:**
- Business language in UI (not technical protocol terms)
- Progressive disclosure (hide complexity by default)
- Visual feedback for all actions
- Graceful degradation for unsupported protocols

---

*Last Updated: May 6, 2026 - Priority 1 task defined*
