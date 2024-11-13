import datetime

def str_human_duration(sec):
    td = datetime.timedelta(seconds=sec)
    if td.days < 0:
        return '-' + str(datetime.timedelta() - td)
    return str(td)

def str_human_seconds(sec):
    if abs(sec) < 10:
        return f"{sec:.1f}s"
    return f"{sec:.0f}s"

def str_human_meters(meters):
    if abs(meters) < 10:
        return f"{meters:.1f}m"
    return f"{meters:.0f}m"

def str_human_distance(meters):
    if abs(meters) > 1000:
        km = meters / 1000
        return f"{km:.1f}km"
    return f"{meters:.0f}m"

def str_human_percentage(p):
    return f"{p * 100:.1f}%"

def str_count(count, total):
    p = count / total if total > 0 else 0
    return f"#{count}/{total}({p:.1%})"

def str_human_delta(value, reference, str_human_format_func):
    delta = value - reference
    sign = '+' if delta >= 0 else ''
    percentage = delta / reference if reference > 0 else 0
    return f"{sign}{str_human_format_func(delta)} ({sign}{str_human_percentage(percentage)})"

def str_human_delta_sec(value_sec, reference_sec): return str_human_delta(value_sec, reference_sec, str_human_seconds)
def str_human_delta_meters(value_m, reference_m): return str_human_delta(value_m, reference_m, str_human_meters)

def str_lat_lng(lat, lng):
    return f"{lat:.6f},{lng:.6f}"

print(f"test str_human_duration(123) -> {str_human_duration(123)}")