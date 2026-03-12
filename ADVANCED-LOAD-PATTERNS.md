# Advanced Load Patterns in JMeter

## Overview
Load patterns define how virtual users (threads) are ramped up, sustained, and ramped down during a test. Different patterns reveal different types of performance issues.

---

## 1. SPIKE TEST 🔺
**Purpose**: Test how the system handles sudden traffic spikes without gradual ramp-up.

**Characteristics**:
- Threads jump to max instantly (or very quickly)
- Exposes issues with resource exhaustion
- Reveals connection pool limits, cache behavior
- Real-world example: Black Friday sales, viral content, breaking news

**Configuration**:
```
- Threads: 100
- Ramp-up: 1 second (near-instant)
- Duration: 60 seconds
- Then drop to 0 (no ramp-down)
```

**Metrics to Watch**:
- Response time spike at start
- Error rate spike
- Thread creation time
- Memory consumption jump

**Test Plan File**: `spike-test.jmx`

---

## 2. SOAK TEST 🏊
**Purpose**: Test system stability under moderate, continuous load over extended periods.

**Characteristics**:
- Moderate thread count
- Long duration (hours or days)
- Continuous request stream
- Detects memory leaks, connection leaks, resource degradation

**Configuration**:
```
- Threads: 20 (moderate load)
- Ramp-up: 120 seconds (gradual)
- Duration: 3600+ seconds (1+ hours)
- Sustained load throughout
```

**Metrics to Watch**:
- Memory usage over time (should remain stable)
- Response time degradation (should stay consistent)
- Error rate increase over time
- Database connection pool exhaustion

**Test Plan File**: `soak-test.jmx`

---

## 3. RAMP-UP + RAMP-DOWN 📈📉
**Purpose**: Realistic load pattern mimicking real user behavior (users join and leave gradually).

**Characteristics**:
- Gradual increase to peak
- Sustained at peak
- Gradual decrease
- Tests system behavior across all load levels

**Configuration**:
```
- Phase 1 Ramp-up: 300 seconds (10 to 100 threads)
- Phase 2 Sustain: 600 seconds (hold at 100)
- Phase 3 Ramp-down: 300 seconds (100 back to 0)
```

**Metrics to Watch**:
- Performance across all load levels
- Recovery after load increase
- Cleanup during ramp-down
- Resource release patterns

**Test Plan File**: `ramp-up-ramp-down-test.jmx`

---

## 4. STEP-LOAD TEST 👣
**Purpose**: Identify capacity thresholds and breaking points under incremental load increases.

**Characteristics**:
- Load increases in discrete steps
- Each step held for duration to stabilize
- Stop when response time or errors become unacceptable

**Configuration**:
```
- Step 1: 10 threads, 120 seconds
- Step 2: 25 threads, 120 seconds
- Step 3: 50 threads, 120 seconds
- Step 4: 100 threads, 120 seconds
- Step 5: 150 threads, 120 seconds
(Keep stepping up until breaking point)
```

**Metrics to Watch**:
- Breaking-point load level
- Response time trend across steps
- Error rate per step
- Resource utilization per step

**Test Plan File**: `step-load-test.jmx`

---

## 5. WAVE TEST (COMBINATION) 🌊
**Purpose**: Simulate realistic traffic patterns with peaks and valleys.

**Characteristics**:
- Multiple ramp-ups and ramp-downs
- Mimics multi-user session behavior
- Tests recovery between peaks

**Configuration**:
```
Wave 1: Ramp 0→50 (60s) → Sustain 50 (120s) → Ramp 50→0 (60s)
Wave 2: Ramp 0→75 (60s) → Sustain 75 (120s) → Ramp 75→0 (60s)
Wave 3: Ramp 0→100 (60s) → Sustain 100 (120s) → Ramp 100→0 (60s)
```

---

## 6. STRESS TEST ⚠️
**Purpose**: Find breaking point and failure mode of the system.

**Characteristics**:
- Aggressive ramp-up
- High thread count
- Continues until system fails
- May cause SLA breaches intentionally

**Configuration**:
```
- Start: 10 threads
- Ramp-up: 10 seconds
- Increment: +10 threads every 60 seconds
- Max threads: 500+ (keep going!)
- Duration: Until failure or resource exhaustion
```

**Metrics to Watch**:
- Exact breaking point
- Error types at failure
- Last successful response time
- Resource exhaustion indicators

**Test Plan File**: `stress-test.jmx`

---

## Comparison Table

| Pattern | Threads | Ramp-up | Duration | Purpose |
|---------|---------|---------|----------|---------|
| **Spike** | High | Very Short (<5s) | Short | Sudden load |
| **Soak** | Moderate | Gradual | Very Long (hours) | Stability |
| **Ramp-Up/Down** | Progressive | Gradual | Medium | Realistic users |
| **Step-Load** | Progressive | Stepped | Long | Capacity threshold |
| **Wave** | Progressive | Multiple cycles | Long | Multi-peak behavior |
| **Stress** | Very High | Aggressive | Until failure | Breaking point |

---

## Recommended Sequence

1. **Start with Spike** → Understand baseline breaking point
2. **Run Ramp-Up/Down** → Understand realistic scenario
3. **Run Step-Load** → Find capacity curve
4. **Run Soak** → Verify stability over time
5. **Analyze results** → Optimize based on findings

---

## How to Run Different Patterns

Each pattern has a corresponding `.jmx` file in `jmeter/` directory:

### Spike Test
```bash
./scripts/run_jmeter_docker.sh jmeter/spike-test.jmx
```

### Soak Test (might take hours!)
```bash
./scripts/run_jmeter_docker.sh jmeter/soak-test.jmx
```

### Step-Load Test
```bash
./scripts/run_jmeter_docker.sh jmeter/step-load-test.jmx
```

---

## Key Thread Group Settings

### For Spike Tests:
```
Threads: 100+
Ramp-up: 1
Scheduler: enabled (60 seconds)
```

### For Soak Tests:
```
Threads: 20
Ramp-up: 120
Scheduler: enabled (3600+ seconds)
```

### For Step-Load:
Use **multiple Thread Groups** with offset scheduling:
- Group 1: Start at 0s
- Group 2: Start at 120s
- Group 3: Start at 240s
(Each adds 25 threads, creating step effect)

---

## Performance Metrics to Track

- **Response Time (Avg, Min, Max, p50, p95, p99)**
- **Throughput (requests/second)**
- **Error Rate (%)**
- **Active Threads over time**
- **Memory consumption**
- **CPU utilization**
- **Database connections**
- **Network I/O**

---

## Tips for Realistic Load Patterns

1. **Add Think Time**: Users spend time reading responses
   ```
   Use Constant Timer or Gaussian Random Timer
   ```

2. **Add Connection Reuse**: Real browsers keep-alive
   ```
   Configure in HTTP Request Defaults
   ```

3. **Add Request Variety**: Not all requests are identical
   ```
   Use CSV data or random elements
   ```

4. **Monitor System Under Test**: Don't just watch JMeter
   ```
   Monitor CPU, Memory, I/O, Database on target server
   ```

5. **Correlate with Business Metrics**: Link load to real KPIs
   ```
   Check SLA compliance, error types, business impact
   ```
