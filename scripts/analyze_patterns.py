#!/usr/bin/env python3
"""
Analyze and compare results from different load pattern tests.
Usage: python3 analyze_patterns.py <results_file.jtl> [results_file2.jtl ...]
"""

import csv
import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

def parse_jtl(filepath):
    """Parse JMeter JTL CSV results file."""
    results = {
        'samples': [],
        'stats': defaultdict(list)
    }
    
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results['samples'].append(row)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    
    return results

def analyze_results(results, name):
    """Analyze JTL results and calculate metrics."""
    if not results or not results['samples']:
        print(f"No samples found in {name}")
        return None
    
    samples = results['samples']
    response_times = []
    latencies = []
    success_count = 0
    error_count = 0
    
    for sample in samples:
        try:
            # JMeter columns: timeStamp, elapsed, label, responseCode, responseMessage, threadName, dataType, success, failureMessage, bytes, sentBytes, grpThreads, allThreads, Latency, IdleTime, Connect
            elapsed = int(sample.get('elapsed', 0))
            success = sample.get('success', 'false').lower() == 'true'
            latency = int(sample.get('Latency', elapsed))
            
            response_times.append(elapsed)
            latencies.append(latency)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        except (ValueError, KeyError):
            continue
    
    if not response_times:
        return None
    
    total_samples = success_count + error_count
    error_rate = (error_count / total_samples * 100) if total_samples > 0 else 0
    
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
            'p95': sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 0 else 0,
            'p99': sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) > 0 else 0,
            'stdev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
        },
        'latency': {
            'min': min(latencies),
            'max': max(latencies),
            'avg': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'p95': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 0 else 0,
            'p99': sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 0 else 0,
        },
        'throughput': total_samples / (len(samples) / 1000) if samples else 0,  # Rough estimate
    }
    
    return metrics

def print_metrics(metrics):
    """Pretty print metrics."""
    print(f"\n{'='*70}")
    print(f"📊 TEST: {metrics['name']}")
    print(f"{'='*70}")
    
    print(f"\n✅ Sample Count:")
    print(f"   Total:       {metrics['total_samples']:,} samples")
    print(f"   Success:     {metrics['success']:,}")
    print(f"   Errors:      {metrics['errors']:,}")
    print(f"   Error Rate:  {metrics['error_rate_pct']:.2f}%")
    
    print(f"\n⏱️  Response Time (ms):")
    rt = metrics['response_time']
    print(f"   Min:         {rt['min']:>10} ms")
    print(f"   Avg:         {rt['avg']:>10.2f} ms")
    print(f"   Median:      {rt['median']:>10} ms")
    print(f"   p95:         {rt['p95']:>10} ms")
    print(f"   p99:         {rt['p99']:>10} ms")
    print(f"   Max:         {rt['max']:>10} ms")
    print(f"   StdDev:      {rt['stdev']:>10.2f} ms")
    
    print(f"\n🔃 Latency (ms):")
    lat = metrics['latency']
    print(f"   Min:         {lat['min']:>10} ms")
    print(f"   Avg:         {lat['avg']:>10.2f} ms")
    print(f"   Median:      {lat['median']:>10} ms")
    print(f"   p95:         {lat['p95']:>10} ms")
    print(f"   p99:         {lat['p99']:>10} ms")
    print(f"   Max:         {lat['max']:>10} ms")
    
    print(f"\n📈 Throughput:")
    print(f"   ~{metrics['throughput']:.2f} requests/sec")

def compare_metrics(all_metrics):
    """Compare multiple test results."""
    if len(all_metrics) < 2:
        return
    
    print(f"\n\n{'='*70}")
    print("📋 COMPARISON SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Test Name':<25} {'Samples':<12} {'Error %':<10} {'Avg RT':<12} {'p95 RT':<12}")
    print(f"{'-'*70}")
    
    for m in all_metrics:
        print(f"{m['name']:<25} {m['total_samples']:<12,} "
              f"{m['error_rate_pct']:<10.2f} {m['response_time']['avg']:<12.1f} "
              f"{m['response_time']['p95']:<12}")
    
    print(f"\n💡 Key Insights:")
    
    # Find best/worst performers
    best_response = min(all_metrics, key=lambda x: x['response_time']['avg'])
    worst_response = max(all_metrics, key=lambda x: x['response_time']['avg'])
    worst_errors = max(all_metrics, key=lambda x: x['error_rate_pct'])
    
    print(f"   Best Response Time:  {best_response['name']} ({best_response['response_time']['avg']:.1f}ms avg)")
    print(f"   Worst Response Time: {worst_response['name']} ({worst_response['response_time']['avg']:.1f}ms avg)")
    print(f"   Highest Errors:      {worst_errors['name']} ({worst_errors['error_rate_pct']:.2f}%)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_patterns.py <results.jtl> [results2.jtl ...]")
        print("\nExample:")
        print("  python3 scripts/analyze_patterns.py results-spike-*.jtl")
        print("  python3 scripts/analyze_patterns.py results-spike-*.jtl results-soak-*.jtl")
        sys.exit(1)
    
    all_metrics = []
    
    for filepath in sys.argv[1:]:
        print(f"📂 Parsing: {filepath}")
        results = parse_jtl(filepath)
        
        if results:
            metrics = analyze_results(results, Path(filepath).stem)
            if metrics:
                print_metrics(metrics)
                all_metrics.append(metrics)
    
    if all_metrics:
        compare_metrics(all_metrics)
    
    print("\n")

if __name__ == '__main__':
    main()
