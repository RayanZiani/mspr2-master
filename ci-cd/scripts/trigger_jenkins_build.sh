#!/usr/bin/env bash
set -euo pipefail

JENKINS_URL="${JENKINS_URL:-http://127.0.0.1:8080}"
JOB_NAME="${JENKINS_JOB:-FutureKawa-CI-CD}"
USER="${JENKINS_USER:-admin}"
PASS="${JENKINS_PASS:?JENKINS_PASS requis}"

CRUMB_JSON=$(curl -sf -u "${USER}:${PASS}" -c /tmp/jenkins_cookies.txt "${JENKINS_URL}/crumbIssuer/api/json")
CRUMB=$(echo "${CRUMB_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin)['crumb'])")
FIELD=$(echo "${CRUMB_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin)['crumbRequestField'])")

HTTP=$(curl -s -o /tmp/jenkins_build_resp.txt -w "%{http_code}" \
  -u "${USER}:${PASS}" \
  -b /tmp/jenkins_cookies.txt \
  -H "${FIELD}: ${CRUMB}" \
  -X POST "${JENKINS_URL}/job/${JOB_NAME}/build")

echo "Build déclenché — HTTP ${HTTP}"
if [[ "${HTTP}" != "201" && "${HTTP}" != "200" ]]; then
  cat /tmp/jenkins_build_resp.txt
  exit 1
fi
