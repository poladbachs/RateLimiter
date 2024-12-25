# rate_limiter/binance.py

def binance_wrap_defs():
    return [
        {
            'regex': 'Get|Post|Delete',
            'tags': ['all'],
            'count': 1000,  # Allow up to 1000 calls in the period
        },
        {
            'regex': 'Get.*Klines',
            'tags': ['all'],
            'count': 100,  # Specific endpoint limits
        },
        {
            'regex': 'Get.*Account',
            'tags': ['all'],
            'count': 100,
        },
        {
            'regex': 'Post.*Order',
            'tags': ['send_order'],
            'count': 500,
        },
    ]

def binance_limits():
    return [
        {
            'tag': 'all',
            'period_sec': 60,  # 1 minute window
            'count': 1000  # 1000 calls per minute
        },
        {
            'tag': 'send_order',
            'period_sec': 10,  # 10 seconds window
            'count': 500  # 500 send_order calls per 10 seconds
        },
        {
            'tag': 'send_order',
            'period_sec': 24 * 60 * 60,  # Daily window
            'count': 160000
        },
    ]
