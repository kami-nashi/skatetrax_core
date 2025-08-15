from datetime import date, timedelta

def current_month():
    today = date.today()
    start = today.replace(day=1)
    end = today
    return {"start": start, "end": end}

def last_month():
    today = date.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return {"start": last_month_start, "end": last_month_end}

def last_3_months():
    today = date.today()
    end = today
    start_month = today.month - 3
    start_year = today.year
    if start_month <= 0:
        start_month += 12
        start_year -= 1
    start = date(start_year, start_month, 1)
    return {"start": start, "end": end}

def last_12_months():
    today = date.today()
    start = today.replace(year=today.year - 1, month=1, day=1)
    end = today
    return {"start": start, "end": end}

def previous_30_days():
    today = date.today()
    start = today - timedelta(days=30)
    end = today
    return {"start": start, "end": end}

def previous_60_days():
    today = date.today()
    start = today - timedelta(days=60)
    end = today
    return {"start": start, "end": end}

def year_to_date():
    today = date.today()
    start = today.replace(month=1, day=1)
    end = today
    return {"start": start, "end": end}

def total():  # Lifetime total of all values
    return None  # signals no date filtering

# Dictionary of all standard timeframes
TIMEFRAMES = {
    "total": total,
    "current_month": current_month,
    "last_month": last_month,
    "90d": last_3_months,
    "12m": last_12_months,
    "30d": previous_30_days,
    "60d": previous_60_days,
    "ytd": year_to_date
}