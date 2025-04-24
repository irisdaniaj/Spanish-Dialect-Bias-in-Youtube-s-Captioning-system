def calculate_total_hours(time_list):
    """
    Given a list of (minutes, seconds), calculate the total time in hours.
    
    Args:
        time_list (list of tuples): Each tuple contains (minutes, seconds).
    
    Returns:
        float: Total time in hours.
    """
    total_seconds = 0

    # Convert all time entries to seconds and sum them
    for minutes, seconds in time_list:
        total_seconds += minutes * 60 + seconds

    # Convert total seconds to hours
    total_hours = total_seconds / 3600

    return total_hours

# Example usage
time_entries = [(28, 40), (28, 42), (28, 48), (28, 50),(28, 48), (28, 45), (28, 52), (28, 45), (28, 50), (29, 56), (30, 4), (28, 38), (28, 39) ]  # (minutes, seconds)
total_hours = calculate_total_hours(time_entries)

print(f"Total time in hours: {total_hours:.2f}")
