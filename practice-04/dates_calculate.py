from datetime import datetime, timedelta

# 1️ Subtract five days from current date
current_date = datetime.now()
five_days_ago = current_date - timedelta(days=5)
print("Current date:", current_date)
print("Date 5 days ago:", five_days_ago)

# 2️ Print yesterday, today, tomorrow
today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print("\nYesterday:", yesterday.strftime("%Y-%m-%d"))
print("Today:", today.strftime("%Y-%m-%d"))
print("Tomorrow:", tomorrow.strftime("%Y-%m-%d"))

# 3️ Drop microseconds from datetime
now_with_micro = datetime.now()
now_no_micro = now_with_micro.replace(microsecond=0)
print("\nNow with microseconds:", now_with_micro)
print("Now without microseconds:", now_no_micro)

# 4️ Calculate two date difference in seconds
date1 = datetime(2026, 2, 20, 12, 0, 0)
date2 = datetime(2026, 2, 24, 14, 30, 0)
difference = date2 - date1
seconds_diff = difference.total_seconds()
print("\nDifference between {} and {} in seconds: {}".format(date2, date1, seconds_diff))
