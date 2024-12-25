def scale_rate_limits(rate_limits, scale_factor):
    scaled_limits = []
    for limit in rate_limits:
        scaled_limit = limit.copy()
        scaled_limit['count'] = int(limit['count'] * scale_factor)
        scaled_limits.append(scaled_limit)
    return scaled_limits

def parse_config(file_path):
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def log_to_file(filename, message):
    with open(filename, "a") as file:
        file.write(f"{message}\n")
