from datetime import datetime

def format_date(date_str):
    """Format date string for display and API calls"""
    if isinstance(date_str, datetime):
        return date_str.strftime("%B %d, %Y")
    elif isinstance(date_str, str):
        try:
            # Try to parse the date string in ISO format (YYYY-MM-DD)
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except ValueError:
            # If parsing fails, return the original string
            pass
    return date_str
