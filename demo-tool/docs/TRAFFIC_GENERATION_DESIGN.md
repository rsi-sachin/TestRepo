# Traffic Generation Engine - Design & Implementation

## Overview
Transforms the TTS Demo Tool into a traffic generation engine with controlled failure injection based on 3GPP conformance scenarios.

**Date:** May 13, 2026  
**Feature Status:** Phase 1 Complete (Models), Phase 2-4 In Progress

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Traffic Generator UI                         │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ Volume     │  │ Failure      │  │  3GPP Conformance       │ │
│  │ Controls   │  │ Injection    │  │  Scenario Selector      │ │
│  │            │  │              │  │                         │ │
│  │ • Calls    │  │ • Rate: 15%  │  │  CONF-SIP-001           │ │
│  │ • Threads  │  │ • Node: HSS  │  │  CONF-AUTH-003          │ │
│  │ • Duration │  │ • Type       │  │  CONF-CALL-002          │ │
│  └────────────┘  └──────────────┘  └─────────────────────────┘ │
│                                                                  │
│  [Start Traffic] [Stop] [Export Data] [View Live Stats]        │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Traffic Profile → JMeter Properties                │
│                                                                  │
│  TrafficProfile.toJMeterProperties():                           │
│    threads=50, loops=2000, rampup=30                            │
│    failure_rate=15.0, failure_node=HSS                          │
│    failure_scenario=CONF-AUTH-003                               │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│            Enhanced DemoRunner (Load Generation)                │
│                                                                  │
│  • Multi-threaded JMeter execution                              │
│  • Dynamic property injection                                   │
│  • Real-time message streaming                                  │
│  • Failure rate enforcement                                     │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TTS/JMeter Execution                          │
│                                                                  │
│  jmeter -n -t test.jmx -l results.jtl                           │
│    -Jthreads=50 -Jloops=2000                                    │
│    -Jfailure_rate=15.0 -Jfailure_node=HSS                       │
│                                                                  │
│  → Injects failures at 15% rate in HSS authentication           │
│  → Generates 100,000 calls (50 threads × 2000 loops)            │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              TrafficStats (Real-time Collection)                │
│                                                                  │
│  Thread-safe counters:                                          │
│    • Total attempts: 100,000                                    │
│    • Successful: 85,000 (85%)                                   │
│    • Failed: 15,000 (15%) ✓ matches target                      │
│                                                                  │
│  Failure breakdown:                                             │
│    • By Type: Authentication Failure: 15,000                    │
│    • By Node: HSS: 15,000                                       │
│    • By Code: 403 Forbidden: 15,000                             │
│                                                                  │
│  Performance metrics:                                           │
│    • Avg response: 245ms                                        │
│    • Throughput: 333 calls/sec                                  │
│    • 95th percentile: 890ms                                     │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Data Export for Analysis Agent                     │
│                                                                  │
│  Formats:                                                       │
│    • CSV: detailed call logs with failure patterns              │
│    • JSON: aggregated statistics by node/type/time              │
│    • JTL: raw JMeter results (can be huge)                      │
│                                                                  │
│  Analysis Agent Input:                                          │
│    → Failure pattern detection                                  │
│    → 3GPP conformance issue identification                      │
│    → Fix recommendations based on protocol spec                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models Created

### 1. **TrafficProfile** (`src/main/java/com/tts/demo/model/TrafficProfile.java`)

**Purpose:** Configures traffic generation parameters and failure injection settings.

**Key Fields:**
```java
// Traffic volume
private int concurrentCalls;        // Number of simultaneous calls (threads)
private int totalCalls;             // Total number of calls to generate
private int rampUpSeconds;          // Time to reach full load
private int durationSeconds;        // Test duration (0 = run to completion)

// Failure injection
private double failureRate;         // 0.0 to 100.0 percent
private ActorType failureNode;      // Which node injects failures
private String failureScenario;     // 3GPP conformance scenario ID
private FailureType failureType;    // Category of failure

// Call timing
private int callHoldTimeMs;         // Active call duration
private int interCallDelayMs;       // Delay between calls
```

**Key Methods:**
```java
Map<String, String> toJMeterProperties()  // Convert to JMeter -J params
boolean isValid()                         // Validation
```

**Example Usage:**
```java
TrafficProfile profile = new TrafficProfile();
profile.setConcurrentCalls(50);          // 50 threads
profile.setTotalCalls(100000);           // 100,000 calls total
profile.setRampUpSeconds(30);            // Ramp up over 30 seconds
profile.setFailureRate(15.0);            // 15% failure rate
profile.setFailureNode(ActorType.HSS);   // Failures at HSS
profile.setFailureScenario("CONF-AUTH-003");  // Invalid credentials

Map<String, String> jmProps = profile.toJMeterProperties();
// Result: threads=50, loops=2000, failure_rate=15.0, etc.
```

---

### 2. **ConformanceScenario** (`src/main/java/com/tts/demo/model/ConformanceScenario.java`)

**Purpose:** Enum of 3GPP protocol conformance test scenarios for failure injection.

**Scenario Categories:**
1. **SIP Protocol Conformance** (3GPP TS 24.229)
   - `INVALID_SIP_URI` - RFC 3261 syntax violations
   - `MISSING_MANDATORY_HEADER` - Missing From/To/Call-ID headers
   - `INVALID_CSEQ_NUMBER` - CSeq sequence errors
   - `MALFORMED_SDP_OFFER` - RFC 4566 SDP violations

2. **Authentication Conformance** (3GPP TS 33.203)
   - `INVALID_AUTH_HEADER` - Missing auth parameters
   - `EXPIRED_NONCE` - Stale nonce value
   - `WRONG_CREDENTIALS` - XRES mismatch (HSS)

3. **Registration Conformance** (3GPP TS 24.229 §5.1)
   - `REGISTRATION_TIMEOUT` - No 200 OK within T1 timer
   - `INVALID_CONTACT_HEADER` - Missing +g.3gpp.icsi-ref
   - `REGISTRATION_REJECTED_NOT_PROVISIONED` - User not in HSS

4. **Session Setup Conformance** (3GPP TS 24.229 §5.2)
   - `INVITE_TIMEOUT` - No 100 Trying within Timer B
   - `PRECONDITION_FAILURE` - QoS not met (RFC 3312)
   - `RESOURCE_ALLOCATION_FAILURE` - TAS resource exhaustion
   - `INCOMPATIBLE_MEDIA` - No common codec

5. **Call Termination Conformance** (3GPP TS 24.229 §5.3)
   - `BYE_TIMEOUT` - No response within Timer F

6. **Routing Conformance** (3GPP TS 23.228 §5.6)
   - `ROUTING_FAILURE_USER_NOT_FOUND` - Not registered
   - `ROUTING_FAILURE_NO_PATH` - I-CSCF routing failure

7. **Emergency Call Conformance** (3GPP TS 24.229 §5.4)
   - `EMERGENCY_CALL_REJECTION` - Emergency service not enabled

**Each Scenario Includes:**
```java
private final String scenarioId;           // E.g., "CONF-AUTH-003"
private final String scenarioName;         // E.g., "Incorrect Subscriber Credentials"
private final String description;          // Full technical description
private final ActorType affectedNode;      // E.g., ActorType.HSS
private final String expectedResponse;     // E.g., "403 Forbidden"
```

**Example Usage:**
```java
ConformanceScenario scenario = ConformanceScenario.WRONG_CREDENTIALS;
System.out.println(scenario.getScenarioId());        // "CONF-AUTH-003"
System.out.println(scenario.getAffectedNode());      // HSS
System.out.println(scenario.getExpectedResponse());  // "403 Forbidden"
System.out.println(scenario.getDescription());       
// "Authentication response does not match expected value (XRES mismatch)"
```

---

### 3. **TrafficStats** (`src/main/java/com/tts/demo/model/TrafficStats.java`)

**Purpose:** Thread-safe real-time statistics tracking for traffic generation sessions.

**Key Features:**
- **Thread-safe counters** using `AtomicInteger`
- **Concurrent maps** for failure breakdown
- **Response time tracking** with percentile calculations
- **Throughput monitoring** (calls per second)

**Key Metrics:**
```java
// Call counters
int getTotalAttempts()
int getSuccessfulCalls()
int getFailedCalls()

// Rates
double getSuccessRate()         // Percentage
double getFailureRate()         // Percentage
double getCallsPerSecond()      // Throughput

// Response times
double getAverageResponseTime()
long getMedianResponseTime()
long get95thPercentileResponseTime()
long getMinResponseTime()
long getMaxResponseTime()

// Failure breakdown
Map<String, Integer> getFailuresByType()        // By FailureType
Map<ActorType, Integer> getFailuresByNode()     // By network node
Map<String, Integer> getFailuresByResponseCode() // By SIP code
```

**Thread-Safe Recording:**
```java
TrafficStats stats = new TrafficStats("session-001", profile);

// From multiple threads simultaneously
stats.recordAttempt();
stats.recordSuccess(245);  // 245ms response time
stats.recordFailure("Authentication Failure", ActorType.HSS, "403", 180);

// Get real-time stats
System.out.println(stats.getSuccessRate());      // 85.2%
System.out.println(stats.getAverageResponseTime()); // 235ms
System.out.println(stats.getSummaryReport());    // Full report
```

**Summary Report Example:**
```
=== Traffic Generation Summary ===
Session ID: session-001
Duration: 300 seconds

Call Statistics:
  Total Attempts: 100000
  Successful: 85000 (85.00%)
  Failed: 15000 (15.00%)

Performance Metrics:
  Avg Response Time: 245 ms
  Median Response Time: 198 ms
  95th Percentile: 890 ms
  Min/Max: 45 / 3421 ms
  Throughput: 333.33 calls/sec

Failure Breakdown by Type:
  Authentication Failure: 15000 (100.0%)

Failure Breakdown by Node:
  HSS: 15000 (100.0%)
```

---

## UI Design (Traffic Generator Tab)

**Location:** New tab in main TabPane (after Execution tab)

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│                      TRAFFIC GENERATOR                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─── Traffic Volume ──────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Concurrent Calls: [50    ]  (threads)                  │   │
│  │  Total Calls:      [100000]  (total volume)             │   │
│  │  Ramp-Up Time:     [30    ]  seconds                    │   │
│  │  Duration:         [0     ]  seconds (0 = until done)   │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── Failure Injection ────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Failure Rate:     [████████░░░░░░░░] 15%               │   │
│  │                                                          │   │
│  │  Failure Node:     [HSS ▼]                              │   │
│  │                    (P-CSCF, I-CSCF, S-CSCF, HSS, etc.)  │   │
│  │                                                          │   │
│  │  3GPP Scenario:    [CONF-AUTH-003 - Wrong Credentials ▼]│   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── Call Timing ──────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Call Hold Time:   [5000  ]  ms                         │   │
│  │  Inter-Call Delay: [100   ]  ms                         │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [🚀 Start Traffic Generation]  [⏸ Stop]  [📊 Export Data]     │
│                                                                  │
│  ┌─── Live Statistics ──────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Status: RUNNING  |  Elapsed: 00:05:23                  │   │
│  │                                                          │   │
│  │  Calls Completed: 88,542 / 100,000  (88.5%)            │   │
│  │                                                          │   │
│  │  Success Rate:    85.2%  ████████░░  (75,438 calls)     │   │
│  │  Failure Rate:    14.8%  ████░░░░░░  (13,104 calls)     │   │
│  │                                                          │   │
│  │  Throughput:      305 calls/sec                         │   │
│  │  Avg Response:    245 ms                                │   │
│  │  95th Percentile: 890 ms                                │   │
│  │                                                          │   │
│  │  Top Failures:                                          │   │
│  │    • HSS (403): 13,104 (100%)                           │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. **DemoRunner Enhancement**
Current `DemoRunner.executeDemoAsync()` needs enhancement:
```java
// NEW METHOD
public RunResult executeTrafficGeneration(Demo demo, TrafficProfile profile, 
                                          Consumer<TrafficStats> statsCallback)
```

**Key Changes:**
- Accept `TrafficProfile` parameter
- Pass traffic params to JMeter via `-J` properties
- Real-time stats collection during execution
- Callback for live UI updates (statsCallback invoked every second)
- Handle multi-threaded JTL parsing

### 2. **JMeter Test Enhancement**
Tests need to support dynamic failure injection:
```xml
<!-- In JMX file: Use JMeter properties -->
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup">
  <stringProp name="ThreadGroup.num_threads">${__P(threads,10)}</stringProp>
  <stringProp name="ThreadGroup.ramp_time">${__P(rampup,10)}</stringProp>
  <stringProp name="LoopController.loops">${__P(loops,10)}</stringProp>
</ThreadGroup>

<!-- Failure injection logic -->
<IfController>
  <stringProp name="IfController.condition">
    ${__Random(0,100)} &lt; ${__P(failure_rate,0)}
  </stringProp>
  <!-- Inject failure based on scenario -->
  <HTTPSampler>
    <stringProp name="HTTPSampler.path">/inject_error</stringProp>
    <stringProp name="HTTPSampler.method">POST</stringProp>
    <stringProp name="failure_node">${__P(failure_node,)}</stringProp>
    <stringProp name="failure_scenario">${__P(failure_scenario,)}</stringProp>
  </HTTPSampler>
</IfController>
```

### 3. **Data Export**
```java
public class TrafficDataExporter {
    
    public void exportToCsv(TrafficStats stats, String filePath) {
        // CSV format for analysis tools
        // Columns: timestamp, call_id, source, target, response_code, 
        //          response_time, success, failure_type, node
    }
    
    public void exportToJson(TrafficStats stats, String filePath) {
        // JSON format for programmatic analysis
        // Hierarchical: {session, profile, summary, calls[], failures[]}
    }
    
    public void exportToJtl(String sourceJtlPath, String destPath) {
        // Copy raw JMeter JTL file
    }
}
```

---

## Usage Example

### Scenario: Test HSS Authentication Failures at 15% Rate

```java
// 1. Create traffic profile
TrafficProfile profile = new TrafficProfile();
profile.setProfileName("HSS Auth Test - 15% Failure");
profile.setConcurrentCalls(50);
profile.setTotalCalls(100000);
profile.setRampUpSeconds(30);
profile.setFailureRate(15.0);
profile.setFailureNode(ActorType.HSS);
profile.setFailureScenario(ConformanceScenario.WRONG_CREDENTIALS.getScenarioId());
profile.setFailureType(FailureType.AUTHENTICATION_FAILURE);

// 2. Execute traffic generation
Demo demo = demoCatalog.getDemo("sip-volte-call-setup");
DemoRunner runner = new DemoRunner();

TrafficStats stats = new TrafficStats("session-001", profile);

RunResult result = runner.executeTrafficGeneration(demo, profile, 
    liveStats -> {
        // Callback for live UI updates (invoked every second)
        Platform.runLater(() -> updateStatsDisplay(liveStats));
    }
);

// 3. Analyze results
System.out.println(stats.getSummaryReport());
System.out.println("Actual failure rate: " + stats.getFailureRate());
// Expected: ~15% (within margin of error)

// 4. Export data for external analysis
TrafficDataExporter exporter = new TrafficDataExporter();
exporter.exportToCsv(stats, "traffic_data.csv");
exporter.exportToJson(stats, "traffic_stats.json");

// 5. Feed to analysis agent
AnalysisAgent agent = new AnalysisAgent();
FixRecommendation fix = agent.analyzeFailurePatterns(
    "traffic_data.csv",
    ConformanceScenario.WRONG_CREDENTIALS
);
System.out.println(fix.getRecommendation());
// "HSS authentication failure - Check XRES calculation in HSS. 
//  Verify shared K value matches between UE USIM and HSS."
```

---

## Next Steps

### Phase 2: UI Implementation
- [ ] Create `TrafficGeneratorTab.fxml` 
- [ ] Create `TrafficGeneratorController.java`
- [ ] Add real-time statistics charts (JavaFX LineChart)
- [ ] Integrate into MainController tab structure

### Phase 3: DemoRunner Enhancement
- [ ] Add `executeTrafficGeneration()` method
- [ ] Implement multi-threaded JTL parsing
- [ ] Add TrafficStats callback mechanism
- [ ] Handle large-scale log files (100K+ calls)

### Phase 4: Data Export & Analysis Interface
- [ ] Implement `TrafficDataExporter` class
- [ ] CSV export with detailed call logs
- [ ] JSON export with aggregated statistics
- [ ] Define interface contract for analysis agent/tool

### Phase 5: Testing
- [ ] Unit tests for TrafficProfile validation
- [ ] Unit tests for TrafficStats thread safety
- [ ] Integration tests for traffic generation
- [ ] Performance tests with 100K+ calls
- [ ] Verify failure rate accuracy (±2% margin)

### Phase 6: Documentation
- [ ] User guide for traffic generation
- [ ] 3GPP conformance scenario reference
- [ ] Analysis agent integration guide
- [ ] Performance tuning guidelines

---

## Key Benefits

1. **Controlled Failure Injection**: Precise control over failure rates and locations
2. **3GPP Protocol Conformance**: Real-world conformance scenarios based on 3GPP specs
3. **Scalable Load Testing**: Generate 100K+ calls with configurable concurrency
4. **Real-time Monitoring**: Live statistics and throughput visualization
5. **Data Export for Analysis**: CSV/JSON export for external analysis tools
6. **Fix Identification Pipeline**: Clear path from traffic data → failure patterns → fixes

---

## Files Created

1. `src/main/java/com/tts/demo/model/TrafficProfile.java` (248 lines)
2. `src/main/java/com/tts/demo/model/ConformanceScenario.java` (257 lines)
3. `src/main/java/com/tts/demo/model/TrafficStats.java` (285 lines)
4. `docs/TRAFFIC_GENERATION_DESIGN.md` (this file)

**Total:** 790+ lines of production code + documentation
