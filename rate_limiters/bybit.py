def bybit_wrap_defs():
    return [
        {'regex': 'Get|Post|Delete', 'tags': ['bybit_all'], 'count': 1000},  # 1,000 calls/minute
        {'regex': 'Post.*Order', 'tags': ['bybit_send_order'], 'count': 50},  # 50 orders/second
    ]

def bybit_limits():
    return [
        {'tag': 'bybit_all', 'period_sec': 60, 'count': 1000},  # 60 sec, 1000 requests
        {'tag': 'bybit_send_order', 'period_sec': 1, 'count': 50},  # 1 sec, 50 orders
    ]
