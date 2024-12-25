# rate_limiter/bybit.py

def bybit_wrap_defs():
    return [
        {
            'regex': 'Get|Post|Delete',
            'tags': ['bybit_all'],
            'count': 1000,  # Example: 1,000 calls per minute
        },
        {
            'regex': 'Post.*Order',
            'tags': ['bybit_send_order'],
            'count': 50,  # Example: 50 orders per second
        },
    ]

def bybit_limits():
    return [
        {
            'tag': 'bybit_all',
            'period_sec': 60,  # 60 seconds
            'count': 1000
        },
        {
            'tag': 'bybit_send_order',
            'period_sec': 1,  # 1 second
            'count': 50
        },
    ]
