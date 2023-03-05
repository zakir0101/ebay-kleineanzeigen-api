# importing datetime from datetime module
from datetime import datetime
import time
# input timestamp
timestamp_string = 1709582369
current_time = time.time()
# Converting timestamp string to datetime object and formatting it
datetime_object = datetime.fromtimestamp(timestamp_string).strftime('%d-%m-%y-%H:%M')

# printing resultant datetime object
print("Resultant datetime object:",datetime_object)

# printing the type of resultant datetime object
print("Type of datetime object:", type(datetime_object))