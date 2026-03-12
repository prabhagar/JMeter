# Advanced Load Patterns - Quick Start Guide

## 📌 What You Learned Today

Five essential JMeter load patterns to test different aspects of system performance:

| Pattern | Purpose | When to Use |
|---------|---------|------------|
| **Spike** | Test sudden traffic surge | Verify system handles unexpected load |
| **Soak** | Test stability over time | Find memory leaks, resource issues |
| **Ramp-Up/Down** | Test realistic user arrival | Understand user session patterns |
| **Step-Load** | Find capacity threshold | Identify breaking points |
| **Stress** | Find system breaking point | Understand failure modes |

---

## 🚀 Running the Tests

### Quick Start - Try Spike Test First
```bash
./scripts/run_load_pattern.sh spike
```

### Run Each Pattern
```bash
# Sudden load (1 minute)
./scripts/run_load_pattern.sh spike

# Stability test (1 hour - go get coffee!)
./scripts/run_load_pattern.sh soak

# Realistic pattern (15 minutes)
./scripts/run_load_pattern.sh ramp

# Find capacity (6 minutes)
./scripts/run_load_pattern.sh step

# Stress test (11 minutes)
./scripts/run_load_pattern.sh stress
```

---

## 📊 Understanding the Results

After each test completes:

1. **HTML Report**: Open `jmeter-report-<pattern>-<timestamp>/index.html`
   - Response time graphs
   - Throughput over time
   - Error trends
   - Thread behavior

2. **Raw JTL File**: `results-<pattern>-<timestamp>.jtl`
   - Detailed per-request metrics
   - Individual response times
   - Sample-level data for analysis

---

## 🔍 Analyzing Results Across Patterns

Compare multiple test results:
```bash
# Analyze a single test
python3 scripts/analyze_patterns.py results-spike-*.jtl

# Compare multiple patterns
python3 scripts/analyze_patterns.py results-spike-*.jtl results-ramp-*.jtl results-step-*.jtl

# Compare all soak test runs
python3 scripts/analyze_patterns.py results-soak-*.jtl
```

### Key Metrics to Watch:
- **Response Time (Avg, Min, Max, p95, p99)** → Performance baseline
- **Error Rate %** → System stability
- **Latency** → Network + server processing time  
- **Throughput** → Requests/second capacity
- **Standard Deviation** → Consistency of response times

---

## 📈 Expected Patterns

### ✅ Healthy System
- Spike: Response times spike initially then stabilize
- Soak: Consistent metrics throughout duration
- Ramp: Linear increase in latency as load increases
- Step: p95 stays below SLA at each step
- Stress: Clean failure, not gradual degradation

### ⚠️ Red Flags
- Spike: High error rate immediately
- Soak: Response time degrades over time (memory leak?)
- Ramp: p95 exceeds SLA before peak load
- Step: Large p95/p99 jumps between steps
- Stress: System hangs instead of returning errors

---

## 🎯 Test Sequence Recommendation

**Day 1: Baseline**
```bash
./scripts/run_load_pattern.sh spike      # 1 min
./scripts/run_load_pattern.sh ramp       # 15 min
Total: ~16 minutes
```

**Day 2: Capacity Analysis**
```bash
./scripts/run_load_pattern.sh step       # 6 min
python3 scripts/analyze_patterns.py results-step-*.jtl
Total: ~6 minutes + analysis
```

**Day 3: Stress & Soak** (run overnight!)
```bash
./scripts/run_load_pattern.sh stress     # 11 min
./scripts/run_load_pattern.sh soak       # 1 hour+ (overnight)
```

---

## 🔧 Customizing Tests

Edit JMX files in `jmeter/` directory:

### Modify Thread Count
```xml
<intProp name="ThreadGroup.num_threads">100</intProp>
```

### Modify Ramp-up Time
```xml
<intProp name="ThreadGroup.ramp_time">300</intProp>  <!-- seconds -->
```

### Modify Duration
```xml
<longProp name="ThreadGroup.duration">3600</longProp>  <!-- seconds -->
```

### Change Target Server
```xml
<stringProp name="HTTPSampler.domain">your-server.com</stringProp>
```

---

## 📝 Test Templates

### For Your Own Tests:

1. **Copy an existing test**
   ```bash
   cp jmeter/spike-test.jmx jmeter/my-custom-test.jmx
   ```

2. **Edit in JMeter GUI or directly in XML**
   - Open in JMeter: `jmeter jmeter/my-custom-test.jmx`
   - Or edit XML with your editor

3. **Run it**
   ```bash
   docker run --rm -v "$(pwd)":/test -w /test \
     justb4/jmeter:5.5 \
     -n -t jmeter/my-custom-test.jmx \
     -l results-custom.jtl \
     -e -o jmeter-report-custom
   ```

---

## 🎓 What's Next to Learn?

With load patterns mastered, explore:

1. **Post-Processors** - Extract data from responses
2. **Correlation** - Extract dynamic values (tokens, IDs)
3. **Timers & Think Time** - Add realistic user delays
4. **Controllers** - Conditional logic, loops, transactions
5. **Real-time Monitoring** - InfluxDB + Grafana integration
6. **Distributed Testing** - Multi-machine load generation

---

## 💡 Pro Tips

1. **Always run baseline first** - Understand normal behavior before optimizing

2. **Monitor target system** - Watch CPU, memory, database on server during tests
   ```bash
   # On target server
   top           # CPU/Memory
   iostat -x 1   # Disk I/O
   netstat -s    # Network stats
   ```

3. **Use realistic data** - Update `test-data.csv` with real URLs/paths

4. **Add think time** - Users don't send requests continuously
   - Use Constant Timer: 1000-3000 ms
   - Use Poisson Timer: More realistic random delays

5. **Save your tests** - Git commit custom test plans
   ```bash
   git add jmeter/
   git commit -m "Add load pattern tests for performance analysis"
   ```

6. **Correlate with business metrics** - Link load patterns to real user impact

---

## 📚 Files Created

```
├── ADVANCED-LOAD-PATTERNS.md           # This documentation
├── jmeter/
│   ├── spike-test.jmx                 # Spike pattern (100 threads, 1s ramp)
│   ├── soak-test.jmx                  # Soak pattern (20 threads, 1 hour)
│   ├── ramp-up-ramp-down-test.jmx     # Realistic pattern (15 min)
│   ├── step-load-test.jmx             # Step-load pattern (10→25→50 threads)
│   └── stress-test.jmx                # Stress pattern (500 threads)
│
├── scripts/
│   ├── run_load_pattern.sh            # Easy runner for all patterns
│   ├── analyze_patterns.py            # Results analysis tool
│   └── check_report.py                # Existing report checker
│
└── README.md                           # Updated with new tests
```

---

## ✨ You Now Understand:

✅ Spike testing - Sudden load behavior  
✅ Soak testing - Long-term stability  
✅ Ramp patterns - Realistic user behavior  
✅ Step-load testing - Capacity analysis  
✅ Stress testing - Breaking points  
✅ Pattern comparison - Performance analysis  
✅ Result interpretation - Metrics that matter  

**Happy load testing!** 🚀
