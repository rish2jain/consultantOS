# ConsultantOS Observability - Cloud Deployment Guide

## Deploying Observability Stack on GCP

This guide covers deploying the observability stack on Google Cloud Platform.

## Architecture

```
┌─────────────────────────────────────┐
│   Cloud Run (ConsultantOS API)      │
│   - Exports metrics on /metrics      │
└────────────┬────────────────────────┘
             │
             │ Scrapes metrics
             ↓
┌─────────────────────────────────────┐
│   Cloud Monitoring (Prometheus)     │
│   - Collects metrics                 │
│   - Stores in Cloud Storage          │
└────────────┬────────────────────────┘
             │
             │ Queries
             ↓
┌─────────────────────────────────────┐
│   Cloud Run (Grafana)               │
│   - Visualizes metrics               │
│   - Hosted dashboard                 │
└─────────────────────────────────────┘
             ↑
             │
             │ Alerts via
             │ Cloud Pub/Sub
             │
┌─────────────────────────────────────┐
│   Cloud Run (AlertManager)          │
│   - Routes alerts                    │
│   - Sends to Slack/Email             │
└─────────────────────────────────────┘
```

## Option 1: Self-Hosted Observability Stack on Cloud Run

### Prerequisites

```bash
# Set environment variables
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"

# Create a GCP project (if needed)
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
```

### Step 1: Create Cloud SQL Instance (for Prometheus)

```bash
gcloud sql instances create consultantos-prometheus \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=$REGION \
  --allocated-ip-range=default
```

### Step 2: Create Cloud Storage Bucket

```bash
gsutil mb gs://$PROJECT_ID-prometheus-data

# Set up lifecycle policy for retention
cat > /tmp/lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 15}
      }
    ]
  }
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://$PROJECT_ID-prometheus-data
```

### Step 3: Create Firestore Database (for Alert History)

```bash
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native
```

### Step 4: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  container.googleapis.com \
  cloudsql.googleapis.com \
  storage-api.googleapis.com \
  cloudtrace.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

### Step 5: Create Service Account

```bash
gcloud iam service-accounts create consultantos-observability \
  --display-name="ConsultantOS Observability"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Step 6: Deploy Prometheus to Cloud Run

```bash
# Create Dockerfile for Prometheus
cat > /tmp/Dockerfile.prometheus << 'EOF'
FROM prom/prometheus:latest

COPY prometheus/prometheus.yml /etc/prometheus/prometheus.yml
COPY prometheus/alerts.yml /etc/prometheus/rules/alerts.yml

EXPOSE 9090
EOF

# Build and push to Container Registry
gcloud builds submit --dockerfile=/tmp/Dockerfile.prometheus \
  --tag=gcr.io/$PROJECT_ID/consultantos-prometheus

# Deploy to Cloud Run
gcloud run deploy consultantos-prometheus \
  --image=gcr.io/$PROJECT_ID/consultantos-prometheus \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --service-account=consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 7: Deploy Grafana to Cloud Run

```bash
# Create Dockerfile for Grafana
cat > /tmp/Dockerfile.grafana << 'EOF'
FROM grafana/grafana:latest

ENV GF_SECURITY_ADMIN_USER=admin
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_SERVER_ROOT_URL=https://consultantos-grafana.run.app

COPY grafana/provisioning /etc/grafana/provisioning
COPY grafana/dashboards /var/lib/grafana/dashboards

EXPOSE 3000
EOF

# Build and push
gcloud builds submit --dockerfile=/tmp/Dockerfile.grafana \
  --tag=gcr.io/$PROJECT_ID/consultantos-grafana

# Deploy
gcloud run deploy consultantos-grafana \
  --image=gcr.io/$PROJECT_ID/consultantos-grafana \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=3600
```

### Step 8: Deploy AlertManager to Cloud Run

```bash
# Create Dockerfile for AlertManager
cat > /tmp/Dockerfile.alertmanager << 'EOF'
FROM prom/alertmanager:latest

COPY alertmanager/config.yml /etc/alertmanager/config.yml

EXPOSE 9093
EOF

# Build and push
gcloud builds submit --dockerfile=/tmp/Dockerfile.alertmanager \
  --tag=gcr.io/$PROJECT_ID/consultantos-alertmanager

# Deploy
gcloud run deploy consultantos-alertmanager \
  --image=gcr.io/$PROJECT_ID/consultantos-alertmanager \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600
```

## Option 2: Use Google Cloud Monitoring (Recommended for Production)

### Prerequisites

```bash
gcloud config set project $PROJECT_ID
gcloud services enable monitoring.googleapis.com
```

### Step 1: Configure ConsultantOS API to Export Metrics

Update `consultantos/api/main.py` to export to Cloud Monitoring:

```python
from google.cloud import monitoring_v3
from prometheus_client import CollectorRegistry

# Initialize Cloud Monitoring exporter
def setup_cloud_monitoring():
    try:
        from google.cloud.monitoring_dashboards import v1

        # Export Prometheus metrics to Cloud Monitoring
        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{os.getenv('GCP_PROJECT_ID')}"

        # Configure metric export
        # This happens automatically when prometheus_client is configured
        # with Google Cloud Monitoring remote write

    except ImportError:
        logger.warning("Cloud Monitoring client not available")
```

### Step 2: Deploy ConsultantOS with Cloud Monitoring

```bash
gcloud run deploy consultantos \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "\
    GEMINI_API_KEY=${GEMINI_API_KEY},\
    TAVILY_API_KEY=${TAVILY_API_KEY},\
    GCP_PROJECT_ID=${PROJECT_ID}" \
  --service-account=consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 3: Create Cloud Monitoring Dashboards

```bash
# Export metrics to Cloud Monitoring dashboard
gcloud monitoring dashboards create --config-from-file=- <<EOF
{
  "displayName": "ConsultantOS System Overview",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "API Success Rate",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"custom.googleapis.com/consultantos_api_requests_total\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
```

### Step 4: Set Up Cloud Alerts

```bash
gcloud alpha monitoring policies create \
  --notification-channels=[YOUR_CHANNEL_ID] \
  --display-name="ConsultantOS API Error Rate" \
  --condition-display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=120s
```

## Monitoring with Datadog (Alternative)

```python
# Add to requirements.txt
datadog>=0.45.0

# Initialize in main.py
from datadog import initialize, api

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}

initialize(**options)

# Export metrics
from datadog.api.metrics import Metrics

Metrics.send(
    metric='consultantos.api.requests',
    points=rate,
    tags=['service:consultantos', 'endpoint:/analyze']
)
```

## Monitoring with New Relic (Alternative)

```python
# Add to requirements.txt
newrelic>=8.4.0

# Initialize in main.py
import newrelic.agent

newrelic.agent.initialize('newrelic.ini')

@newrelic.agent.wsgi_application()
def application(environ, start_response):
    return app(environ, start_response)
```

## Cost Estimation

| Component | Service | Cost/Month (est.) |
|-----------|---------|------------------|
| API | Cloud Run | $10-50 |
| Prometheus | Cloud Run | $5-20 |
| Grafana | Cloud Run | $5-10 |
| AlertManager | Cloud Run | $2-5 |
| Cloud Monitoring | Built-in | Free (with limits) |
| Cloud Storage | GCS | $0.20-5 |
| Cloud SQL | MySQL | $10-50 |
| **Total** | | **$32-140** |

### Cost Optimization

1. Use Cloud Monitoring (free tier) instead of self-hosted Prometheus
2. Reduce Cloud Run memory allocation during off-peak hours
3. Use committed use discounts for persistent services
4. Implement data retention policies (15-30 days)
5. Use Cloud Storage lifecycle policies for automatic deletion

## Scaling Considerations

### Horizontal Scaling
- Cloud Run automatically scales based on traffic
- Set max instances: `--max-instances=100`
- Set min instances: `--min-instances=1`

### Vertical Scaling
- Increase memory for Prometheus: `--memory=4Gi`
- Increase CPU: `--cpu=4`

### Database Scaling
- Use Cloud SQL scaling policies
- Set up read replicas for high traffic

## Security

### Network Security
```bash
# Use VPC connector for private communication
gcloud compute networks vpc-access connectors create consultantos-connector \
  --region=$REGION \
  --subnet=default

# Deploy Cloud Run with VPC connector
gcloud run deploy consultantos \
  --vpc-connector=consultantos-connector \
  --vpc-egress=all
```

### Authentication
```bash
# Require authentication for services
gcloud run deploy consultantos-prometheus \
  --no-allow-unauthenticated

# Grant access to specific service accounts
gcloud run add-iam-policy-binding consultantos-prometheus \
  --member=serviceAccount:consultantos-observability@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.invoker
```

### Secret Management
```bash
# Store secrets in Secret Manager
gcloud secrets create slack-webhook --data-file=-
echo "https://hooks.slack.com/services/..." | gcloud secrets create slack-webhook --data-file=-

# Reference in Cloud Run
gcloud run deploy alertmanager \
  --set-env-vars="SLACK_WEBHOOK=projects/$PROJECT_ID/secrets/slack-webhook/versions/latest"
```

## Monitoring Cloud Run Services

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos" \
  --limit=50 \
  --format=json

# View metrics
gcloud monitoring metrics-list --filter="metric.type:cloud.run"

# Set up log-based metrics
gcloud logging metrics create consultantos_errors \
  --log-filter='resource.type=cloud_run_revision AND severity=ERROR'
```

## Troubleshooting

### Services not connecting
```bash
# Check Cloud Run service URLs
gcloud run services list

# Verify VPC connector
gcloud compute networks vpc-access connectors list

# Test connectivity
curl https://consultantos-prometheus.run.app/metrics
```

### Metrics not appearing
```bash
# Check metric export
gcloud monitoring metrics-list --filter="metric.type:custom.googleapis.com/consultantos*"

# Verify Cloud Monitoring API enabled
gcloud services enable monitoring.googleapis.com

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:consultantos-observability*"
```

### Alert not firing
```bash
# Check notification channels
gcloud alpha monitoring channels list

# Verify alert policy
gcloud alpha monitoring policies list

# Test alert notification
gcloud alpha monitoring policies update [POLICY_ID] --test
```

## Rollback Procedure

```bash
# View deployment revisions
gcloud run revisions list

# Rollback to previous revision
gcloud run deploy consultantos \
  --image=gcr.io/$PROJECT_ID/consultantos:previous-tag \
  --region=$REGION
```

## Next Steps

1. Deploy to Cloud Run following Option 1 or 2
2. Configure Slack webhooks for alerts
3. Set up PagerDuty integration for critical alerts
4. Establish on-call rotation
5. Schedule weekly alert threshold reviews
6. Plan monthly disaster recovery drills

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Prometheus Remote Storage](https://prometheus.io/docs/prometheus/latest/storage/#remote-storage-integrations)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
