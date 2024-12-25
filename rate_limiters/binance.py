def binance_wrap_defs():
    return [
        {'regex': 'Get|Post|Delete', 'tags': ['binance_all'], 'count': 1200},  # 1,200 calls/minute
        {'regex': 'Post.*Order', 'tags': ['binance_send_order'], 'count': 10},  # 10 orders/second
    ]

def binance_limits():
    return [
        {'tag': 'binance_all', 'period_sec': 60, 'count': 1200},  # 60 sec, 1200 requests
        {'tag': 'binance_send_order', 'period_sec': 1, 'count': 10},  # 1 sec, 10 orders
    ]
