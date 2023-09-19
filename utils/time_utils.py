def convert_time_format(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            raise ValueError("Invalid time format")

        hours, minutes, seconds = map(int, parts)

        if hours == 0 and minutes == 0:
            return f"{seconds}s"
        elif hours == 0:
            return f"{minutes}min{seconds}s"
        else:
            return f"{hours}h{minutes}min{seconds}s"
    except ValueError as e:
        return str(e)