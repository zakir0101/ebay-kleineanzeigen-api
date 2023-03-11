# importing datetime from datetime module
import sys
from datetime import datetime
import time
# input timestamp
timestamp_string = 1678575724739/1000
current_time = time.time()
# Converting timestamp string to datetime object and formatting it
datetime_object = datetime.fromtimestamp(timestamp_string).strftime('%d-%m-%y-%H:%M')

# printing resultant datetime object
print("Resultant datetime object:",datetime_object)

# printing the type of resultant datetime object
print("Type of datetime object:", type(datetime_object))

msg_body = dict(message="hallo",
                adId="2382158583",
                adType="private",
                contactName="Zakir")

string1 = "message=hallo&adId=2382158583&adType=private&contactName=Zakir"
print("content lenght ",sys.getsizeof(string1).__str__() )