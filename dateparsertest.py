import parsedatetime
import datetime

cal = parsedatetime.Calendar()

while True:
    user_input = input("Please enter your preferred appointment date (e.g. 'tomorrow', 'next Monday'): ")
    
    time_struct, parse_status = cal.parse(user_input)
    
    if parse_status == 1:
        appointment_date = datetime.datetime(*time_struct[:6])
        formatted_date = appointment_date.strftime("%Y-%m-%d")
        print("Your appointment is set for:", formatted_date)
        break
    else:
        print("Invalid input. Please try again using natural language like 'next Monday', 'tomorrow', or 'in 2 days'.")
