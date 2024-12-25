def binance_wrap_defs():
    return [
        {
            'regex': 'Get|Post|Delete',
            'tags': ['binance_all'],
            'count': 1200,  # 1,200 calls per minute
        },
        {
            'regex': 'Post.*Order',
            'tags': ['binance_send_order'],
            'count': 10,  # 10 orders per second
        },
    ]

def binance_limits():
    return [
        {
            'tag': 'binance_all',
            'period_sec': 60,  # 60 seconds
            'count': 1200
        },
        {
            'tag': 'binance_send_order',
            'period_sec': 1,  # 1 second
            'count': 10
        },
    ]
