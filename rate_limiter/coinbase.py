def coinbase_wrap_defs():
    return [
        {
            'regex': 'Get|Post|Delete',
            'tags': ['coinbase_all'],
            'count': 3000,  # 3,000 calls per minute
        },
        {
            'regex': 'Post.*Order',
            'tags': ['coinbase_send_order'],
            'count': 50,  # 50 orders per second
        },
    ]

def coinbase_limits():
    return [
        {
            'tag': 'coinbase_all',
            'period_sec': 60,  # 60 seconds
            'count': 3000
        },
        {
            'tag': 'coinbase_send_order',
            'period_sec': 1,  # 1 second
            'count': 50
        },
    ]
