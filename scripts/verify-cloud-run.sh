#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "Usage: $0 <project_id> <api_url> <task_handler_url> <agent_url> <reporting_url>" >&2
  exit 1
fi

PROJECT_ID=$1
API_URL=$2
TASK_HANDLER_URL=$3
AGENT_URL=$4
REPORTING_URL=$5

# Validate that all arguments are non-empty
if [[ -z "$PROJECT_ID" ]] || [[ -z "$API_URL" ]] || [[ -z "$TASK_HANDLER_URL" ]] || [[ -z "$AGENT_URL" ]] || [[ -z "$REPORTING_URL" ]]; then
  echo "Usage: $0 <project_id> <api_url> <task_handler_url> <agent_url> <reporting_url>" >&2
  echo "Error: All arguments must be non-empty" >&2
  exit 1
fi
QUEUE="projects/$PROJECT_ID/locations/us-central1/queues/analysis-queue"

print_step() { echo "[verify] $1"; }

print_step "Triggering async analysis via API service"
JOB_RESPONSE=$(curl -s -X POST "$API_URL/analyze/async-task" -H "Content-Type: application/json" -d '{"company":"Acme","frameworks":["porter"],"depth":"quick"}') || true
echo "$JOB_RESPONSE"

print_step "Listing Cloud Tasks queue"
gcloud tasks list --queue="$QUEUE" --location=us-central1 --limit=5 || true

print_step "Getting authentication token"
TOKEN_OUTPUT=$(gcloud auth print-identity-token 2>&1)
TOKEN_EXIT_CODE=$?

if [[ $TOKEN_EXIT_CODE -ne 0 ]]; then
  echo "Error: Failed to get authentication token" >&2
  echo "$TOKEN_OUTPUT" >&2
  exit 1
fi

TOKEN="$TOKEN_OUTPUT"
if [[ -z "$TOKEN" ]]; then
  echo "Error: Authentication token is empty" >&2
  exit 1
fi

print_step "Probing agent service"
curl -s -o /dev/null -w "status=%{http_code}\n" -X POST "$AGENT_URL/execute" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"company":"SmokeCo","frameworks":["porter"],"depth":"quick"}' || true

print_step "Probing reporting service"
curl -s -o /dev/null -w "status=%{http_code}\n" -X POST "$REPORTING_URL/reports/pdf" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"executive_summary":{"company_name":"SmokeCo","industry":"Test","analysis_date":"2024-01-01T00:00:00","key_findings":["finding"],"strategic_recommendation":"Go","confidence_score":0.8,"supporting_evidence":[],"next_steps":[]},"company_research":{"company_name":"SmokeCo","description":"desc","products_services":[],"target_market":"","key_competitors":[],"recent_news":[],"sources":[]},"financial_snapshot":{"ticker":"SMK","risk_assessment":"low"},"framework_analysis":{},"recommendations":["Ship"]}' || true

print_step "Probing task handler directly"
curl -s -o /dev/null -w "status=%{http_code}\n" -X POST "$TASK_HANDLER_URL/tasks/process" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"job_id":"smoke-run","analysis_request":{"company":"SmokeCo","frameworks":["swot"],"depth":"quick"}}' || true

print_step "Done"
