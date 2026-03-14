#!/usr/bin/env node

// analyze_patterns.js
// Simple JS script to analyze JMeter .jtl (CSV) results files.
// Usage: node scripts/analyze_patterns.js results-*.jtl

const fs = require('fs');
const path = require('path');

function parseCsv(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  const lines = raw.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(',');
  const rows = lines.slice(1).map((line) => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((header, i) => {
      obj[header] = values[i] === undefined ? '' : values[i];
    });
    return obj;
  });

  return rows;
}

function toNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function percentile(sorted, p) {
  if (!sorted.length) return 0;
  const idx = Math.min(sorted.length - 1, Math.floor(sorted.length * p));
  return sorted[idx];
}

function analyze(filePath) {
  const samples = parseCsv(filePath);
  if (!samples.length) {
    console.warn(`No data found in ${filePath}`);
    return null;
  }

  const responseTimes = [];
  const latencies = [];
  let successCount = 0;
  let errorCount = 0;

  for (const sample of samples) {
    const elapsed = toNumber(sample.elapsed, 0);
    const success = String(sample.success).toLowerCase() === 'true';
    const latency = toNumber(sample.Latency, elapsed);

    responseTimes.push(elapsed);
    latencies.push(latency);

    if (success) successCount += 1;
    else errorCount += 1;
  }

  responseTimes.sort((a, b) => a - b);
  latencies.sort((a, b) => a - b);

  const total = successCount + errorCount;
  const errorRate = total ? (errorCount / total) * 100 : 0;

  const stats = {
    totalSamples: total,
    success: successCount,
    errors: errorCount,
    errorRatePct: errorRate,
    responseTime: {
      min: responseTimes[0] ?? 0,
      max: responseTimes[responseTimes.length - 1] ?? 0,
      avg: responseTimes.reduce((a, b) => a + b, 0) / (responseTimes.length || 1),
      median: percentile(responseTimes, 0.5),
      p95: percentile(responseTimes, 0.95),
      p99: percentile(responseTimes, 0.99),
    },
    latency: {
      min: latencies[0] ?? 0,
      max: latencies[latencies.length - 1] ?? 0,
      avg: latencies.reduce((a, b) => a + b, 0) / (latencies.length || 1),
      median: percentile(latencies, 0.5),
      p95: percentile(latencies, 0.95),
      p99: percentile(latencies, 0.99),
    },
  };

  return stats;
}

function printStats(name, stats) {
  if (!stats) return;

  const fmt = (n) => `${Math.round(n * 100) / 100}`;

  console.log('\n' + '='.repeat(60));
  console.log(`RESULT: ${name}`);
  console.log('='.repeat(60));

  console.log('Total Samples: ', stats.totalSamples);
  console.log('Success:       ', stats.success);
  console.log('Errors:        ', stats.errors);
  console.log('Error Rate:    ', fmt(stats.errorRatePct) + '%');

  console.log('\nResponse Time (ms):');
  console.log('  min:  ', stats.responseTime.min);
  console.log('  avg:  ', fmt(stats.responseTime.avg));
  console.log('  p95:  ', stats.responseTime.p95);
  console.log('  p99:  ', stats.responseTime.p99);
  console.log('  max:  ', stats.responseTime.max);

  console.log('\nLatency (ms):');
  console.log('  min:  ', stats.latency.min);
  console.log('  avg:  ', fmt(stats.latency.avg));
  console.log('  p95:  ', stats.latency.p95);
  console.log('  p99:  ', stats.latency.p99);
  console.log('  max:  ', stats.latency.max);
}

function main() {
  const args = process.argv.slice(2);
  // If the user provides no arguments, automatically search for results-*.jtl files.
  const patterns = args.length ? args : ['results-*.jtl'];

  const reports = [];

  for (const filePattern of patterns) {
    const resolved = filePattern.includes('*')
      ? fs.readdirSync(process.cwd()).filter((f) => f.match(new RegExp(filePattern.replace('*', '.*'))))
      : [filePattern];

    for (const filePath of resolved) {
      if (!fs.existsSync(filePath)) continue;
      const stats = analyze(filePath);
      printStats(path.basename(filePath), stats);
      reports.push({ name: path.basename(filePath), stats });
    }
  }

  if (reports.length > 1) {
    console.log('\n' + '='.repeat(60));
    console.log('COMPARISON:');
    console.log('='.repeat(60));
    console.log('Name'.padEnd(30), 'Error %'.padEnd(10), 'Avg RT'.padEnd(10), 'p95 RT'.padEnd(10));

    reports.forEach((report) => {
      const s = report.stats;
      const name = report.name.padEnd(30);
      const err = fmt(s.errorRatePct).padEnd(10);
      const avg = fmt(s.responseTime.avg).padEnd(10);
      const p95 = String(s.responseTime.p95).padEnd(10);
      console.log(name, err, avg, p95);
    });
  }
}

main();
