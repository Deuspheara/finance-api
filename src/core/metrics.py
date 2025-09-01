from prometheus_client import Counter

# Subscription metrics
subscriptions_active_total = Counter(
    'subscriptions_active_total',
    'Total number of active subscriptions',
    ['tier']
)

# Finance metrics
finance_tool_usage_total = Counter(
    'finance_tool_usage_total',
    'Total usage of finance tools',
    ['tool_name', 'user_id']
)

# Privacy/GDPR metrics
gdpr_actions_total = Counter(
    'gdpr_actions_total',
    'Total GDPR actions performed',
    ['action_type']
)