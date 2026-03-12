#!/usr/bin/env bash
# Advanced Load Patterns Test Runner

set -euo pipefail

IMAGE=justb4/jmeter:5.5
OUTDIR_BASE=jmeter-report
RESULTS_BASE=results

show_usage() {
    echo "Usage: $0 <pattern> [-d DURATION_OVERRIDE]"
    echo ""
    echo "Available patterns:"
    echo "  spike       - Sudden load spike (100 threads, instant ramp-up)"
    echo "  soak        - Long-running moderate load (20 threads, 1 hour)"
    echo "  ramp        - Realistic ramp-up and ramp-down (100 threads, 15 min)"
    echo "  step        - Incremental step-load (10→25→50 threads, 6 min total)"
    echo "  stress      - Aggressive stress test (500 threads, 10 min)"
    echo ""
    echo "Examples:"
    echo "  $0 spike"
    echo "  $0 soak"
    echo "  $0 ramp"
    exit 1
}

if [ $# -lt 1 ]; then
    show_usage
fi

PATTERN=$1
DURATION_OVERRIDE=${2:-}

case "$PATTERN" in
    spike)
        TEST=jmeter/spike-test.jmx
        NAME="Spike Load Test"
        DESC="Sudden load: 100 threads, instant ramp-up, 60 seconds"
        TIMEFRAME="1 minute"
        ;;
    soak)
        TEST=jmeter/soak-test.jmx
        NAME="Soak Test"
        DESC="Stability: 20 threads, gradual ramp-up, 1 hour duration"
        TIMEFRAME="1+ hour"
        ;;
    ramp)
        TEST=jmeter/ramp-up-ramp-down-test.jmx
        NAME="Ramp-Up & Ramp-Down Test"
        DESC="Realistic: 100 threads, 5 min ramp-up, 10 min sustain, auto ramp-down"
        TIMEFRAME="15 minutes"
        ;;
    step)
        TEST=jmeter/step-load-test.jmx
        NAME="Step Load Test"
        DESC="Capacity: 3 steps (10→25→50 threads), 2 min each"
        TIMEFRAME="6 minutes"
        ;;
    stress)
        TEST=jmeter/stress-test.jmx
        NAME="Stress Test"
        DESC="Breaking point: 500 threads, 1 min ramp-up, 10 min duration"
        TIMEFRAME="11 minutes"
        ;;
    *)
        echo "Error: Unknown pattern '$PATTERN'"
        show_usage
        ;;
esac

# Create timestamped output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTDIR="${OUTDIR_BASE}-${PATTERN}-${TIMESTAMP}"
RESULTS="${RESULTS_BASE}-${PATTERN}-${TIMESTAMP}.jtl"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  JMETER ADVANCED LOAD PATTERN TEST                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Pattern:  $NAME"
echo "Desc:     $DESC"
echo "Duration: $TIMEFRAME"
echo "Test:     $TEST"
echo "Results:  $RESULTS"
echo "Report:   $OUTDIR/index.html"
echo ""
echo "Starting test at $(date)..."
echo "⏱️  Please wait..."
echo ""

# Run JMeter in Docker
mkdir -p "${OUTDIR}"
docker run --rm -v "$(pwd)":/test -w /test ${IMAGE} \
  -n -t ${TEST} \
  -l ${RESULTS} \
  -e -o /test/${OUTDIR}

echo ""
echo "✅ Test completed!"
echo ""
echo "📊 Report generated: $OUTDIR/index.html"
echo "📈 Raw results: $RESULTS"
echo ""
echo "📋 Quick Summary:"
echo "   Open the HTML report in a browser to see detailed charts and metrics."
echo ""
