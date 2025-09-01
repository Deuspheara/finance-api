# Subscription Tiers and Usage Limits

## Overview

The system implements a tiered subscription model with usage-based limits. All users start with a free tier and can upgrade to premium through Stripe integration.

## Subscription Tiers

### Free Tier

**Price:** $0/month
**Features:**
- Portfolio analysis: 5 analyses per month
- LLM chat requests: 10 requests per month
- Basic financial tools
- Community support

**Limitations:**
- Limited to basic portfolio analysis features
- Lower priority for LLM responses
- No advanced analytics

### Premium Tier

**Price:** Managed through Stripe
**Features:**
- Portfolio analysis: 100 analyses per month
- LLM chat requests: 1000 requests per month
- Advanced portfolio analytics with NumPy/Pandas
- Priority LLM responses
- Email support
- Advanced financial tools

**Benefits:**
- Higher usage limits
- Enhanced performance with scientific computing libraries
- Priority customer support
- Advanced features and analytics

## Usage Limits Implementation

### Limit Tracking

Limits are tracked per user per feature:

```python
TIER_LIMITS = {
    SubscriptionTier.FREE: TierLimits(
        portfolio_limit=5,
        llm_requests_limit=10
    ),
    SubscriptionTier.PREMIUM: TierLimits(
        portfolio_limit=100,
        llm_requests_limit=1000
    )
}
```

### Monthly Reset

- Limits reset on the first day of each month
- Based on subscription creation date
- Usage tracking is continuous across sessions

### Feature Mapping

```python
# Portfolio Analysis
feature_name = "portfolio"
limit = limits.portfolio_limit

# LLM Chat
feature_name = "llm_requests"
limit = limits.llm_requests_limit
```

## Usage Monitoring

### Current Usage Query

Users can check their current usage:

```bash
curl -X GET http://localhost:8000/api/v1/usage \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Usage Response Format

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "feature_name": "portfolio",
    "timestamp": "2024-01-01T10:30:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "feature_name": "llm_requests",
    "timestamp": "2024-01-01T11:15:00Z"
  }
]
```

## Limit Enforcement

### Pre-Request Validation

Before processing any request, the system:

1. Retrieves user's subscription tier
2. Counts current usage for the feature
3. Compares against tier limits
4. Rejects request if limit exceeded

### Error Responses

**Portfolio Limit Exceeded:**
```json
{
  "detail": "Usage limit exceeded for portfolio"
}
```

**LLM Limit Exceeded:**
```json
{
  "detail": "Usage limit exceeded for LLM requests"
}
```

## Subscription Changes

### Upgrading from Free to Premium

1. User initiates upgrade through external payment system
2. Stripe processes payment and sends webhook
3. System updates user tier to "premium"
4. Limits immediately increase to premium levels
5. User gains access to premium features

### Downgrading from Premium to Free

1. Subscription cancellation through Stripe
2. Stripe sends cancellation webhook
3. System maintains premium access until period ends
4. At period end, tier changes to "free"
5. Limits reduce to free tier levels

### Webhook Processing

```python
# Example webhook handler (processed by Celery)
@process_stripe_event.task
def handle_subscription_update(event):
    if event.type == 'customer.subscription.updated':
        # Update user tier based on subscription status
        update_user_subscription_tier(event.data.object)
    elif event.type == 'customer.subscription.deleted':
        # Handle subscription cancellation
        downgrade_user_to_free(event.data.object)
```

## Billing Integration

### Stripe Configuration

- **API Key:** Configured via `STRIPE_API_KEY`
- **Webhook Secret:** Configured via `STRIPE_WEBHOOK_SECRET`
- **Premium Price ID:** Configured via `STRIPE_PREMIUM_PLAN_PRICE_ID`

### Customer Management

- Each user has a corresponding Stripe customer
- Customer ID stored in subscription record
- Subscription status synced via webhooks

## Usage Analytics

### Metrics Collection

The system collects usage metrics for monitoring:

- Total active subscriptions by tier
- Feature usage rates
- Limit exceedance rates
- Subscription churn rates

### Prometheus Metrics

```python
# Example metrics
subscriptions_active_total = Gauge(
    'subscriptions_active_total',
    'Total active subscriptions',
    ['tier']
)

finance_tool_usage_total = Counter(
    'finance_tool_usage_total',
    'Total finance tool usage',
    ['tool', 'tier']
)
```

## Best Practices

### For Users

1. **Monitor Usage:** Regularly check usage via API
2. **Plan Upgrades:** Upgrade before reaching limits
3. **Optimize Usage:** Batch requests when possible
4. **Track Billing:** Monitor subscription status

### For Developers

1. **Graceful Degradation:** Handle limit exceeded errors
2. **Clear Messaging:** Provide informative error messages
3. **Usage Transparency:** Make limits visible to users
4. **Webhook Reliability:** Implement webhook retry logic

## Future Enhancements

### Planned Features

- **Usage Alerts:** Email notifications when approaching limits
- **Flexible Limits:** Custom limits for enterprise customers
- **Usage Analytics:** Detailed usage dashboards
- **Bulk Operations:** Higher limits for bulk processing
- **API Rate Limits:** Separate from feature usage limits

### Scaling Considerations

- **Database Optimization:** Efficient usage queries
- **Caching Strategy:** Redis caching for limit checks
- **Background Processing:** Async usage logging
- **Monitoring:** Comprehensive metrics collection