import calendar
def print_leap_year_feb_calendars():
    start_year = 1925
    end_year = 2025
    
    for year in range(start_year, end_year + 1):
        if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
            print(f"\nFebruary Calendar for Leap Year {year}:")
            cal = calendar.month(year, 2)
            print(cal)

print_leap_year_feb_calendars()