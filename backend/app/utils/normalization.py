def min_max_scale(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.0
    return (value - min_value) / (max_value - min_value)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
