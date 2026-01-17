# PTW Webhooks Documentation

## Overview
The PTW system supports outbound webhooks to notify external systems of permit lifecycle events in real-time.

## Configuration

### Creating a Webhook Endpoint
```bash
POST /api/v1/ptw/webhooks/
{
  "name": "ERP Integration",
  "url": "https://your-system.com/webhooks/ptw",
  "secret": "your_secret_key_here",
  "enabled": true,
  "events": [
    "permit_created",
    "permit_approved",
    "permit_rejected",
    "permit_activated",
    "permit_completed"
  ],
  "project": 1  // Optional: null for global
}
```

### Managing Webhooks
- **List**: `GET /api/v1/ptw/webhooks/`
- **Retrieve**: `GET /api/v1/ptw/webhooks/{id}/`
- **Update**: `PUT /api/v1/ptw/webhooks/{id}/`
- **Delete**: `DELETE /api/v1/ptw/webhooks/{id}/`
- **Test**: `POST /api/v1/ptw/webhooks/{id}/test/`
- **Delivery Logs**: `GET /api/v1/ptw/webhooks/{id}/deliveries/`

## Supported Events
- `permit_created` - New permit created
- `workflow_initiated` - Workflow started
- `verifier_assigned` - Verifier assigned
- `approval_required` - Sent to approver
- `permit_approved` - Permit approved
- `permit_rejected` - Permit rejected
- `permit_activated` - Work started
- `permit_completed` - Work completed
- `permit_expired` - Permit expired
- `closeout_completed` - Closeout finished
- `isolation_verified` - Isolation verified
- `escalation_triggered` - SLA breach

## Payload Format
```json
{
  "event": "permit_approved",
  "timestamp": "2024-01-15T10:30:00Z",
  "permit_id": 123,
  "permit_number": "PTW-2024-001",
  "project_id": 5,
  "data": {
    "status": "approved",
    "permit_type": "Hot Work",
    "location": "Building A - Level 3",
    "risk_level": "high",
    "approved_by": "John Doe",
    "comments": "Approved with conditions"
  }
}
```

## Security - Signature Verification

All webhook requests include an `X-Athens-Signature` header with HMAC SHA256 signature.

### Python Verification
```python
import hmac
import hashlib
import json

def verify_signature(payload_body, signature_header, secret):
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    received_sig = signature_header.replace('sha256=', '')
    return hmac.compare_digest(expected_sig, received_sig)

# Usage
payload = request.body.decode('utf-8')
signature = request.headers.get('X-Athens-Signature')
secret = 'your_secret_key_here'

if verify_signature(payload, signature, secret):
    # Process webhook
    data = json.loads(payload)
else:
    # Reject - invalid signature
    return 401
```

### Node.js Verification
```javascript
const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  const receivedSig = signature.replace('sha256=', '');
  return crypto.timingSafeEqual(
    Buffer.from(expectedSig),
    Buffer.from(receivedSig)
  );
}

// Usage
app.post('/webhooks/ptw', (req, res) => {
  const signature = req.headers['x-athens-signature'];
  const payload = JSON.stringify(req.body);
  
  if (verifySignature(payload, signature, process.env.WEBHOOK_SECRET)) {
    // Process webhook
    console.log('Event:', req.body.event);
    res.sendStatus(200);
  } else {
    res.sendStatus(401);
  }
});
```

## Delivery Guarantees
- **Idempotency**: Same event won't be sent twice within the same hour
- **Timeout**: 10 seconds
- **Retry**: Currently best-effort (future: exponential backoff with Celery)
- **Logging**: All delivery attempts are logged for debugging

## Best Practices
1. **Validate signatures** - Always verify the HMAC signature
2. **Respond quickly** - Return 200 OK within 10 seconds
3. **Process async** - Queue webhook processing for heavy operations
4. **Monitor failures** - Check delivery logs regularly
5. **Use HTTPS** - Only HTTPS URLs are recommended
6. **Rotate secrets** - Periodically update webhook secrets

## Troubleshooting

### Check Delivery Logs
```bash
GET /api/v1/ptw/webhooks/{id}/deliveries/
```

### Common Issues
- **Timeout**: Endpoint taking >10s to respond
- **SSL Error**: Invalid/expired SSL certificate
- **401/403**: Signature verification failing
- **Connection refused**: Endpoint not accessible

### Testing
```bash
POST /api/v1/ptw/webhooks/{id}/test/
```
Sends a test event with sample permit data.
