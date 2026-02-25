#!/usr/bin/env python3
import json
from pathlib import Path
import sys

STATS_JSON = Path('jmeter-report') / 'statistics.json'

if not STATS_JSON.exists():
    print('statistics.json not found.')
    sys.exit(2)

with STATS_JSON.open() as fh:
    data = json.load(fh)

total = data.get('Total')
if not total:
    print('Total section not found in statistics.json')
    sys.exit(2)

# JMeter dashboard percentiles:
# pct1ResTime ~= 90th, pct2ResTime ~= 95th, pct3ResTime ~= 99th
p95 = float(total.get('pct2ResTime', total.get('pct1ResTime', 0)) or 0)
errors = float(total.get('errorPct', 0) or 0)

print(f'p95={p95} ms, errors={errors}%')
sys.exit(0 if p95 <= 2000 and errors <= 1.0 else 1)
