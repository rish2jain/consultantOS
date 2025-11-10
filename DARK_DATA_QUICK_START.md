# Dark Data Email Mining - Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm

# Install NLTK data for sentiment
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### 2. Set Environment Variables

Create `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
ENCRYPTION_KEY=your_32_byte_encryption_key_base64

# Optional
GCP_PROJECT_ID=your_gcp_project
```

Generate encryption key:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Add to .env as ENCRYPTION_KEY
```

### 3. Gmail API Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create/select project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:8080/oauth2callback`
6. Download client configuration

---

## Quick Test

### Run PII Detector Tests

```bash
pytest tests/test_pii_detector.py -v
```

Expected output:
```
tests/test_pii_detector.py::test_detect_credit_card PASSED
tests/test_pii_detector.py::test_detect_ssn PASSED
tests/test_pii_detector.py::test_detect_email_address PASSED
...
========== 25 passed in 5.2s ==========
```

### Run Dark Data Agent Tests

```bash
pytest tests/test_dark_data_agent.py -v
```

### Run All Tests with Coverage

```bash
pytest tests/test_pii_detector.py tests/test_dark_data_agent.py tests/test_gmail_connector.py --cov=consultantos --cov-report=term-missing
```

Expected coverage: **91%+**

---

## Usage Examples

### Example 1: PII Detection

```python
from consultantos.security.pii_detector import quick_detect_pii, quick_anonymize

# Detect PII
text = "Contact me at john@example.com or call 555-1234. SSN: 123-45-6789"
result = await quick_detect_pii(text)

print(f"Has PII: {result.has_pii}")
print(f"Types found: {result.pii_types_found}")
print(f"High risk count: {result.high_risk_count}")

# Anonymize
anonymized = await quick_anonymize(text, strategy="replace")
print(f"Anonymized: {anonymized}")
# Output: "Contact me at <EMAIL_ADDRESS> or call <PHONE_NUMBER>. SSN: <US_SSN>"
```

### Example 2: Gmail Connector

```python
from consultantos.connectors.gmail_connector import GmailConnector

# Initialize
client_config = {
    "web": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

connector = GmailConnector(client_config)

# Start OAuth flow
auth_url = await connector.authenticate()
print(f"Visit: {auth_url}")

# After user authorizes...
credentials = await connector.complete_authentication(authorization_code="...")

# Search emails
emails = await connector.search_emails(
    keywords=["acquisition", "partnership"],
    date_range={"start": "2024-01-01", "end": "2024-12-31"},
    max_results=50
)

print(f"Found {len(emails)} emails")
```

### Example 3: Dark Data Agent

```python
from consultantos.agents.dark_data_agent import DarkDataAgent
from consultantos.models.dark_data import EmailSource, EmailProvider

# Initialize agent
agent = DarkDataAgent(timeout=180)

# Setup source
source = EmailSource(
    provider=EmailProvider.GMAIL,
    credentials_id="cred_123",
    user_email="user@example.com",
    filters={"keywords": ["acquisition"]},
    enabled=True
)

# Execute analysis
result = await agent.execute({
    'source': source,
    'connector': connector,
    'max_emails': 100,
    'anonymization_strategy': 'replace'
})

if result['success']:
    insight = result['data']
    print(f"Analyzed: {insight.emails_analyzed} emails")
    print(f"PII detected: {insight.pii_detected}")
    print(f"Risk score: {insight.risk_score}")
    print(f"Companies found: {insight.entities_found.companies}")
    print(f"Sentiment: {insight.sentiment.polarity}")
```

---

## API Usage

### Start Server

```bash
python -m uvicorn consultantos.api.main:app --reload --port 8080
```

### API Endpoints

#### 1. Connect Email Source

```bash
curl -X POST http://localhost:8080/dark-data/connect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "provider": "gmail",
    "redirect_uri": "http://localhost:8080/oauth2callback"
  }'
```

Response:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "csrf_state_token"
}
```

#### 2. Analyze Emails

```bash
curl -X POST http://localhost:8080/dark-data/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "source_id": "src_abc123",
    "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
    "keywords": ["acquisition", "partnership"],
    "max_emails": 100,
    "anonymization_strategy": "replace"
  }'
```

Response:
```json
{
  "status": "success",
  "insight": {
    "emails_analyzed": 100,
    "pii_detected": true,
    "pii_summary": {"EMAIL_ADDRESS": 45, "PHONE_NUMBER": 20},
    "risk_score": 0.65,
    "entities_found": {
      "companies": ["Tesla", "Apple"],
      "people": ["Elon Musk"],
      "financial_figures": [{"amount": 50000000, "currency": "USD"}]
    },
    "sentiment": {
      "overall_score": 0.6,
      "polarity": "positive"
    }
  }
}
```

#### 3. List Connected Sources

```bash
curl -X GET http://localhost:8080/dark-data/sources \
  -H "X-API-Key: your_api_key"
```

#### 4. Disconnect Source

```bash
curl -X DELETE http://localhost:8080/dark-data/disconnect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"source_id": "src_abc123"}'
```

---

## Security Best Practices

### Production Deployment

1. **Use Secret Manager**:
   ```python
   # Store in GCP Secret Manager
   from google.cloud import secretmanager
   client = secretmanager.SecretManagerServiceClient()
   # Store: ENCRYPTION_KEY, GMAIL_CLIENT_SECRET
   ```

2. **Enable HTTPS**:
   ```bash
   # Use Cloud Run with HTTPS
   gcloud run deploy dark-data-api --allow-unauthenticated
   ```

3. **Rotate Keys**:
   ```python
   # Rotate encryption keys every 90 days
   new_key = Fernet.generate_key()
   # Re-encrypt all credentials with new key
   ```

4. **Monitor Audit Logs**:
   ```bash
   # Query audit logs daily
   curl -X GET http://localhost:8080/dark-data/audit-logs \
     -H "X-API-Key: admin_api_key"
   ```

### GDPR Compliance

1. **Data Retention**:
   ```python
   # Run daily cleanup
   from consultantos.security.gdpr_compliance import get_gdpr_service
   gdpr = get_gdpr_service()
   deleted = await gdpr.cleanup_expired_data()
   ```

2. **User Deletion**:
   ```python
   # Delete all user data on request
   deleted_counts = await gdpr.delete_user_data(user_id)
   ```

3. **Data Export**:
   ```python
   # Export user data on request
   export = await gdpr.export_user_data(user_id)
   # Provide to user within 30 days
   ```

---

## Troubleshooting

### Common Issues

**1. Import Error: No module named 'presidio_analyzer'**

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_sm
```

**2. OAuth Error: Invalid redirect URI**

- Check redirect URI matches exactly in Google Cloud Console
- Default: `http://localhost:8080/oauth2callback`

**3. PII Detection Returns Empty**

- Check confidence threshold (default: 0.6)
- Verify spaCy model is installed: `python -m spacy validate`

**4. Rate Limit Exceeded**

- Gmail API limit: 250 requests/minute
- Reduce batch size or add delays between requests

**5. Encryption Key Error**

Generate valid key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Tuning

### Optimize PII Detection

```python
# Reduce confidence threshold for higher recall
detector = PIIDetector(confidence_threshold=0.5)

# Limit entity types for faster processing
result = await detector.detect_pii(
    text,
    entity_types=['EMAIL_ADDRESS', 'PHONE_NUMBER', 'CREDIT_CARD']
)
```

### Batch Processing

```python
# Process emails in batches
batch_size = 50
for i in range(0, len(message_ids), batch_size):
    batch = message_ids[i:i+batch_size]
    emails = await connector.batch_get_emails(batch)
```

### Caching

```python
# Cache PII detection results
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_pii_detection(text_hash):
    return await detector.detect_pii(text)
```

---

## Monitoring

### Key Metrics

```python
# Track in production
metrics = {
    'emails_processed': insight.emails_analyzed,
    'pii_detected_rate': len([r for r in pii_results if r.has_pii]) / len(pii_results),
    'average_risk_score': insight.risk_score,
    'processing_time': insight.analysis_duration
}
```

### Alerts

```python
# Alert on high-risk detections
if insight.risk_score > 0.8:
    send_alert(f"High-risk email analysis: {insight.risk_score}")

# Alert on PII threshold
if insight.pii_summary.get('CREDIT_CARD', 0) > 5:
    send_alert("Multiple credit cards detected in emails")
```

---

## Next Steps

1. **Week 7-8**: Implement Outlook and Slack connectors
2. **Week 9**: Advanced NLP and topic modeling
3. **Week 10**: Machine learning for anomaly detection
4. **Week 11**: React dashboard for insights visualization

---

## Support

- **Documentation**: See `DARK_DATA_IMPLEMENTATION_SUMMARY.md`
- **Tests**: Run `pytest tests/ -v --cov=consultantos`
- **Issues**: Check logs in `consultantos/logs/`

## Security Contact

For security issues or GDPR requests:
- Email: security@consultantos.ai (example)
- Response time: Within 72 hours (GDPR requirement)
