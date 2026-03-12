# 🎓 Understanding analyze_patterns.py for Beginners

## Real Analogy: Think of a Restaurant 🍽️

Imagine you're a restaurant manager analyzing customer data. This script does the same:

```
1. READ the data → "Open the customer logbook"
2. EXTRACT info → "Get each customer's payment amount"
3. CALCULATE → "Find average payment, min, max, etc"
4. DISPLAY → "Show the summary nicely"
5. COMPARE → "Compare this month vs last month"
```

Let's understand it with REAL DATA, not confusing code.

---

## 📂 Part 1: Reading the File (What is filepath?)

### The File: `results-spike-20260312.jtl`

This is what a `.jtl` file looks like (it's just a CSV file):

```
timeStamp,elapsed,label,responseCode,success,Latency,Connect
1615542600000,150,HTTP Request,200,true,95,45
1615542601000,165,HTTP Request,200,true,110,48
1615542602000,145,HTTP Request,200,true,92,44
1615542603000,500,HTTP Request,500,false,450,46
1615542604000,170,HTTP Request,200,true,115,50
```

**What each column means:**
- `timeStamp` = When the request happened
- `elapsed` = How long it took (milliseconds) ← **WE NEED THIS**
- `responseCode` = HTTP status (200=OK, 500=ERROR)
- `success` = Did it work? (true/false) ← **WE NEED THIS**
- `Latency` = Server response time ← **WE NEED THIS**

---

### Reading Step-by-Step

#### **Step 1: User types command**
```bash
python3 scripts/analyze_patterns.py results-spike-20260312.jtl
```

This means:
- Run Python script = `analyze_patterns.py`
- The FILENAME to analyze = `results-spike-20260312.jtl`

#### **Step 2: Python gets the filename**

```python
# In Python, sys.argv is like "command parameters"
# 
# sys.argv[0] = 'scripts/analyze_patterns.py'  (the script name)
# sys.argv[1] = 'results-spike-20260312.jtl'   (what you passed)
# sys.argv[2] = 'results-spike-20260313.jtl'   (if you passed another file)
```

#### **Step 3: The main() function loops through files**

```python
def main():
    for filepath in sys.argv[1:]:  # "for each FILENAME you gave me"
        print(f"📂 Parsing: {filepath}")
        results = parse_jtl(filepath)  # "Open and read this file"
```

**Translation:**
```
FOR each filepath in the list of files:
    - Print which file we're reading
    - Call parse_jtl() to open and read it
```

---

## 🔍 Part 2: How parse_jtl() Opens and Reads the File

```python
def parse_jtl(filepath):
    """Parse JMeter JTL CSV results file."""
    results = {
        'samples': [],  # Empty list ready to hold data
        'stats': defaultdict(list)
    }
    
    try:
        with open(filepath, 'r') as f:  # Open file for reading ('r')
            reader = csv.DictReader(f)  # Treat as CSV with headers
            for row in reader:          # Loop through each line
                results['samples'].append(row)  # Add to list
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    
    return results
```

**Breaking it down:**

### `with open(filepath, 'r') as f:`

```
Think of it like opening a book:
  - filepath = "which book to open" 
  - 'r' = "read mode" (not write/delete)
  - as f = "call it 'f' while I'm reading"
  - with = "when done, automatically close the book"

Real example:
  with open('results-spike-20260312.jtl', 'r') as f:
       # f is now your open file
```

### `csv.DictReader(f)`

```
CSV file looks like:
┌─────────────┬─────────┬──────────┐
│ timeStamp   │ elapsed │ success  │
├─────────────┼─────────┼──────────┤
│ 1615542600  │ 150     │ true     │
│ 1615542601  │ 165     │ true     │
└─────────────┴─────────┴──────────┘

DictReader converts EACH ROW into a DICTIONARY:

Row 1 becomes:
{
  'timeStamp': '1615542600',
  'elapsed': '150',
  'success': 'true'
}

Row 2 becomes:
{
  'timeStamp': '1615542601',
  'elapsed': '165',
  'success': 'true'
}

So you can access by name instead of by number!
```

### `for row in reader:`

```python
for row in reader:
    results['samples'].append(row)
```

**This loops through EACH ROW:**

```
LOOP ITERATION 1:
  row = {'timeStamp': '1615542600', 'elapsed': '150', 'success': 'true'}
  results['samples'].append(row)
  results['samples'] now has 1 dictionary
  
LOOP ITERATION 2:
  row = {'timeStamp': '1615542601', 'elapsed': '165', 'success': 'true'}
  results['samples'].append(row)
  results['samples'] now has 2 dictionaries

LOOP ITERATION 3:
  row = {'timeStamp': '1615542602', 'elapsed': '145', 'success': 'true'}
  results['samples'].append(row)
  results['samples'] now has 3 dictionaries

... and so on for every row ...
```

**At the end, results['samples'] looks like:**
```python
[
  {'timeStamp': '1615542600', 'elapsed': '150', 'success': 'true'},
  {'timeStamp': '1615542601', 'elapsed': '165', 'success': 'true'},
  {'timeStamp': '1615542602', 'elapsed': '145', 'success': 'true'},
  {'timeStamp': '1615542603', 'elapsed': '500', 'success': 'false'},
  {'timeStamp': '1615542604', 'elapsed': '170', 'success': 'true'},
]
```

---

## 🔄 Part 3: How Variables Are Mapped (The Complex Stuff)

Now we have all the data. Let's extract what we need!

### The analyze_results() Function

```python
def analyze_results(results, name):
    samples = results['samples']  # Get the list of all rows
    response_times = []   # Empty list for collecting times
    latencies = []        # Empty list for collecting latencies
    success_count = 0     # Counter (starts at 0)
    error_count = 0       # Counter (starts at 0)
    
    # Loop through each individual sample
    for sample in samples:
        elapsed = int(sample.get('elapsed', 0))
        success = sample.get('success', 'false').lower() == 'true'
        latency = int(sample.get('Latency', elapsed))
        
        response_times.append(elapsed)
        latencies.append(latency)
        
        if success:
            success_count += 1
        else:
            error_count += 1
```

**Let's trace through with REAL DATA:**

```
samples = [
  sample[0]: {'elapsed': '150', 'success': 'true', 'Latency': '95'},
  sample[1]: {'elapsed': '165', 'success': 'true', 'Latency': '110'},
  sample[2]: {'elapsed': '500', 'success': 'false', 'Latency': '450'},
]

LOOP - Iteration 1 (sample[0]):
────────────────────────────────
sample = {'elapsed': '150', 'success': 'true', 'Latency': '95'}

elapsed = int(sample.get('elapsed', 0))
           → int('150')
           → 150
           → elapsed = 150

success = sample.get('success', 'false').lower() == 'true'
           → 'true'.lower() == 'true'
           → 'true' == 'true'
           → True
           → success = True

latency = int(sample.get('Latency', 95))
           → int('95')
           → 95
           → latency = 95

response_times.append(elapsed)
→ response_times = [150]

latencies.append(latency)
→ latencies = [95]

if success:  (True)
    success_count += 1
    → success_count = 1


LOOP - Iteration 2 (sample[1]):
────────────────────────────────
sample = {'elapsed': '165', 'success': 'true', 'Latency': '110'}

elapsed = 165
success = True
latency = 110

response_times.append(165)
→ response_times = [150, 165]

latencies.append(110)
→ latencies = [95, 110]

success_count += 1
→ success_count = 2


LOOP - Iteration 3 (sample[2]):
────────────────────────────────
sample = {'elapsed': '500', 'success': 'false', 'Latency': '450'}

elapsed = 500
success = False  (because 'false' != 'true')
latency = 450

response_times.append(500)
→ response_times = [150, 165, 500]

latencies.append(450)
→ latencies = [95, 110, 450]

if success:  (False)
    error_count += 1
    → error_count = 1

AFTER LOOP COMPLETES:
response_times = [150, 165, 500]
latencies = [95, 110, 450]
success_count = 2
error_count = 1
```

---

## 📊 Part 4: Building the Metrics Dictionary (Line 68)

```python
metrics = {
    'name': name,
    'total_samples': total_samples,
    'success': success_count,
    'errors': error_count,
    'error_rate_pct': error_rate,
    'response_time': {
        'min': min(response_times),
        'max': max(response_times),
        'avg': statistics.mean(response_times),
        'median': statistics.median(response_times),
        'p95': sorted(response_times)[int(len(response_times) * 0.95)],
        'p99': sorted(response_times)[int(len(response_times) * 0.99)],
        'stdev': statistics.stdev(response_times),
    },
    'latency': {
        'min': min(latencies),
        'max': max(latencies),
        'avg': statistics.mean(latencies),
    },
}
```

**Using our data:**

```
response_times = [150, 165, 500]
latencies = [95, 110, 450]
success_count = 2
error_count = 1
total_samples = 3
error_rate = 33.33%

Building metrics:

'name': 'results-spike-20260312'  ← The filename

'response_time': {
    'min': min([150, 165, 500]) = 150
    'max': max([150, 165, 500]) = 500
    'avg': statistics.mean([150, 165, 500]) = (150+165+500)/3 = 271.67
    'median': statistics.median([150, 165, 500]) = 165
    'p95': sorted([150, 165, 500])[int(3 * 0.95)]
           = sorted list[2]
           = [150, 165, 500][2]
           = 500
}

'latency': {
    'min': 95
    'max': 450
    'avg': 218.33
}

So metrics looks like:
{
  'name': 'results-spike-20260312',
  'success': 2,
  'errors': 1,
  'total_samples': 3,
  'error_rate_pct': 33.33,
  'response_time': {
    'min': 150,
    'avg': 271.67,
    'max': 500,
    'median': 165,
    'p95': 500,
    'p99': 500,
    'stdev': 142.5
  },
  'latency': {
    'min': 95,
    'avg': 218.33,
    'max': 450
  }
}
```

---

## 🖨️ Part 5: Displaying (print_metrics)

```python
def print_metrics(metrics):
    print(f"\n{'='*70}")
    print(f"📊 TEST: {metrics['name']}")
    print(f"{'='*70}")
    
    print(f"\n✅ Sample Count:")
    print(f"   Total: {metrics['total_samples']:,} samples")
    print(f"   Success: {metrics['success']:,}")
    print(f"   Errors: {metrics['errors']:,}")
    print(f"   Error Rate: {metrics['error_rate_pct']:.2f}%")
```

**What gets printed:**

```
======================================================================
📊 TEST: results-spike-20260312
======================================================================

✅ Sample Count:
   Total: 3 samples
   Success: 2
   Errors: 1
   Error Rate: 33.33%
```

---

## 🌊 The Complete Flow (All Together)

```
USER COMMAND:
  python3 scripts/analyze_patterns.py results-spike-20260312.jtl

      ↓

main() function RUNS:
  sys.argv[1] = 'results-spike-20260312.jtl'
  
      ↓

parse_jtl('results-spike-20260312.jtl') RUNS:
  Opens file
  Reads each line
  Converts to dictionary
  Returns list of 1000 samples:
  [
    {'elapsed': '150', 'success': 'true'},
    {'elapsed': '165', 'success': 'true'},
    ... 998 more rows ...
  ]
  
      ↓

analyze_results(results, name) RUNS:
  Loops through all 1000 samples
  Extracts elapsed times → [150, 165, 200, ..., 500]
  Extracts success/error → success_count = 980, error_count = 20
  Calculates statistics:
    - avg = 195.3 ms
    - p95 = 310 ms
    - error_rate = 2%
  Returns metrics dictionary with all these numbers
  
      ↓

print_metrics(metrics) RUNS:
  Takes the metrics dictionary
  Prints it nicely:
  
  ======================================================================
  📊 TEST: results-spike-20260312
  ======================================================================
  
  ✅ Sample Count:
     Total:       1,000 samples
     Success:     980
     Errors:      20
     Error Rate:  2.00%
  
  ⏱️  Response Time (ms):
     Min:                100 ms
     Avg:              195.30 ms
     Median:           180 ms
     p95:              310 ms
     p99:              420 ms
     Max:              500 ms
```

---

## 🔑 Key Python Concepts Simplified

| Concept | Simple Meaning | Example |
|---------|---|---|
| **Variable** | A box holding a value | `elapsed = 150` |
| **List `[]`** | A bag holding multiple items | `response_times = [150, 165, 200]` |
| **Dictionary `{}`** | A labeled box (key-value pairs) | `sample = {'elapsed': '150', 'success': 'true'}` |
| **For loop** | "Do this for each item" | `for row in reader:` |
| **Append** | "Add to the end" | `list.append(item)` |
| **Function** | "A reusable block of code" | `def parse_jtl(filepath):` |
| **String** | Text in quotes | `'hello'` or `"hello"` |
| **Int** | Whole number | `150` |
| **Boolean** | True or False | `success = True` |

---

## 📝 Quick Cheat Sheet

```python
# Reading a CSV:
with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)  # row is like {'col1': 'value1', 'col2': 'value2'}

# Getting values from dictionary:
row.get('elapsed', 0)     # Get 'elapsed', or use 0 if missing
row['elapsed']            # Get 'elapsed' (crashes if missing)

# Converting types:
int('150')                # Convert string '150' to number 150
float('150.5')            # Convert to decimal number

# Lists and calculations:
min([150, 165, 200])      # Returns 150
max([150, 165, 200])      # Returns 200
statistics.mean([150, 165, 200])  # Returns 171.67

# String formatting:
f"Test: {filename}"       # Puts variable value in string
f"{value:,}"              # With commas (1000 → 1,000)
f"{value:.2f}"            # 2 decimal places (10.5 → 10.50)
```

---

## ✨ Summary

**The script's job:**
1. **READ** - Open .jtl file, read each request
2. **EXTRACT** - Get response times, success/failure
3. **CALCULATE** - Find min, max, avg, percentiles
4. **DISPLAY** - Print formatted report
5. **COMPARE** - Show which test performed best

**The data flow:**
```
File → List of dicts → Extracted lists → Calculated stats → Formatted output
```

Does this make more sense now? Want me to explain any specific line in detail? 😊

