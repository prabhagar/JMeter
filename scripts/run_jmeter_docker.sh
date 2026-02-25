#!/usr/bin/env bash
set -euo pipefail
IMAGE=justb4/jmeter:5.5
TEST=jmeter/simple-http-test.jmx
OUTDIR=jmeter-report
RESULTS=results.jtl
rm -rf ${OUTDIR}
docker run --rm -v "$(pwd)":/test -w /test ${IMAGE} -n -t ${TEST} -l ${RESULTS} -e -o /test/${OUTDIR}
echo "Report generated in ${OUTDIR}/index.html"
