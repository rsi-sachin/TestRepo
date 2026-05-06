# TTS Demo Tool - TODO List

**Last Updated:** May 6, 2026

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

## 🟢 PRIORITY 2: Additional Features (Future)

**Status:** Backlog

- [ ] Add authentication/authorization for GUI access
- [ ] Add Diameter protocol call flow visualization
- [ ] Add RADIUS protocol message flow visualization
- [ ] Add test scheduling/automation features
- [ ] Add comparative analysis (compare 2+ test runs side-by-side)
- [ ] Add performance trending charts (duration over time, success rate over time)

---

## 🟡 PRIORITY 3: Phase 2 Architecture (Spring Boot Migration)

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
